#!/usr/bin/env python3
"""
Write test files to large vector collection using MCP tools
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server_qdrant.enhanced_qdrant import EnhancedQdrantConnector
from mcp_server_qdrant.enhanced_settings import EnhancedQdrantSettings, EnhancedEmbeddingProviderSettings

async def write_test_documents():
    """Write test documents to the largest collection using MCP tools"""

    # Initialize connector
    settings = EnhancedQdrantSettings()
    embedding_settings = EnhancedEmbeddingProviderSettings()
    connector = EnhancedQdrantConnector(settings, embedding_settings)

    # Target collection (large vectors for GPU stress testing)
    target_collection = "lodestar_legal_analysis"

    # Legal analysis test documents for GPU stress testing
    test_documents = [
        {
            "content": "Legal Contract Analysis: GPU-Accelerated Document Processing. This comprehensive analysis examines the implementation of CUDA-accelerated embedding generation for large-scale legal document review. The enhanced MCP server utilizes cuDNN 9.13.0 libraries to process complex legal terminology, contract clauses, and regulatory compliance requirements with improved computational efficiency. Legal practitioners benefit from faster semantic search capabilities across extensive document repositories, enabling rapid identification of relevant precedents, contractual obligations, and compliance violations. The system's multi-vector support accommodates various document types from simple contracts to complex regulatory frameworks.",
            "metadata": {"test_type": "gpu_legal_analysis", "domain": "contract_analysis", "complexity": "high", "gpu_accelerated": True}
        },
        {
            "content": "Regulatory Compliance Framework Analysis: Enhanced Vector Processing for Legal Technology Applications. This detailed examination focuses on the application of advanced embedding models in regulatory compliance assessment. The enhanced Qdrant MCP server employs sophisticated vector processing techniques to analyze regulatory requirements across multiple jurisdictions. Legal professionals utilize this system to ensure compliance with evolving regulatory landscapes, including data privacy regulations, financial compliance standards, and industry-specific requirements. The GPU acceleration enables real-time analysis of regulatory changes and their impact on existing legal frameworks.",
            "metadata": {"test_type": "regulatory_analysis", "jurisdiction": "multi_national", "vectors": "1024D", "processing_type": "real_time"}
        },
        {
            "content": "Case Law Research and Precedent Analysis: Large-Scale Legal Vector Database Operations. This comprehensive study investigates the deployment of enhanced vector search capabilities for legal precedent identification and case law research. The system processes extensive legal databases containing judicial opinions, case summaries, and legal arguments to provide contextually relevant precedents. Legal researchers and attorneys leverage this technology to identify supporting case law, analyze judicial reasoning patterns, and predict potential legal outcomes. The multi-dimensional vector approach captures nuanced legal concepts and argumentation structures.",
            "metadata": {"test_type": "case_law_analysis", "database_size": "extensive", "legal_domain": "precedent_research", "vector_dimensions": "768D"}
        },
        {
            "content": "Intellectual Property Analysis: Advanced Semantic Processing for Patent and Trademark Research. This specialized analysis explores the application of enhanced vector processing in intellectual property research and analysis. The system processes patent applications, trademark filings, and intellectual property documentation to identify potential conflicts, prior art, and infringement risks. Legal practitioners in intellectual property law utilize the GPU-accelerated processing to perform comprehensive freedom-to-operate analyses, patent landscape assessments, and competitive intelligence research. The enhanced embedding models capture technical specifications, legal claims, and commercial applications.",
            "metadata": {"test_type": "ip_analysis", "patent_processing": True, "trademark_analysis": True, "gpu_intensive": True}
        },
        {
            "content": "Litigation Support and Discovery Analysis: High-Performance Document Review Systems for Legal Proceedings. This extensive analysis examines the deployment of enhanced MCP server capabilities in litigation support and electronic discovery processes. The system processes large volumes of legal documents, correspondence, and evidence materials to identify relevant information for legal proceedings. Legal teams benefit from accelerated document review workflows, privilege review processes, and responsive document identification. The GPU acceleration significantly reduces processing time for large-scale discovery operations while maintaining accuracy in legal document classification and relevance determination.",
            "metadata": {"test_type": "litigation_support", "ediscovery": True, "document_volume": "high", "processing_speed": "accelerated"}
        }
    ]

    print(f"Writing {len(test_documents)} test documents to collection '{target_collection}'")
    print("=" * 60)

    successful_writes = 0
    failed_writes = 0

    for i, doc in enumerate(test_documents, 1):
        try:
            print(f"Writing document {i}/{len(test_documents)}...")

            # Use connector store function
            from mcp_server_qdrant.enhanced_qdrant import Entry
            entry = Entry(content=doc["content"], metadata=doc["metadata"])

            start_time = time.time()
            await connector.store(entry, collection_name=target_collection)
            end_time = time.time()

            print(f"  ✅ Success in {end_time - start_time:.3f}s")
            print(f"  📝 Content: {doc['content'][:60]}...")
            print(f"  🏷️  Metadata: {doc['metadata']['test_type']}")
            successful_writes += 1

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            failed_writes += 1

        print()

    # Summary
    print("=" * 60)
    print("Test Write Summary:")
    print(f"  Target Collection: {target_collection}")
    print(f"  Successful Writes: {successful_writes}")
    print(f"  Failed Writes: {failed_writes}")
    print(f"  Success Rate: {(successful_writes / len(test_documents) * 100):.1f}%")

    # Test a search to verify the documents were written
    if successful_writes > 0:
        print("\nTesting search functionality...")
        try:
            search_results = await connector.search(
                query="CUDA acceleration test",
                collection_name=target_collection,
                limit=3
            )

            print(f"  🔍 Found {len(search_results)} results for 'CUDA acceleration test'")
            for result in search_results:
                print(f"    - Score: {result.get('score', 'N/A'):.3f}")
                print(f"      Content: {result.get('content', 'N/A')[:50]}...")

        except Exception as e:
            print(f"  ❌ Search test failed: {e}")

if __name__ == "__main__":
    asyncio.run(write_test_documents())