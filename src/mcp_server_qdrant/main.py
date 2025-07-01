import argparse
import sys
import os


def main():
    """
    Main entry point for the mcp-server-qdrant script defined
    in pyproject.toml. It runs the MCP server with a specific transport
    protocol.
    """
    # Debug logging to stderr - disabled for MCP compatibility
    # print(f"[DEBUG] main.py: Starting MCP server", file=sys.stderr)
    # print(f"[DEBUG] main.py: Python version: {sys.version}", file=sys.stderr)
    # print(f"[DEBUG] main.py: Environment variables:", file=sys.stderr)
    # for key, value in os.environ.items():
    #     if key.startswith(('QDRANT', 'EMBEDDING', 'COLLECTION', 'TOOL')):
    #         print(f"[DEBUG] main.py:   {key}={value}", file=sys.stderr)

    # Parse the command-line arguments to determine the transport protocol.
    parser = argparse.ArgumentParser(description="mcp-server-qdrant")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
    )
    args = parser.parse_args()
    # print(f"[DEBUG] main.py: Transport mode: {args.transport}", file=sys.stderr)

    try:
        # Import is done here to make sure environment variables are loaded
        # only after we make the changes.
        # print(f"[DEBUG] main.py: Importing server module", file=sys.stderr)
        from mcp_server_qdrant.server import mcp
        # print(f"[DEBUG] main.py: Server module imported successfully", file=sys.stderr)

        # print(f"[DEBUG] main.py: Starting MCP server with transport={args.transport}", file=sys.stderr)
        mcp.run(transport=args.transport)
    except Exception as e:
        #         print(f"[ERROR] main.py: Exception occurred: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
