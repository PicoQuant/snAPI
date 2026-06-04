import pytest
from pathlib import Path
from snAPI.rag.config import RagConfig
from snAPI.rag.indexer import build_index
from snAPI.rag.retriever import SnAPIRag


@pytest.fixture(scope="module")
def rag(tmp_path_factory):
    index_dir = tmp_path_factory.mktemp("index")
    cfg = RagConfig()
    build_index(cfg, index_dir=index_dir)
    return SnAPIRag(index_dir=index_dir)


def test_query_returns_results(rag):
    results = rag.query("how do I start a histogram measurement?")
    assert len(results) > 0


def test_query_as_context_is_string(rag):
    ctx = rag.query_as_context("coincidence windowTime")
    assert isinstance(ctx, str)
    assert "coincidence" in ctx.lower()


def test_lookup_finds_method(rag):
    ctx = rag.query_as_context("Manipulators.coincidence")
    assert "coincidence" in ctx.lower()
    assert "windowTime" in ctx


def test_module_level_query_raises_on_missing_index():
    from snAPI.rag import query
    with pytest.raises(FileNotFoundError):
        query("test", index_dir=Path("/nonexistent/path"))
