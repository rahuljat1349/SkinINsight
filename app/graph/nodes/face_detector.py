"""Face Detector Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
import numpy as np

from app.graph.state import AnalysisState
from app.models.face_detector import FaceDetector
from app.core.config import settings


class FaceDetectorNode:
    """
    Node that detects faces using InsightFace.
    
    Model: InsightFace (buffalo_l)
    
    Responsibilities:
    - Detect face
    - Extract landmarks
    - Extract bounding box
    - Extract confidence score
    
    Outputs:
    - face_metadata: Dictionary containing bbox, landmarks, confidence
    """
    
    def __init__(self):
        self.name = "face_detector"
        self._face_detector = None
    
    @property
    def face_detector(self):
        if self._face_detector is None:
            self._face_detector = FaceDetector()
        return self._face_detector
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Detect face in the image"""
        image = state.get("image")
        
        if image is None:
            new_state = state.copy()
            new_state["current_error"] = "No image available for face detection"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No image available for face detection"]
            return new_state
        
        try:
            # Perform face detection
            detection_result = self.face_detector.detect_faces(image)
            
            # Extract face metadata
            face_metadata = {
                "num_faces": detection_result.faces_detected,
                "bounding_boxes": detection_result.bounding_boxes,
                "is_valid": detection_result.is_valid
            }
            
            # Update state
            new_state = state.copy()
            new_state["face_metadata"] = face_metadata
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Face detection failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
