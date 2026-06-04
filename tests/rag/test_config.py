import os
from pathlib import Path
from snAPI.rag.config import RagConfig


def test_default_config_paths():
    cfg = RagConfig()
    assert cfg.repo_root.is_dir()
    assert (cfg.repo_root / "snAPI" / "Main.py").exists()


def test_index_dir_resolves():
    cfg = RagConfig()
    assert cfg.index_dir == cfg.repo_root / "snAPI" / "rag" / "index"


def test_embedding_model_default():
    cfg = RagConfig()
    assert cfg.embedding_model == "local:BAAI/bge-small-en-v1.5"


def test_embedding_model_from_env(monkeypatch):
    monkeypatch.setenv("SNAPI_RAG_EMBEDDING", "openai:text-embedding-3-small")
    cfg = RagConfig()
    assert cfg.embedding_model == "openai:text-embedding-3-small"
