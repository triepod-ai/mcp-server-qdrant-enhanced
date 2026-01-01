"""
Enhanced HTTP/SSE entry point for the mcp-server-qdrant with multi-model support.
This variant uses streamable HTTP (SSE) transport instead of stdio.
"""

import sys


def main():
    """
    Enhanced HTTP main entry point for the mcp-server-qdrant.
    Supports collection-specific embedding models with SSE transport.

    Note: FastMCP's native SSE transport runs on port 8000 by default.
    With host networking, this is directly accessible at localhost:8000.
    """
    try:
        # Use enhanced server with multi-model support
        from mcp_server_qdrant.enhanced_server import mcp

        # Use FastMCP's native SSE transport
        # It will bind to 0.0.0.0:8000 by default
        print("Starting MCP SSE server (FastMCP native transport)", file=sys.stderr)
        mcp.run(transport="sse")

    except Exception:
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
