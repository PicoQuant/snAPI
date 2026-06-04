from __future__ import annotations

from pathlib import Path
from typing import Optional

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore

from snAPI.rag.config import RagConfig
from snAPI.rag.chunker import (
    chunk_main_py, chunk_constants_py, chunk_demos, chunk_rst, chunk_images
)


def _get_embed_model(cfg: RagConfig):
    provider, model_name = cfg.embedding_model.split(":", 1)
    if provider == "local":
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        return HuggingFaceEmbedding(model_name=model_name)
    if provider == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding
        return OpenAIEmbedding(model=model_name)
    if provider == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding
        return OllamaEmbedding(model_name=model_name)
    raise ValueError(
        f"Unknown embedding provider: {provider}. Use local:, openai:, or ollama:"
    )


def build_index(
    cfg: RagConfig,
    index_dir: Optional[Path] = None,
    verbose: bool = False,
) -> VectorStoreIndex:
    index_dir = index_dir or cfg.index_dir
    index_dir.mkdir(parents=True, exist_ok=True)

    Settings.embed_model = _get_embed_model(cfg)
    Settings.llm = None

    docs = []
    docs += chunk_main_py(cfg.main_py)
    docs += chunk_constants_py(cfg.constants_py)
    docs += chunk_demos(cfg.demos_dir)
    docs += chunk_rst(cfg.doc_source_dir)
    if cfg.images_dir.exists():
        docs += chunk_images(cfg.images_dir, cfg.doc_source_dir)

    if verbose:
        print(f"Indexing {len(docs)} chunks from snAPI sources...")

    storage_context = StorageContext.from_defaults(
        docstore=SimpleDocumentStore(),
        vector_store=SimpleVectorStore(),
        index_store=SimpleIndexStore(),
    )
    index = VectorStoreIndex.from_documents(
        docs, storage_context=storage_context, show_progress=verbose
    )
    index.storage_context.persist(persist_dir=str(index_dir))

    if verbose:
        print(f"Index saved to {index_dir}")
    return index


def load_index(cfg: RagConfig, index_dir: Optional[Path] = None) -> VectorStoreIndex:
    index_dir = index_dir or cfg.index_dir
    if not index_dir.exists():
        raise FileNotFoundError(
            f"Index not found at {index_dir}. "
            "Run: python -m snAPI.rag index"
        )
    Settings.embed_model = _get_embed_model(cfg)
    Settings.llm = None
    storage_context = StorageContext.from_defaults(persist_dir=str(index_dir))
    return load_index_from_storage(storage_context)
