import argparse
import sys
from pathlib import Path

from snAPI.rag.config import RagConfig


def cmd_index(args):
    from snAPI.rag.indexer import build_index
    cfg = RagConfig()
    if args.download:
        _download_index(cfg)
        return
    print("Building snAPI RAG index (this takes ~2-5 minutes on first run)...")
    build_index(cfg, verbose=True)
    print("Done.")


def _download_index(cfg: RagConfig):
    import urllib.request
    import zipfile
    import io
    url = "https://github.com/PicoQuant/snAPI/releases/latest/download/snapi-rag-index.zip"
    print(f"Downloading pre-built index from {url} ...")
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        cfg.index_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(cfg.index_dir)
        print(f"Index downloaded to {cfg.index_dir}")
    except Exception as e:
        print(f"Download failed: {e}\nFalling back to local build...")
        from snAPI.rag.indexer import build_index
        build_index(cfg, verbose=True)


def cmd_serve(args):
    from snAPI.rag.mcp_server import run_server
    cfg = RagConfig()
    if args.port:
        cfg.mcp_port = args.port
    print(f"Starting snAPI MCP server on port {cfg.mcp_port}...")
    run_server(cfg)


def cmd_install(args):
    from snAPI.rag.installer import install_mcp
    install_mcp()


def main():
    parser = argparse.ArgumentParser(prog="python -m snAPI.rag")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Build or download the RAG index")
    p_index.add_argument(
        "--download", action="store_true",
        help="Download pre-built index from GitHub Release"
    )
    p_index.set_defaults(func=cmd_index)

    p_serve = sub.add_parser("serve", help="Start MCP server")
    p_serve.add_argument("--port", type=int, help="Override port (default: 3333)")
    p_serve.set_defaults(func=cmd_serve)

    p_install = sub.add_parser("install", help="Register MCP server in your AI tool")
    p_install.set_defaults(func=cmd_install)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
