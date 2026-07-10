"""Image Decoder Node for LangGraph Pipeline"""

from typing import Any, Dict, Optional
import numpy as np
from PIL import Image
from io import BytesIO

from app.graph.state import AnalysisState
from app.core.exceptions import UnsupportedFormatError


class ImageDecoderNode:
    """
    Node that decodes image bytes into a numpy array.
    
    Input:
    - image_bytes: Raw image bytes from upload
    
    Output:
    - image: RGB numpy array (H x W x 3)
    
    Failure:
    - Unsupported image format
    """
    
    def __init__(self):
        self.name = "image_decoder"
        self.supported_formats = {"jpg", "jpeg", "png", "webp"}
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Decode image bytes to numpy array"""
        image_bytes = state.get("image_bytes")
        
        if image_bytes is None:
            state["current_error"] = "No image bytes provided"
            state["is_error_state"] = True
            state["errors"] = state.get("errors", []) + ["No image bytes provided"]
            return state
        
        try:
            # Open image with PIL
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB and then to numpy array
            rgb_image = image.convert("RGB")
            image_array = np.array(rgb_image)
            
            # Update state
            new_state = state.copy()
            new_state["image"] = image_array
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Failed to decode image: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
