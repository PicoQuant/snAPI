from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from snAPI.rag.config import RagConfig
from snAPI.rag.retriever import SnAPIRag


def create_mcp_app(rag: SnAPIRag) -> Server:
    app = Server("snapi-rag")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="snapi_query",
                description=(
                    "Search the snAPI documentation, API reference, and demos "
                    "using a natural language question. Returns relevant context "
                    "for writing snAPI measurement scripts."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Natural language question about snAPI",
                        }
                    },
                    "required": ["question"],
                },
            ),
            types.Tool(
                name="snapi_lookup",
                description=(
                    "Look up a specific snAPI class or method by name. "
                    "Examples: 'snAPI.initDevice', 'Manipulators.coincidence', 'MeasMode'"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Class or method name, e.g. 'Manipulators.coincidence'",
                        }
                    },
                    "required": ["symbol"],
                },
            ),
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name == "snapi_query":
            result = rag.query_as_context(arguments["question"])
        elif name == "snapi_lookup":
            result = rag.query_as_context(arguments["symbol"], top_k=3)
        else:
            raise ValueError(f"Unknown tool: {name}")
        return [types.TextContent(type="text", text=result)]

    return app


def run_server(cfg: RagConfig):
    rag = SnAPIRag(config=cfg)
    app = create_mcp_app(rag)

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )

    asyncio.run(_run())
