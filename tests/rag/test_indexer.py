from pathlib import Path
import pytest
from snAPI.rag.config import RagConfig
from snAPI.rag.indexer import build_index, load_index


def test_build_index_creates_directory(tmp_path):
    cfg = RagConfig()
    index_dir = tmp_path / "index"
    build_index(cfg, index_dir=index_dir)
    assert index_dir.exists()
    assert any(index_dir.iterdir())


def test_load_index_after_build(tmp_path):
    cfg = RagConfig()
    index_dir = tmp_path / "index"
    build_index(cfg, index_dir=index_dir)
    index = load_index(cfg, index_dir=index_dir)
    assert index is not None


def test_build_index_reports_chunk_count(tmp_path, capsys):
    cfg = RagConfig()
    index_dir = tmp_path / "index"
    build_index(cfg, index_dir=index_dir, verbose=True)
    out = capsys.readouterr().out
    assert "chunks" in out.lower()


def test_load_index_raises_if_missing(tmp_path):
    cfg = RagConfig()
    with pytest.raises(FileNotFoundError):
        load_index(cfg, index_dir=tmp_path / "nonexistent")
