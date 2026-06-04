import ast
import re
from pathlib import Path

from llama_index.core import Document


def chunk_main_py(path: Path) -> list[Document]:
    """One Document per method, including class context, signature, docstring, body."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines()
    docs = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        class_name = node.name
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name.startswith("_") and item.name != "__init__":
                continue
            start = item.lineno - 1
            end = item.end_lineno
            method_source = "\n".join(lines[start:end])
            docs.append(Document(
                text=f"# {class_name}.{item.name}\n\n{method_source}",
                metadata={
                    "source_type": "api",
                    "class": class_name,
                    "method": item.name,
                    "source_file": str(path),
                },
            ))
    return docs


def chunk_constants_py(path: Path) -> list[Document]:
    """One Document per Enum class."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines()
    docs = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = [getattr(b, "id", "") for b in node.bases]
        if "Enum" not in bases:
            continue
        start = node.lineno - 1
        end = node.end_lineno
        enum_source = "\n".join(lines[start:end])
        docs.append(Document(
            text=f"# Enum: {node.name}\n\n{enum_source}",
            metadata={
                "source_type": "constants",
                "enum_class": node.name,
                "source_file": str(path),
            },
        ))
    return docs


def chunk_demos(demos_dir: Path) -> list[Document]:
    """One Document per demo file, with auto-generated description."""
    docs = []
    for demo_file in sorted(demos_dir.glob("Demo_*.py")):
        source = demo_file.read_text(encoding="utf-8")
        classes_used = sorted(set(re.findall(r'sn\.(\w+)', source)))
        first_comment = ""
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and stripped != "#":
                first_comment = stripped.lstrip("# ")
                break

        description = (
            f"Demo: {demo_file.stem}\n"
            f"snAPI features used: {', '.join(classes_used) or 'general'}\n"
            f"{first_comment}\n\n"
        )
        docs.append(Document(
            text=description + source,
            metadata={
                "source_type": "demo",
                "filename": demo_file.name,
                "source_file": str(demo_file),
                "snapi_classes": classes_used,
            },
        ))
    return docs


def chunk_rst(doc_source_dir: Path) -> list[Document]:
    """One Document per RST section."""
    docs = []
    for rst_file in sorted(doc_source_dir.glob("*.rst")):
        text = rst_file.read_text(encoding="utf-8")
        sections = re.split(r'\n[=\-~^]+\n', text)
        for i, section in enumerate(sections):
            section = section.strip()
            if len(section) < 50:
                continue
            docs.append(Document(
                text=section,
                metadata={
                    "source_type": "docs",
                    "source_file": rst_file.name,
                    "section_index": i,
                },
            ))
    return docs


def _extract_image_captions(doc_source_dir: Path) -> dict[str, str]:
    captions: dict[str, str] = {}
    for rst_file in doc_source_dir.glob("*.rst"):
        text = rst_file.read_text(encoding="utf-8")
        for match in re.finditer(
            r'\.\. image:: (?:_images/)?(\S+)\s*\n((?:[ \t]+.*\n)*)', text
        ):
            filename = Path(match.group(1)).name
            context_lines = match.group(2).strip()
            start = max(0, match.start() - 200)
            surrounding = text[start:match.start()].strip()[-150:]
            captions[filename] = f"{surrounding}\n{context_lines}".strip()
    return captions


def chunk_images(images_dir: Path, doc_source_dir: Path) -> list[Document]:
    """One Document per image, with RST caption as text."""
    captions = _extract_image_captions(doc_source_dir)
    docs = []
    for img_path in sorted(images_dir.iterdir()):
        if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif"}:
            continue
        caption = captions.get(img_path.name, f"Image: {img_path.stem}")
        docs.append(Document(
            text=f"Image: {img_path.name}\n\n{caption}",
            metadata={
                "source_type": "image",
                "filename": img_path.name,
                "source_file": str(img_path),
            },
        ))
    return docs
