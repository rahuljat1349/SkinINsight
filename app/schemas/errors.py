"""Error Response Schemas"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Error codes for the API"""
    NO_FACE_DETECTED = "no_face_detected"
    MULTIPLE_FACES = "multiple_faces_detected"
    FACE_TOO_SMALL = "face_too_small"
    POOR_LIGHTING = "poor_lighting"
    EXCESSIVE_BLUR = "excessive_blur"
    UNSUPPORTED_FORMAT = "unsupported_image_format"
    IMAGE_TOO_LARGE = "image_too_large"
    LOW_RESOLUTION = "low_resolution"
    INTERNAL_ERROR = "internal_error"


class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: ErrorCode
    message: str = Field(description="Human-readable error message")
    user_message: str = Field(description="User-friendly explanation")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: ErrorDetail
    success: bool = False
