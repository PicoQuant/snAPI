import ast
from pathlib import Path
from snAPI.rag.chunker import chunk_main_py, chunk_constants_py, chunk_demos, chunk_rst

FIXTURES = Path(__file__).parent / "fixtures"


def test_chunk_main_py_never_splits_methods():
    from snAPI.rag.config import RagConfig
    cfg = RagConfig()
    docs = chunk_main_py(cfg.main_py)
    for doc in docs:
        assert "def " in doc.text, f"Chunk missing def: {doc.metadata}"
        assert not doc.text.rstrip().endswith(",")


def test_chunk_main_py_metadata():
    from snAPI.rag.config import RagConfig
    cfg = RagConfig()
    docs = chunk_main_py(cfg.main_py)
    for doc in docs:
        assert doc.metadata["source_type"] == "api"
        assert "class" in doc.metadata
        assert "method" in doc.metadata


def test_chunk_constants_py_one_per_enum():
    from snAPI.rag.config import RagConfig
    cfg = RagConfig()
    docs = chunk_constants_py(cfg.constants_py)
    names = [d.metadata["enum_class"] for d in docs]
    assert "MeasMode" in names
    assert "CoincidenceMode" in names
    assert len(names) == len(set(names))


def test_chunk_demos_one_per_file():
    from snAPI.rag.config import RagConfig
    cfg = RagConfig()
    docs = chunk_demos(cfg.demos_dir)
    filenames = [d.metadata["filename"] for d in docs]
    assert "Demo_HistogramSimple.py" in filenames
    assert "Demo_CorrelationG2.py" in filenames
    assert len(filenames) == len(set(filenames))


def test_chunk_rst_preserves_sections():
    from snAPI.rag.config import RagConfig
    cfg = RagConfig()
    docs = chunk_rst(cfg.doc_source_dir)
    sources = [d.metadata["source_file"] for d in docs]
    assert any("introduction" in s for s in sources)
