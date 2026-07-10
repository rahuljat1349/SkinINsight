"""Face Validator Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional

from app.graph.state import AnalysisState
from app.core.config import settings
from app.core.exceptions import (
    NoFaceDetectedError,
    MultipleFacesError,
    FaceTooSmallError
)


class FaceValidatorNode:
    """
    Node that validates face detection results.
    
    Checks:
    - One face only
    - Minimum face size
    
    Failure:
    - Returns user-friendly error messages
    """
    
    def __init__(self):
        self.name = "face_validator"
        self.min_face_size = settings.min_face_size_pixels
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Validate face detection results"""
        face_metadata = state.get("face_metadata")
        image = state.get("image")
        
        if face_metadata is None:
            new_state = state.copy()
            new_state["current_error"] = "No face metadata available"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No face metadata available"]
            return new_state
        
        if not face_metadata.get("is_valid", False):
            new_state = state.copy()
            new_state["current_error"] = "Face detection was not valid"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["Face detection was not valid"]
            return new_state
        
        num_faces = face_metadata.get("num_faces", 0)
        bounding_boxes = face_metadata.get("bounding_boxes", [])
        
        # Check for no faces
        if num_faces == 0:
            new_state = state.copy()
            new_state["current_error"] = "No face detected in the image"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No face detected"]
            return new_state
        
        # Check for multiple faces
        if num_faces > 1:
            new_state = state.copy()
            new_state["current_error"] = f"Multiple faces detected ({num_faces}). Please upload an image with only one face."
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [f"Multiple faces detected ({num_faces})"]
            return new_state
        
        # Check face size
        if bounding_boxes:
            bbox = bounding_boxes[0]
            face_width = bbox[2] - bbox[0]
            face_height = bbox[3] - bbox[1]
            
            if face_width < self.min_face_size or face_height < self.min_face_size:
                new_state = state.copy()
                new_state["current_error"] = (
                    f"Face is too small ({face_width}x{face_height} pixels). "
                    f"Minimum required: {self.min_face_size}x{self.min_face_size} pixels. "
                    "Please upload a clearer image with a larger face."
                )
                new_state["is_error_state"] = True
                new_state["errors"] = state.get("errors", []) + [f"Face too small: {face_width}x{face_height}"]
                return new_state
        
        # Validation passed
        new_state = state.copy()
        new_state["errors"] = state.get("errors", [])
        return new_state
