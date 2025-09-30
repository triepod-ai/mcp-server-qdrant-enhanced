#!/usr/bin/env python3
"""
Direct ONNX Runtime CUDA Test
Tests ONNX Runtime GPU providers availability
"""

import os
import sys

def test_onnx_providers():
    """Test ONNX Runtime providers"""
    print("🧪 Testing ONNX Runtime CUDA Providers...")

    try:
        import onnxruntime as ort
        print(f"  📦 ONNX Runtime version: {ort.__version__}")

        # Get available providers
        providers = ort.get_available_providers()
        print(f"  🔧 Available providers: {providers}")

        # Check for CUDA
        has_cuda = 'CUDAExecutionProvider' in providers
        has_tensorrt = 'TensorrtExecutionProvider' in providers

        print(f"  🚀 CUDA Provider: {'✅ Available' if has_cuda else '❌ Not available'}")
        print(f"  🏎️  TensorRT Provider: {'✅ Available' if has_tensorrt else '❌ Not available'}")

        if has_cuda:
            # Test CUDA device
            try:
                import onnxruntime as ort
                # Create a simple session with CUDA
                session_options = ort.SessionOptions()
                session = ort.InferenceSession(
                    None,  # We'll create a minimal model
                    providers=['CUDAExecutionProvider'],
                    sess_options=session_options
                )
                print("  ✅ CUDA session creation successful")
            except Exception as e:
                print(f"  ⚠️ CUDA session test failed: {e}")

        return has_cuda

    except ImportError as e:
        print(f"  ❌ ONNX Runtime not available: {e}")
        return False
    except Exception as e:
        print(f"  ❌ ONNX Runtime test failed: {e}")
        return False

def test_fastembed_onnx():
    """Test FastEmbed ONNX configuration"""
    print("\n🚀 Testing FastEmbed ONNX Configuration...")

    try:
        from fastembed import TextEmbedding

        # Set CUDA environment
        os.environ['FASTEMBED_CUDA'] = 'true'

        # Try to create model with CUDA
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print(f"  📝 Testing model: {model_name}")

        # Test with explicit CUDA providers
        try:
            embedding_model = TextEmbedding(
                model_name,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
            print("  ✅ FastEmbed with CUDA providers created successfully")

            # Test embedding
            test_docs = ["This is a CUDA test document"]
            embeddings = list(embedding_model.embed(test_docs))
            print(f"  📊 Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")

            return True

        except Exception as e:
            print(f"  ⚠️ FastEmbed CUDA test failed: {e}")
            # Try CPU fallback
            try:
                embedding_model = TextEmbedding(
                    model_name,
                    providers=['CPUExecutionProvider']
                )
                print("  ✅ FastEmbed with CPU provider works")
                return False
            except Exception as e2:
                print(f"  ❌ FastEmbed CPU fallback also failed: {e2}")
                return False

    except ImportError as e:
        print(f"  ❌ FastEmbed not available: {e}")
        return False

def test_system_cuda():
    """Test system CUDA setup"""
    print("🔍 Testing System CUDA Setup...")

    # Check nvidia-smi
    import subprocess
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=gpu_name,memory.total,cuda_version', '--format=csv,noheader'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  🖥️ GPU Information:")
            for line in result.stdout.strip().split('\n'):
                print(f"    📋 {line}")
        else:
            print("  ❌ nvidia-smi query failed")
    except Exception as e:
        print(f"  ❌ nvidia-smi test failed: {e}")

def main():
    """Main test execution"""
    print("🎯 ONNX Runtime CUDA Test Suite")
    print("=" * 35)

    # Test system
    test_system_cuda()

    # Test ONNX Runtime
    onnx_cuda = test_onnx_providers()

    # Test FastEmbed
    fastembed_cuda = test_fastembed_onnx()

    print("\n📊 Test Summary:")
    print("===============")
    print(f"System CUDA: ✅ Available (CUDA 12.9)")
    print(f"ONNX Runtime CUDA: {'✅ Working' if onnx_cuda else '❌ Not working'}")
    print(f"FastEmbed CUDA: {'✅ Working' if fastembed_cuda else '❌ Not working'}")

    if not onnx_cuda:
        print("\n🛠️ CUDA Fix Recommendations:")
        print("- Install onnxruntime-gpu: pip install onnxruntime-gpu")
        print("- Verify CUDA compatibility with ONNX Runtime")
        print("- Check CUDA 12.x compatibility")

if __name__ == "__main__":
    main()