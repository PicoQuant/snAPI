# snAPI RAG — AI-Assisted Scripting

The snAPI RAG module lets any AI tool query the snAPI documentation, API reference,
and demos to help you write measurement scripts.

## Install

```bash
pip install snAPI[rag]
```

## Quick Start

### Option 1: MCP Server (Claude Code, Cursor, Copilot, ...)

If you opened this repository in Claude Code or Cursor, the server is already
configured via `.mcp.json`. Start it with:

```bash
python -m snAPI.rag serve
```

For other AI tools, run the auto-installer:

```bash
python -m snAPI.rag install
```

Then restart your AI tool.

### Option 2: Python API (custom pipelines)

```python
from snAPI.rag import SnAPIRag

rag = SnAPIRag()
context = rag.query_as_context("how do I measure g(2) with two detectors?")
# Inject `context` into your LLM prompt
```

## Build / Download the Index

The index is pre-built for each snAPI release. Download it with:

```bash
python -m snAPI.rag index --download
```

Or build locally (~2-5 minutes):

```bash
python -m snAPI.rag index
```

## Embedding Model

The default model (`BAAI/bge-small-en-v1.5`) runs locally, no API key required.
To use a different model:

```bash
export SNAPI_RAG_EMBEDDING="openai:text-embedding-3-small"
export SNAPI_RAG_EMBEDDING="ollama:nomic-embed-text"
```
