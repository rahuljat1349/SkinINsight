"""Image Validation Module"""

from io import BytesIO
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.core.exceptions import (
    ExcessiveBlurError,
    ImageTooLargeError,
    LowResolutionError,
    PoorLightingError,
    UnsupportedFormatError,
)
from app.schemas.image import ImageFormat, ImageValidationResult


class ImageValidator:
    """Validates uploaded images for skin analysis"""
    
    def __init__(self):
        self.settings = settings
        
    def validate_image(self, image_bytes: bytes) -> ImageValidationResult:
        """
        Validate an image for skin analysis.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            ImageValidationResult with validation details
            
        Raises:
            Various SkinAnalysisException types for invalid images
        """
        # Check size
        size_bytes = len(image_bytes)
        if size_bytes > self.settings.max_image_size_bytes:
            raise ImageTooLargeError(size_bytes, self.settings.max_image_size_bytes)
        
        # Check format
        image_format = self._detect_format(image_bytes)
        if image_format not in self.settings.supported_image_formats:
            raise UnsupportedFormatError(image_format, self.settings.supported_image_formats)
        
        # Load image
        image = self._load_image(image_bytes)
        
        # Check resolution
        width, height = image.size
        min_width, min_height = self.settings.min_image_resolution
        if width < min_width or height < min_height:
            raise LowResolutionError(width, height, min_width, min_height)
        
        # Convert to numpy for OpenCV operations
        np_image = np.array(image.convert("RGB"))
        
        # Check lighting
        if self._has_poor_lighting(np_image):
            raise PoorLightingError()
        
        # Check blur
        if self._has_excessive_blur(np_image):
            raise ExcessiveBlurError()
        
        return ImageValidationResult(
            is_valid=True,
            format=ImageFormat(image_format),
            width=width,
            height=height,
            size_bytes=size_bytes
        )
    
    def _detect_format(self, image_bytes: bytes) -> str:
        """Detect image format from bytes"""
        # Try PIL first
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                format = img.format
                if format:
                    return format.lower()
        except Exception:
            pass
        
        # Fallback: try to detect from magic bytes
        # Check for common image formats
        if len(image_bytes) >= 8:
            # JPEG: starts with FF D8
            if image_bytes[0] == 0xFF and image_bytes[1] == 0xD8:
                return "jpeg"
            # PNG: starts with 89 50 4E 47 0D 0A 1A 0A
            if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                return "png"
            # WEBP: starts with RIFF....WEBP
            if image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP':
                return "webp"
        
        return "unknown"
    
    def _load_image(self, image_bytes: bytes) -> Image.Image:
        """Load image from bytes"""
        return Image.open(BytesIO(image_bytes))
    
    def _has_poor_lighting(self, image: np.ndarray) -> bool:
        """
        Check if image has poor lighting.
        
        Uses mean brightness and standard deviation to detect under/over exposure.
        A well-lit photo has balanced brightness and good contrast.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        mean_brightness = float(np.mean(gray))
        std_brightness = float(np.std(gray))
        
        # Extremely dark (underexposed) or extremely bright (overexposed)
        if mean_brightness < 30 or mean_brightness > 225:
            return True
        
        # Very low contrast indicates flat, poor lighting
        if std_brightness < 20:
            return True
        
        return False
    
    def _has_excessive_blur(self, image: np.ndarray, threshold: float = 100.0) -> bool:
        """
        Check if image has excessive blur.
        
        Uses Laplacian variance method for blur detection.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Laplacian operator
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Calculate variance
        variance = laplacian.var()
        
        # Low variance indicates blur
        return variance < threshold
    
    def get_image_info(self, image_bytes: bytes) -> Tuple[int, int, str]:
        """Get basic image information without full validation"""
        image = self._load_image(image_bytes)
        width, height = image.size
        format = self._detect_format(image_bytes)
        return width, height, format
