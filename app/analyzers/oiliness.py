"""Oiliness Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer


class OilinessAnalyzer(BaseAnalyzer):
    """
    Analyzes skin oiliness on a scale of 0-100.
    
    Oilier skin has:
    - Higher brightness (shininess/reflectivity)
    - More saturated colors
    - Smoother texture (pores less visible)
    - More uniform appearance
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> int:
        """
        Analyze oiliness of the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            Oiliness score (0-100)
        """
        if skin_mask is None:
            # Analyze entire face
            skin_pixels = face_image.reshape(-1, 3)
        else:
            skin_pixels = self._get_skin_pixels(face_image, skin_mask)
        
        if len(skin_pixels) == 0:
            return 50
        
        # Calculate various features
        brightness = self._calculate_brightness(skin_pixels)
        saturation = self._calculate_saturation(skin_pixels)
        contrast = self._calculate_contrast(skin_pixels)
        
        # Detect specular highlights (very bright spots)
        highlights = self._detect_highlights(face_image, skin_mask)
        
        # Oiliness features (normalized to 0-100)
        brightness_score = min(100, (brightness / 255) * 150)
        saturation_score = min(100, saturation * 150)
        smoothness_score = max(0, 100 - (contrast / 255) * 150)
        highlight_score = min(100, highlights * 200)
        
        # Weighted combination
        oiliness = (
            brightness_score * 0.3 +
            saturation_score * 0.25 +
            smoothness_score * 0.25 +
            highlight_score * 0.2
        )
        
        return int(np.clip(oiliness, 0, 100))
    
    def _detect_highlights(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Detect specular highlights (very bright spots).
        
        Args:
            image: RGB numpy array
            mask: Optional mask to limit detection area
            
        Returns:
            Proportion of image that is very bright (0-1)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply mask if provided
        if mask is not None:
            gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Threshold for very bright pixels
        _, bright_mask = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
        
        # Calculate proportion of bright pixels
        bright_pixels = np.sum(bright_mask > 0)
        total_pixels = bright_mask.size
        
        if total_pixels == 0:
            return 0.0
        
        return float(bright_pixels / total_pixels)
