#!/usr/bin/env python3
"""
Direct validation of Qdrant MCP server functionality
"""
import subprocess
import json
import time
from datetime import datetime

def run_cmd(cmd, container="mcp-server-qdrant-enhanced"):
    """Run command in container"""
    full_cmd = f"docker exec {container} bash -c '{cmd}'"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    print("="*60)
    print("🔍 QDRANT MCP SERVER VALIDATION")
    print(f"   Timestamp: {datetime.now()}")
    print("="*60)
    
    # 1. Check container health
    print("\n✅ Step 1: Container Health Check")
    code, stdout, stderr = run_cmd("ps aux | grep enhanced_main | grep -v grep | wc -l")
    if stdout.strip() == "1":
        print("   ✓ MCP server process running")
    else:
        print("   ✗ MCP server not running")
    
    # 2. Check GPU/CUDA
    print("\n🚀 Step 2: GPU Acceleration Check")
    code, stdout, stderr = run_cmd("""python3 -c 'import onnxruntime as ort; print("CUDA Available:", "CUDAExecutionProvider" in ort.get_available_providers())'""")
    print(f"   {stdout.strip()}")
    
    # 3. Test Qdrant connection
    print("\n🔌 Step 3: Qdrant Connection Test")
    code, stdout, stderr = run_cmd("curl -s http://localhost:6333/collections | jq -r '.result.collections | length'")
    if code == 0 and stdout.strip().isdigit():
        print(f"   ✓ Qdrant API responding with {stdout.strip()} collections")
    else:
        print("   ✗ Qdrant API not responding")
    
    # 4. Test store operation
    print("\n💾 Step 4: Store Operation Test")
    test_cmd = """python3 -c '
import asyncio
from src.mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from src.mcp_server_qdrant.models import Entry

async def test():
    connector = EnhancedQdrantConnector()
    entry = Entry(
        content="Test document for validation",
        metadata={"timestamp": "2025-01-23", "type": "validation"}
    )
    result = await connector.store(entry, collection_name="validation_test")
    print("Store successful:", result is not None)

asyncio.run(test())
'"""
    
    code, stdout, stderr = run_cmd(test_cmd)
    if "Store successful: True" in stdout:
        print("   ✓ Store operation working")
    else:
        print(f"   ✗ Store operation failed: {stderr[:100]}")
    
    # 5. Test find operation
    print("\n🔍 Step 5: Find Operation Test")
    test_cmd = """python3 -c '
import asyncio
from src.mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector

async def test():
    connector = EnhancedQdrantConnector()
    results = await connector.find("validation", collection_name="validation_test", limit=5)
    print("Find successful:", len(results), "results")

asyncio.run(test())
'"""
    
    code, stdout, stderr = run_cmd(test_cmd)
    if "Find successful:" in stdout:
        print(f"   ✓ Find operation working: {stdout.strip()}")
    else:
        print(f"   ✗ Find operation failed: {stderr[:100]}")
    
    # 6. Test embedding performance
    print("\n⚡ Step 6: Embedding Performance Test")
    test_cmd = """python3 -c '
import time
from src.mcp_server_qdrant.embeddings.enhanced_fastembed import EnhancedFastEmbedProvider

provider = EnhancedFastEmbedProvider()
text = ["Performance test document"]

start = time.perf_counter()
embedding = provider.embed_texts(text, model_name="all-minilm-l6-v2")
duration = (time.perf_counter() - start) * 1000

print(f"Embedding time: {duration:.2f}ms")
print(f"Device: {provider.device}")
print(f"Shape: {embedding[0].shape}")
'"""
    
    code, stdout, stderr = run_cmd(test_cmd)
    if "Embedding time:" in stdout:
        print(f"   ✓ Embeddings working:")
        for line in stdout.strip().split('\n'):
            print(f"     {line}")
    else:
        print(f"   ✗ Embedding failed: {stderr[:100]}")
    
    # 7. Run pytest tests
    print("\n🧪 Step 7: Running Test Suite")
    code, stdout, stderr = run_cmd("cd /app && python -m pytest tests/ -q")
    if code == 0:
        # Count passed/failed
        passed = stdout.count(" passed")
        failed = stdout.count(" failed") 
        print(f"   ✓ Tests executed: {passed} passed, {failed} failed")
    else:
        print(f"   ✗ Test suite failed to run")
    
    # 8. Test MCP tools
    print("\n🔧 Step 8: MCP Tool Validation")
    test_cmd = """python3 -c '
from src.mcp_server_qdrant.enhanced_mcp_server import EnhancedQdrantMCPServer

server = EnhancedQdrantMCPServer()
tools = ["qdrant_store", "qdrant_find", "qdrant_get_collections", 
         "qdrant_delete_collection", "qdrant_create_collection"]

found = []
for tool in tools:
    if hasattr(server, tool):
        found.append(tool)

print(f"Tools found: {len(found)}/{len(tools)}")
for tool in found:
    print(f"  ✓ {tool}")
'"""
    
    code, stdout, stderr = run_cmd(test_cmd)
    if "Tools found:" in stdout:
        print(f"   {stdout.strip()}")
    else:
        print(f"   ✗ MCP tools check failed")
    
    # Summary
    print("\n" + "="*60)
    print("📋 VALIDATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()