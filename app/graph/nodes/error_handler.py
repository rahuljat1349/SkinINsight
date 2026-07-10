"""Error Handler Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional

from app.graph.state import AnalysisState
from app.core.exceptions import (
    NoFaceDetectedError,
    MultipleFacesError,
    FaceTooSmallError,
    PoorLightingError,
    ExcessiveBlurError,
    UnsupportedFormatError,
    ImageTooLargeError,
    LowResolutionError,
    InternalInferenceError
)


class ErrorHandlerNode:
    """
    Node that handles errors and converts them to user-friendly messages.
    
    Maps internal errors to proper error codes and user messages.
    """
    
    def __init__(self):
        self.name = "error_handler"
        self.error_mapping = {
            "No face detected": {
                "code": "no_face_detected",
                "message": "No face detected in the image",
                "user_message": "No face was detected. Please ensure the image contains a clear view of your face.",
                "suggestion": "Upload an image with a clearly visible face"
            },
            "Multiple faces detected": {
                "code": "multiple_faces_detected",
                "message": "Multiple faces detected",
                "user_message": "Multiple faces were detected. Please upload an image with only one face.",
                "suggestion": "Upload an image with only one face"
            },
            "Face too small": {
                "code": "face_too_small",
                "message": "Face is too small",
                "user_message": "The face in the image is too small for accurate analysis.",
                "suggestion": "Upload a clearer image with a larger, closer view of your face"
            },
            "Poor lighting": {
                "code": "poor_lighting",
                "message": "Poor lighting conditions",
                "user_message": "The image appears to have poor lighting.",
                "suggestion": "Ensure good lighting. Avoid harsh shadows or overexposure."
            },
            "Excessive blur": {
                "code": "excessive_blur",
                "message": "Image is too blurry",
                "user_message": "The image is too blurry for accurate analysis.",
                "suggestion": "Ensure the image is sharp and in focus"
            },
            "Unsupported image format": {
                "code": "unsupported_image_format",
                "message": "Unsupported image format",
                "user_message": "The uploaded image format is not supported.",
                "suggestion": "Use JPG, JPEG, PNG, or WEBP format"
            },
            "Image too large": {
                "code": "image_too_large",
                "message": "Image file is too large",
                "user_message": "The image file is too large.",
                "suggestion": "Upload an image smaller than 10MB"
            },
            "Low resolution": {
                "code": "low_resolution",
                "message": "Image resolution is too low",
                "user_message": "The image resolution is too low for analysis.",
                "suggestion": "Upload a higher resolution image"
            }
        }
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Handle errors and convert to user-friendly format"""
        errors = state.get("errors", [])
        current_error = state.get("current_error")
        is_error_state = state.get("is_error_state", False)
        
        if not is_error_state and not current_error:
            # No error, pass through
            return state
        
        try:
            # Build error response
            error_info = self._get_error_info(current_error or "")
            
            # Update state with formatted error
            new_state = state.copy()
            new_state["error_info"] = error_info
            new_state["error_code"] = error_info.get("code", "unknown_error")
            new_state["user_error_message"] = error_info.get("user_message", "An error occurred")
            new_state["error_suggestion"] = error_info.get("suggestion", "Please try again")
            
            return new_state
            
        except Exception as e:
            error_msg = f"Error handling failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["errors"] = errors + [error_msg]
            return new_state
    
    def _get_error_info(self, error_str: str) -> Dict[str, str]:
        """Get error info from error string"""
        for error_key, error_info in self.error_mapping.items():
            if error_key.lower() in error_str.lower():
                return error_info
        
        # Default error info
        return {
            "code": "unknown_error",
            "message": error_str,
            "user_message": "An unexpected error occurred during analysis.",
            "suggestion": "Please try again with a different image"
        }
