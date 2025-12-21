import sys

from mcp_server_qdrant.mcp_server import QdrantMCPServer
from mcp_server_qdrant.enhanced_settings import (
    EnhancedEmbeddingProviderSettings,
    EnhancedQdrantSettings,
)
from mcp_server_qdrant.settings import ToolSettings

# print("[DEBUG] server.py: Initializing settings", file=sys.stderr)

try:
    tool_settings = ToolSettings()
    #     print(f"[DEBUG] server.py: ToolSettings initialized", file=sys.stderr)
    
    qdrant_settings = EnhancedQdrantSettings()
    #     print(f"[DEBUG] server.py: EnhancedQdrantSettings initialized:", file=sys.stderr)
    #     print(f"[DEBUG] server.py:   location={qdrant_settings.location}", file=sys.stderr)
    #     print(f"[DEBUG] server.py:   collection_name={qdrant_settings.collection_name}", file=sys.stderr)
    #     print(f"[DEBUG] server.py:   local_path={qdrant_settings.local_path}", file=sys.stderr)
    #     print(f"[DEBUG] server.py:   read_only={qdrant_settings.read_only}", file=sys.stderr)
    
    embedding_settings = EnhancedEmbeddingProviderSettings()
    #     print(f"[DEBUG] server.py: EnhancedEmbeddingProviderSettings initialized:", file=sys.stderr)
    #     print(f"[DEBUG] server.py:   provider_type={embedding_settings.provider_type}", file=sys.stderr)
    #     print(f"[DEBUG] server.py:   model_name={embedding_settings.model_name}", file=sys.stderr)
    
    #     print("[DEBUG] server.py: Creating QdrantMCPServer instance", file=sys.stderr)
    mcp = QdrantMCPServer(
        tool_settings=tool_settings,
        qdrant_settings=qdrant_settings,
        embedding_provider_settings=embedding_settings,
    )
    #     print("[DEBUG] server.py: QdrantMCPServer instance created successfully", file=sys.stderr)
except Exception:
    #     print(f"[ERROR] server.py: Failed to initialize server: {type(e).__name__}: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise
