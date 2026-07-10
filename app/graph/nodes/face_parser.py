"""Face Parser Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
import numpy as np

from app.graph.state import AnalysisState
from app.models.face_parser import FaceParser
from app.models.face_detector import FaceDetector


class FaceParserNode:
    """
    Node that parses the face into regions using Face Parsing model.
    
    Model: Face Parsing (CelebAMask-HQ / BiSeNet)
    
    Produces:
    - skin_mask: Binary mask of skin region
    - regions: Dictionary of region masks (forehead, cheeks, chin, nose)
    
    Removes:
    - hair, lips, eyes, background
    """
    
    def __init__(self):
        self.name = "face_parser"
        self._face_detector = None
        self._face_parser = None
    
    @property
    def face_detector(self):
        if self._face_detector is None:
            self._face_detector = FaceDetector()
        return self._face_detector
    
    @property
    def face_parser(self):
        if self._face_parser is None:
            self._face_parser = FaceParser(self.face_detector)
        return self._face_parser
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Parse face into regions"""
        image = state.get("image")
        
        if image is None:
            new_state = state.copy()
            new_state["current_error"] = "No image available for face parsing"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No image available for face parsing"]
            return new_state
        
        try:
            # Parse face into regions
            regions = self.face_parser.parse_face(image)
            
            # Extract skin mask
            skin_mask = regions.get("skin", None)
            
            # Update state
            new_state = state.copy()
            new_state["skin_mask"] = skin_mask
            new_state["regions"] = regions
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Face parsing failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
