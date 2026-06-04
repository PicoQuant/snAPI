from __future__ import annotations

from pathlib import Path
from typing import Optional

from llama_index.core import VectorStoreIndex

from snAPI.rag.config import RagConfig
from snAPI.rag.indexer import load_index


class SnAPIRag:
    def __init__(
        self,
        config: Optional[RagConfig] = None,
        index_dir: Optional[Path] = None,
    ):
        self._cfg = config or RagConfig()
        self._index: VectorStoreIndex = load_index(self._cfg, index_dir=index_dir)
        self._retriever = self._index.as_retriever(similarity_top_k=5)

    def query(self, question: str, top_k: int = 5) -> list[dict]:
        self._retriever.similarity_top_k = top_k
        nodes = self._retriever.retrieve(question)
        return [
            {
                "text": n.text,
                "score": n.score,
                "metadata": n.metadata,
            }
            for n in nodes
        ]

    def query_as_context(self, question: str, top_k: int = 5) -> str:
        results = self.query(question, top_k=top_k)
        parts = []
        for i, r in enumerate(results, 1):
            source = r["metadata"].get("source_file", "unknown")
            parts.append(f"--- Result {i} (source: {source}) ---\n{r['text']}")
        return "\n\n".join(parts)


def query(
    question: str,
    top_k: int = 5,
    config: Optional[RagConfig] = None,
    index_dir: Optional[Path] = None,
) -> str:
    return SnAPIRag(config=config, index_dir=index_dir).query_as_context(
        question, top_k=top_k
    )
