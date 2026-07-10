"""Quality Gate Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
import numpy as np
import cv2

from app.graph.state import AnalysisState
from app.core.config import settings


class QualityGateNode:
    """
    Node that checks image quality before proceeding to analysis.
    
    Checks:
    - Brightness
    - Blur
    - Skin visibility
    - Parser confidence (if available)
    
    If failed:
    - Set quality_check_passed = False
    - Set quality_errors and quality_suggestions
    - Pipeline should terminate early
    """
    
    def __init__(self):
        self.name = "quality_gate"
        self.min_brightness = 20.0  # Minimum average brightness (0-255)
        self.max_brightness = 240.0  # Maximum average brightness (0-255)
        self.min_blur_score = 20.0  # Minimum blur score (higher = less blur)
        self.min_skin_coverage = 0.1  # Minimum skin coverage (10% of image)
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Check image quality"""
        image = state.get("image")
        skin_mask = state.get("skin_mask")
        aligned_face = state.get("aligned_face")
        
        if image is None:
            new_state = state.copy()
            new_state["current_error"] = "No image available for quality check"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No image available for quality check"]
            return new_state
        
        try:
            quality_errors = []
            quality_suggestions = []
            
            # Use aligned face if available, otherwise use original image
            check_image = aligned_face if aligned_face is not None else image
            
            # Check brightness
            brightness_score, brightness_ok = self._check_brightness(check_image)
            if not brightness_ok:
                quality_errors.append("poor_lighting")
                quality_suggestions.append(
                    "Please ensure good lighting. Avoid harsh shadows or overexposure."
                )
            
            # Check blur
            blur_score, blur_ok = self._check_blur(check_image)
            if not blur_ok:
                quality_errors.append("excessive_blur")
                quality_suggestions.append(
                    "Please ensure the image is sharp and in focus. Avoid motion blur."
                )
            
            # Check skin coverage
            if skin_mask is not None:
                skin_ok = self._check_skin_coverage(skin_mask)
                if not skin_ok:
                    quality_errors.append("insufficient_skin")
                    quality_suggestions.append(
                        "Please ensure your full face is visible in the image."
                    )
            
            # Determine if quality check passed
            quality_passed = (
                len(quality_errors) == 0 and
                brightness_ok and
                blur_ok and
                (skin_mask is None or skin_ok)
            )
            
            # Map quality errors to human-readable messages for the error handler
            error_msg_map = {
                "poor_lighting": "Poor lighting",
                "excessive_blur": "Excessive blur",
                "insufficient_skin": "Insufficient skin visibility"
            }
            
            # Update state
            new_state = state.copy()
            new_state["quality_check_passed"] = quality_passed
            new_state["quality_errors"] = quality_errors if quality_errors else []
            new_state["quality_suggestions"] = quality_suggestions if quality_suggestions else []
            new_state["errors"] = state.get("errors", [])
            
            # If quality check failed, set error state with specific error
            if not quality_passed:
                new_state["is_error_state"] = True
                first_error = quality_errors[0] if quality_errors else "image_quality_failed"
                new_state["current_error"] = error_msg_map.get(first_error, "Image quality check failed")
            
            return new_state
            
        except Exception as e:
            error_msg = f"Quality check failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
    
    def _check_brightness(self, image: np.ndarray) -> tuple[float, bool]:
        """Check if image brightness is within acceptable range"""
        # Calculate average brightness (grayscale value)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        avg_brightness = float(np.mean(gray))
        
        # Check if within range
        if avg_brightness < self.min_brightness:
            return avg_brightness, False
        elif avg_brightness > self.max_brightness:
            return avg_brightness, False
        else:
            return avg_brightness, True
    
    def _check_blur(self, image: np.ndarray) -> tuple[float, bool]:
        """Check if image has excessive blur"""
        # Use Laplacian variance as blur metric
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Laplacian filter
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = float(np.var(laplacian))
        
        # Higher variance = less blur
        return variance, variance > self.min_blur_score
    
    def _check_skin_coverage(self, skin_mask: np.ndarray) -> bool:
        """Check if skin mask covers enough of the image"""
        if skin_mask is None:
            return True
        
        # Calculate coverage
        total_pixels = skin_mask.size
        skin_pixels = np.count_nonzero(skin_mask)
        coverage = skin_pixels / total_pixels
        
        return coverage >= self.min_skin_coverage
