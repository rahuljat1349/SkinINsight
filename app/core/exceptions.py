"""Custom Exceptions"""

from fastapi import HTTPException, status

from app.schemas.errors import ErrorCode


class SkinAnalysisException(HTTPException):
    """Base exception for skin analysis errors"""
    
    def __init__(self, error_code: ErrorCode, message: str, user_message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.error_code = error_code
        self.message = message
        self.user_message = user_message
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code.value,
                    "message": message,
                    "user_message": user_message
                },
                "success": False
            }
        )


class NoFaceDetectedError(SkinAnalysisException):
    """Raised when no face is detected in the image"""
    
    def __init__(self):
        super().__init__(
            error_code=ErrorCode.NO_FACE_DETECTED,
            message="No face detected in the uploaded image",
            user_message="We couldn't detect a face in your photo. Please upload a clear image with a visible face."
        )


class MultipleFacesError(SkinAnalysisException):
    """Raised when multiple faces are detected"""
    
    def __init__(self, count: int):
        super().__init__(
            error_code=ErrorCode.MULTIPLE_FACES,
            message=f"Multiple faces detected: {count}",
            user_message="We detected multiple faces. Please upload a photo with only one person."
        )


class FaceTooSmallError(SkinAnalysisException):
    """Raised when the detected face is too small"""
    
    def __init__(self, width: int, height: int, min_size: int):
        super().__init__(
            error_code=ErrorCode.FACE_TOO_SMALL,
            message=f"Face too small: {width}x{height}, minimum is {min_size}x{min_size}",
            user_message="The face in your photo is too small. Please upload a closer image."
        )


class PoorLightingError(SkinAnalysisException):
    """Raised when lighting is inadequate"""
    
    def __init__(self):
        super().__init__(
            error_code=ErrorCode.POOR_LIGHTING,
            message="Poor lighting detected",
            user_message="The lighting in your photo is too dark or uneven. Please take a photo in well-lit conditions."
        )


class ExcessiveBlurError(SkinAnalysisException):
    """Raised when the image is too blurry"""
    
    def __init__(self):
        super().__init__(
            error_code=ErrorCode.EXCESSIVE_BLUR,
            message="Excessive blur detected",
            user_message="Your photo is too blurry. Please upload a clearer image."
        )


class UnsupportedFormatError(SkinAnalysisException):
    """Raised when the image format is not supported"""
    
    def __init__(self, format: str, supported: set[str]):
        super().__init__(
            error_code=ErrorCode.UNSUPPORTED_FORMAT,
            message=f"Unsupported image format: {format}",
            user_message=f"We only support {', '.join(sorted(supported))} files. Please upload a photo in one of these formats."
        )


class ImageTooLargeError(SkinAnalysisException):
    """Raised when the image exceeds the size limit"""
    
    def __init__(self, size: int, max_size: int):
        super().__init__(
            error_code=ErrorCode.IMAGE_TOO_LARGE,
            message=f"Image size {size} exceeds maximum {max_size}",
            user_message=f"Your photo is too large (over {max_size // (1024*1024)} MB). Please upload a smaller image."
        )


class LowResolutionError(SkinAnalysisException):
    """Raised when the image resolution is too low"""
    
    def __init__(self, width: int, height: int, min_width: int, min_height: int):
        super().__init__(
            error_code=ErrorCode.LOW_RESOLUTION,
            message=f"Image resolution {width}x{height} is below minimum {min_width}x{min_height}",
            user_message=f"Your photo is too small. Please upload an image at least {min_width}x{min_height} pixels."
        )


class InternalInferenceError(SkinAnalysisException):
    """Raised when there's an internal error during inference"""
    
    def __init__(self, original_error: str):
        super().__init__(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=f"Internal inference error: {original_error}",
            user_message="We encountered an error processing your photo. Please try again later.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
