"""
ASGI application module for uvicorn to import.
Exports the FastMCP streamable HTTP app for HTTP transport.

This uses FastMCP's built-in streamable_http_app() method which automatically
handles schema generation, session management, and MCP protocol compliance.
"""

from mcp_server_qdrant.enhanced_server import mcp

# Get the FastAPI app from FastMCP's streamable HTTP implementation
# This ensures proper tool schema generation and MCP protocol compliance
# Note: DNS rebinding protection is disabled for compatibility with IP-based access
app = mcp.streamable_http_app()
