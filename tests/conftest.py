"""Shared fixtures for backend tests"""

from typing import Generator
from unittest.mock import patch, MagicMock
from io import BytesIO

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.config import settings


def make_test_image(width: int = 400, height: int = 400, format: str = "jpeg") -> bytes:
    """Create a synthetic test image"""
    img = np.random.randint(100, 200, (height, width, 3), dtype=np.uint8)
    _, buf = cv2.imencode(f".{format}", img,
                          [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return buf.tobytes()


def make_blank_image(width: int = 400, height: int = 400) -> bytes:
    """Create a solid-color image (no face)"""
    img = np.full((height, width, 3), [180, 150, 130], dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return buf.tobytes()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_image_jpeg() -> bytes:
    return make_test_image(400, 400, "jpeg")


@pytest.fixture
def sample_image_png() -> bytes:
    return make_test_image(400, 400, "png")


@pytest.fixture
def blank_image() -> bytes:
    return make_blank_image(400, 400)


@pytest.fixture
def large_image() -> bytes:
    return make_test_image(4000, 4000, "jpeg")


@pytest.fixture(autouse=True)
def override_settings():
    """Force test-friendly settings for all tests"""
    with patch.object(settings, "send_image_to_llm", "false"):
        with patch.object(settings, "fallback_to_local_models", True):
            with patch.object(settings, "llm_enabled", False):
                yield


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    """Reset rate limiter buckets between tests"""
    from app.main import rate_limiter
    rate_limiter._buckets.clear()
    yield


@pytest.fixture
def mock_direct_llm():
    """Mock the DirectLLMNode to return predictable output"""
    mock_output = MagicMock()
    mock_output.overall_score = 75
    mock_output.skin_type = "Combination"
    mock_output.oiliness = 55
    mock_output.hydration = 60
    mock_output.redness = "Low"
    mock_output.pigmentation = "Mild"
    mock_output.wrinkles = "Minimal"
    mock_output.pores = "Medium"
    mock_output.acne.severity = "None"
    mock_output.acne.count = 0
    mock_output.texture = 70
    mock_output.skin_tone = "Light"
    mock_output.explanation = "Test explanation"
    mock_output.summary = "Test summary"
    mock_output.recommendations = []
    mock_output.interactions = []
    mock_output.home_remedies = "Test remedies"
    mock_output.wishing_message = "Test wish"

    with patch("app.graph.nodes.direct_llm_node.DirectLLMNode._call_llm_with_image",
               return_value=mock_output):
        yield
