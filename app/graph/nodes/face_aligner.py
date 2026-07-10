"""Face Aligner Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import cv2

from app.graph.state import AnalysisState
from app.models.face_detector import FaceDetector
from app.core.config import settings


class FaceAlignerNode:
    """
    Node that aligns and normalizes the face.
    
    Responsibilities:
    - Normalize rotation
    - Normalize scale
    - Normalize position
    
    Output:
    - aligned_face: Aligned RGB numpy array (standardized size)
    """
    
    def __init__(self):
        self.name = "face_aligner"
        self._face_detector = None
        self.target_size = (256, 256)  # Standard size for aligned face
    
    @property
    def face_detector(self):
        if self._face_detector is None:
            self._face_detector = FaceDetector()
        return self._face_detector
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Align and normalize the face"""
        image = state.get("image")
        face_metadata = state.get("face_metadata")
        
        if image is None:
            new_state = state.copy()
            new_state["current_error"] = "No image available for alignment"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No image available for alignment"]
            return new_state
        
        if face_metadata is None:
            new_state = state.copy()
            new_state["current_error"] = "No face metadata available for alignment"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No face metadata available for alignment"]
            return new_state
        
        try:
            # Get bounding box
            bounding_boxes = face_metadata.get("bounding_boxes", [])
            if not bounding_boxes:
                new_state = state.copy()
                new_state["current_error"] = "No bounding box available for alignment"
                new_state["is_error_state"] = True
                new_state["errors"] = state.get("errors", []) + ["No bounding box available"]
                return new_state
            
            bbox = bounding_boxes[0]
            
            # Extract face region with padding (ensure ints for slicing)
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            face_width = x2 - x1
            face_height = y2 - y1
            
            # Add padding (20% on each side)
            padding_x = int(face_width * 0.2)
            padding_y = int(face_height * 0.2)
            
            x1 = max(0, x1 - padding_x)
            y1 = max(0, y1 - padding_y)
            x2 = min(image.shape[1], x2 + padding_x)
            y2 = min(image.shape[0], y2 + padding_y)
            
            # Extract face region
            face_region = image[y1:y2, x1:x2]
            
            # Resize to target size
            aligned_face = cv2.resize(face_region, self.target_size, interpolation=cv2.INTER_AREA)
            
            # Convert back to RGB (cv2 uses BGR by default, but our input is RGB)
            # Since we're working with RGB throughout, no conversion needed
            
            # Update state
            new_state = state.copy()
            new_state["aligned_face"] = aligned_face
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Face alignment failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
