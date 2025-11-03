#!/bin/bash
# Quick test runner script

echo "=================================="
echo "Image Embeddings Pipeline Tests"
echo "=================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"

case $TEST_TYPE in
    "unit")
        echo "🧪 Running Unit Tests..."
        pytest tests/unit/ -v --tb=short
        ;;
    
    "integration")
        echo "🔗 Running Integration Tests..."
        pytest tests/integration/ -v --tb=short
        ;;
    
    "search")
        echo "🔍 Running Search Tests..."
        pytest tests/test_search.py -v --tb=short
        ;;
    
    "visual")
        echo "🖼️  Running Visual Similarity Tests..."
        pytest tests/test_fashion_image_search.py -v --tb=short
        ;;
    
    "fast")
        echo "⚡ Running Fast Tests Only..."
        pytest tests/ -v -m "not slow" --tb=short
        ;;
    
    "examples")
        echo "📚 Running Example Scripts..."
        echo ""
        echo "1. Processing Sample Images..."
        python tests/examples/process_sample.py
        echo ""
        echo "2. Basic Text Search..."
        python tests/examples/basic_text_search.py
        ;;
    
    "all")
        echo "🎯 Running All Tests..."
        pytest tests/ -v --tb=short
        ;;
    
    *)
        echo "Usage: ./run_tests.sh [unit|integration|search|visual|fast|examples|all]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  search      - Run search functionality tests"
        echo "  visual      - Run visual similarity tests"
        echo "  fast        - Run fast tests (skip slow ones)"
        echo "  examples    - Run example scripts"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "✅ Test run complete!"
echo "=================================="
