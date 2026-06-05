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
configured via `.mcp.json`. Otherwise, run the auto-installer:

```bash
python -m snAPI.rag install
```

Then restart your AI tool. The installer detects Claude Code, Cursor, and VS Code
automatically.

#### Manual Configuration

If the installer doesn't cover your setup, add this to your tool's MCP config:

```json
{
  "mcpServers": {
    "snapi": {
      "command": "python",
      "args": ["-m", "snAPI.rag", "serve"]
    }
  }
}
```

Config file locations:

| Tool | Config Path |
|------|-------------|
| Claude Code CLI | `~/.claude/settings.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| VS Code (Claude extension) | `.claude.json` in the project root |
| Cursor | `~/.cursor/mcp.json` |
| VS Code (Copilot) | `~/.vscode/mcp.json` |

The MCP server uses **stdio** transport — it does not open a network port.

#### Windows: Cache Path Issue

On Windows, `llama_index` may use a separate cache directory that causes model
loading failures. If you see a `FileNotFoundError` for
`config_sentence_transformers.json`, add an `env` block to the MCP config:

```json
{
  "mcpServers": {
    "snapi": {
      "command": "python",
      "args": ["-m", "snAPI.rag", "serve"],
      "env": {
        "LLAMA_INDEX_CACHE_DIR": "C:\\Users\\<username>\\.cache\\huggingface\\hub"
      }
    }
  }
}
```

### Option 2: Python API (custom pipelines)

```python
from snAPI.rag import SnAPIRag

rag = SnAPIRag()
context = rag.query_as_context("how do I measure g(2) with two detectors?")
# Inject `context` into your LLM prompt
```

Module-level shortcut:

```python
from snAPI.rag import query

context = query("how do I set up a histogram measurement?")
```

## MCP Tools

The MCP server exposes two tools:

* **`snapi_query`** — natural language search over all snAPI sources
* **`snapi_lookup`** — direct lookup by class or method name (e.g. `Manipulators.coincidence`)

## Rebuild the Index

The pre-built index is included in the repository. To rebuild after updating snAPI:

```bash
python -m snAPI.rag index
```

## Embedding Model

The default model (`BAAI/bge-small-en-v1.5`) runs locally, no API key required.
To use a different model:

```bash
# OpenAI
export SNAPI_RAG_EMBEDDING="openai:text-embedding-3-small"

# Ollama (local server)
export SNAPI_RAG_EMBEDDING="ollama:nomic-embed-text"
```

The same model must be used for both building the index and querying.
If you change the model, rebuild the index.
