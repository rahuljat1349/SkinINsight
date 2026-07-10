"""Image Validation Schemas"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ImageFormat(str, Enum):
    """Supported image formats"""
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"


class ImageValidationResult(BaseModel):
    """Image validation result"""
    is_valid: bool
    format: Optional[ImageFormat] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class FaceDetectionResult(BaseModel):
    """Face detection validation result"""
    faces_detected: int
    bounding_boxes: list[list[float]] = Field(default_factory=list)
    is_valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
