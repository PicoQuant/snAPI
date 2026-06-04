import json
import sys
from pathlib import Path

MCP_CONFIG = {
    "mcpServers": {
        "snapi": {
            "command": sys.executable,
            "args": ["-m", "snAPI.rag", "serve"],
            "description": "snAPI documentation and API reference RAG",
        }
    }
}

TOOL_CONFIG_PATHS = {
    "claude_code": Path.home() / ".claude" / "settings.json",
    "cursor": Path.home() / ".cursor" / "mcp.json",
    "vscode": Path.home() / ".vscode" / "mcp.json",
}


def _merge_mcp_config(existing: dict, addition: dict) -> dict:
    result = dict(existing)
    result.setdefault("mcpServers", {})
    result["mcpServers"].update(addition["mcpServers"])
    return result


def install_mcp():
    installed = []
    for tool_name, config_path in TOOL_CONFIG_PATHS.items():
        if not config_path.parent.exists():
            continue
        existing = {}
        if config_path.exists():
            try:
                existing = json.loads(config_path.read_text())
            except json.JSONDecodeError:
                pass
        merged = _merge_mcp_config(existing, MCP_CONFIG)
        config_path.write_text(json.dumps(merged, indent=2))
        installed.append(f"  {tool_name}: {config_path}")

    if installed:
        print("snAPI MCP server registered in:")
        print("\n".join(installed))
        print("\nRestart your AI tool to activate.")
    else:
        print("No supported AI tool config found.")
        print("Add this manually to your tool's MCP config:")
        print(json.dumps(MCP_CONFIG, indent=2))
