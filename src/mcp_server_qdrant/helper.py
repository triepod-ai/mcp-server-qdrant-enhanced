import importlib.metadata


def get_package_version() -> str:
    """Get the package version using importlib.metadata."""
    try:
        return importlib.metadata.version("mcp-server-qdrant")
    except importlib.metadata.PackageNotFoundError:
        # Fall back to a default version if package is not installed
        return "0.0.0"
