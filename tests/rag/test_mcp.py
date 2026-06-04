from unittest.mock import MagicMock


def test_mcp_server_imports():
    from snAPI.rag.mcp_server import create_mcp_app
    assert callable(create_mcp_app)


def test_mcp_tools_defined():
    from snAPI.rag.mcp_server import create_mcp_app
    mock_rag = MagicMock()
    mock_rag.query_as_context.return_value = "context text"
    app = create_mcp_app(mock_rag)
    assert app is not None
