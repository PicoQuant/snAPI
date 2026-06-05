AI-Assisted Scripting (RAG)
===========================

snAPI includes a built-in RAG (Retrieval-Augmented Generation) module that allows
any AI tool — Claude, Copilot, Cursor, ChatGPT, or your own pipeline — to query
the snAPI documentation, API reference, and demo scripts to help write measurement code.

The module indexes the full snAPI source: all classes and methods from ``Main.py``,
enums from ``Constants.py``, all demo scripts, and the RST documentation pages.

Installation
------------

Install snAPI with the RAG dependencies::

    pip install snAPI[rag]

The default embedding model (``BAAI/bge-small-en-v1.5``) runs locally.
No API key is required.

Building the Index
------------------

The pre-built index is included in the repository. To rebuild after updating snAPI::

    python -m snAPI.rag index

This takes approximately 2–5 minutes and downloads the embedding model (~130 MB) on first run.
The index is stored in ``snAPI/rag/index/`` and persists across sessions.

Usage
-----

MCP Server (Claude Code, Cursor, Copilot, ...)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you opened this repository in Claude Code or Cursor, the MCP server is already
configured via ``.mcp.json`` in the repository root.

For other AI tools, run the auto-installer::

    python -m snAPI.rag install

Then restart your AI tool. The installer detects Claude Code, Cursor, and VS Code
automatically and writes the configuration to the correct location.

The MCP server uses **stdio** transport — it does not open a network port.
The connected AI tool starts the server process automatically.

Manual Configuration
^^^^^^^^^^^^^^^^^^^^

If the installer doesn't cover your setup, add this to your tool's MCP config:

.. code-block:: json

    {
      "mcpServers": {
        "snapi": {
          "command": "python",
          "args": ["-m", "snAPI.rag", "serve"]
        }
      }
    }

Config file locations:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Tool
     - Config Path
   * - Claude Code CLI
     - ``~/.claude/settings.json``
   * - Claude Desktop (Windows)
     - ``%APPDATA%\Claude\claude_desktop_config.json``
   * - Claude Desktop (macOS)
     - ``~/Library/Application Support/Claude/claude_desktop_config.json``
   * - VS Code (Claude extension)
     - ``.claude.json`` in the project root
   * - Cursor
     - ``~/.cursor/mcp.json``
   * - VS Code (Copilot)
     - ``~/.vscode/mcp.json``

Windows: Cache Path Issue
^^^^^^^^^^^^^^^^^^^^^^^^^

On Windows, ``llama_index`` may use a separate cache directory that causes model
loading failures. If you see a ``FileNotFoundError`` for
``config_sentence_transformers.json``, add an ``env`` block to the MCP config:

.. code-block:: json

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

MCP Tools
^^^^^^^^^

The MCP server exposes two tools to the connected AI:

* ``snapi_query`` — natural language search over all snAPI sources
* ``snapi_lookup`` — direct lookup by class or method name (e.g. ``Manipulators.coincidence``)

Python API (custom pipelines)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For integration into your own AI pipeline::

    from snAPI.rag import SnAPIRag

    rag = SnAPIRag()

    # Natural language query — returns formatted context string
    context = rag.query_as_context("how do I measure g(2) with two detectors?")

    # Direct method lookup
    context = rag.query_as_context("Manipulators.coincidence")

    # Low-level — returns list of result dicts with text, score, metadata
    results = rag.query("coincidence windowTime parameter", top_k=5)

Inject the returned context string into your LLM prompt. The RAG module returns
relevant source excerpts; your LLM generates the final answer.

Module-level shortcut::

    from snAPI.rag import query

    context = query("how do I set up a histogram measurement?")

Embedding Model Configuration
------------------------------

The embedding model is configured via environment variable::

    # Default — local, no API key required
    export SNAPI_RAG_EMBEDDING="local:BAAI/bge-small-en-v1.5"

    # OpenAI
    export SNAPI_RAG_EMBEDDING="openai:text-embedding-3-small"

    # Ollama (local server)
    export SNAPI_RAG_EMBEDDING="ollama:nomic-embed-text"

The same model must be used for both building the index and querying.
If you change the model, rebuild the index with ``python -m snAPI.rag index``.

CLI Reference
-------------

.. code-block:: text

    python -m snAPI.rag <command> [options]

    Commands:
      index     Build the RAG index
      serve     Start the MCP server (stdio transport)
      install   Register the MCP server in your AI tool automatically

What Gets Indexed
-----------------

The RAG index covers all snAPI sources:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Source
     - Coverage
   * - ``snAPI/Main.py``
     - Every public method as a complete chunk (signature + docstring + example)
   * - ``snAPI/Constants.py``
     - Every enum class with all values and descriptions
   * - ``demos/``
     - Every demo script with auto-generated feature summary
   * - ``doc_source/*.rst``
     - All documentation pages, split by section
   * - ``docs/_images/``
     - Hardware diagrams and timing figures with RST captions

.. note::

   Method chunks are never split at token boundaries. Each chunk always contains
   a complete method — signature, parameter descriptions, and example code —
   so retrieved context is always immediately usable.
