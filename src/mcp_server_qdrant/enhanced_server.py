"""
Enhanced server entry point with collection-specific embedding models.
"""
import sys
from mcp_server_qdrant.mcp_server import QdrantMCPServer
from mcp_server_qdrant.enhanced_settings import (
    EnhancedEmbeddingProviderSettings,
    EnhancedQdrantSettings,
)
from mcp_server_qdrant.settings import ToolSettings
from mcp.server.transport_security import TransportSecuritySettings

# print("[DEBUG] enhanced_server.py: Initializing enhanced settings", file=sys.stderr)

try:
    tool_settings = ToolSettings()
    # print(f"[DEBUG] enhanced_server.py: ToolSettings initialized", file=sys.stderr)

    qdrant_settings = EnhancedQdrantSettings()
    # print(f"[DEBUG] enhanced_server.py: EnhancedQdrantSettings initialized:", file=sys.stderr)
    # print(f"[DEBUG] enhanced_server.py:   location={qdrant_settings.location}", file=sys.stderr)
    # print(f"[DEBUG] enhanced_server.py:   auto_create_collections={qdrant_settings.auto_create_collections}", file=sys.stderr)
    # print(f"[DEBUG] enhanced_server.py:   enable_quantization={qdrant_settings.enable_quantization}", file=sys.stderr)

    embedding_settings = EnhancedEmbeddingProviderSettings()
    # print(f"[DEBUG] enhanced_server.py: EnhancedEmbeddingProviderSettings initialized:", file=sys.stderr)
    # print(f"[DEBUG] enhanced_server.py:   provider_type={embedding_settings.provider_type}", file=sys.stderr)
    # print(f"[DEBUG] enhanced_server.py:   model_name={embedding_settings.model_name}", file=sys.stderr)

    # Configure transport security to allow IP-based access
    transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "localhost:10650",
            "127.0.0.1:10650",
            "10.0.0.225:10650",
            "localhost:*",
            "127.0.0.1:*",
            "10.0.0.225:*",
            "[::1]:*",
        ],
        allowed_origins=[
            "http://localhost:*",
            "http://127.0.0.1:*",
            "http://10.0.0.225:*",
            "http://[::1]:*",
        ],
    )

    # print("[DEBUG] enhanced_server.py: Creating EnhancedQdrantMCPServer instance", file=sys.stderr)
    mcp = QdrantMCPServer(
        tool_settings=tool_settings,
        qdrant_settings=qdrant_settings,
        embedding_provider_settings=embedding_settings,
        transport_security=transport_security,
    )
    # print("[DEBUG] enhanced_server.py: EnhancedQdrantMCPServer instance created successfully", file=sys.stderr)

except Exception:
    # print(f"[ERROR] enhanced_server.py: Failed to initialize enhanced server: {type(e).__name__}: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise