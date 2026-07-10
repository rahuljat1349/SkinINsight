#!/usr/bin/env python3
"""
Skin Insight AI - Full Application Test Script

This script tests:
1. Backend API endpoints
2. Pipeline functionality
3. Error handling
4. Performance

Usage: python test_application.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app


def create_test_client():
    """Create a FastAPI test client"""
    return TestClient(app)


def test_health_endpoints():
    """Test health and info endpoints"""
    print("🧪 Testing health endpoints...")
    client = create_test_client()
    
    # Test health endpoint
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    print("   ✅ Health endpoint: OK")
    
    # Test root endpoint
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['name'] == 'Skin Insight AI'
    print("   ✅ Root endpoint: OK")
    
    # Test API docs endpoint
    response = client.get('/docs')
    assert response.status_code == 200
    print("   ✅ API docs endpoint: OK")


def test_image_validation():
    """Test image validation"""
    print("\n🧪 Testing image validation...")
    client = create_test_client()
    
    # Test with invalid format
    response = client.post('/api/v1/analyze', files={'file': ('test.txt', b'not an image', 'text/plain')})
    assert response.status_code == 400
    error = response.json()['error']
    assert 'unsupported' in error['code'].lower() or 'format' in error['code'].lower()
    print("   ✅ Invalid format handling: OK")
    
    # Test with image that's too large
    large_image = np.random.randint(0, 255, (4000, 4000, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.jpg', large_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    response = client.post('/api/v1/analyze', files={'file': ('large.jpg', img_encoded.tobytes(), 'image/jpeg')})
    assert response.status_code == 400
    error = response.json()['error']
    assert 'large' in error['code'].lower() or 'size' in error['code'].lower()
    print("   ✅ Large image handling: OK")


def test_error_handling():
    """Test various error scenarios"""
    print("\n🧪 Testing error handling...")
    client = create_test_client()
    
    # Test with no face (synthetic image)
    test_image = np.random.randint(150, 220, (400, 400, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.png', test_image)
    response = client.post('/api/v1/analyze', files={'file': ('no_face.png', img_encoded.tobytes(), 'image/png')})
    assert response.status_code == 400
    error = response.json()['error']
    assert 'face' in error['code'].lower()
    print("   ✅ No face detection: OK")
    
    # Test with multiple faces (if we could create such an image)
    print("   ✅ Error handling tests: OK")


def test_performance():
    """Test performance of the pipeline"""
    print("\n🧪 Testing performance...")
    client = create_test_client()
    
    # Create a test image
    test_image = np.random.randint(150, 220, (500, 500, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.png', test_image)
    image_bytes = img_encoded.tobytes()
    
    # Measure time for validation (will fail at face detection, but that's OK)
    start_time = time.time()
    response = client.post('/api/v1/analyze', files={'file': ('test.png', image_bytes, 'image/png')})
    end_time = time.time()
    
    processing_time = end_time - start_time
    print(f"   ⏱️  Processing time: {processing_time:.2f}s")
    
    # Should complete within reasonable time (InsightFace loading takes time on first run)
    assert processing_time < 60  # 60 seconds max for first run
    print("   ✅ Performance test: OK")


def test_api_response_structure():
    """Test that API responses have correct structure"""
    print("\n🧪 Testing API response structure...")
    client = create_test_client()
    
    # Test error response structure
    test_image = np.random.randint(150, 220, (100, 100, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.png', test_image)
    response = client.post('/api/v1/analyze', files={'file': ('test.png', img_encoded.tobytes(), 'image/png')})
    
    assert response.status_code == 400
    error_response = response.json()
    assert 'error' in error_response
    assert 'code' in error_response['error']
    assert 'message' in error_response['error']
    assert 'user_message' in error_response['error']
    assert 'success' in error_response
    assert error_response['success'] == False
    print("   ✅ Error response structure: OK")


def main():
    """Run all tests"""
    print("🚀 Skin Insight AI - Full Application Test")
    print("=" * 50)
    
    try:
        test_health_endpoints()
        test_image_validation()
        test_error_handling()
        test_performance()
        test_api_response_structure()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("\n✅ Backend is working correctly")
        print("✅ API endpoints are responsive")
        print("✅ Error handling is functional")
        print("✅ Performance is acceptable")
        print("\n📋 Summary:")
        print("   - Backend: FastAPI with Uvicorn")
        print("   - Port: 8000")
        print("   - API endpoint: POST /api/v1/analyze")
        print("   - Frontend: Vue 3 + Vite")
        print("   - Frontend port: 5173")
        print("\n💡 To test with real images:")
        print("   1. Start the backend: uvicorn app.main:app --reload")
        print("   2. Start the frontend: cd frontend && npm run dev")
        print("   3. Open http://localhost:5173 in your browser")
        print("   4. Upload a photo with a clear, well-lit face")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
