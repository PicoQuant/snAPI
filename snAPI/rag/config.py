import os
from dataclasses import dataclass, field
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).parent.parent.parent


@dataclass
class RagConfig:
    repo_root: Path = field(default_factory=_repo_root)
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "SNAPI_RAG_EMBEDDING", "local:BAAI/bge-small-en-v1.5"
        )
    )
    mcp_port: int = field(
        default_factory=lambda: int(os.getenv("SNAPI_RAG_PORT", "3333"))
    )

    @property
    def index_dir(self) -> Path:
        return self.repo_root / "snAPI" / "rag" / "index"

    @property
    def doc_source_dir(self) -> Path:
        return self.repo_root / "doc_source"

    @property
    def main_py(self) -> Path:
        return self.repo_root / "snAPI" / "Main.py"

    @property
    def constants_py(self) -> Path:
        return self.repo_root / "snAPI" / "Constants.py"

    @property
    def demos_dir(self) -> Path:
        return self.repo_root / "demos"

    @property
    def images_dir(self) -> Path:
        return self.repo_root / "docs" / "_images"
