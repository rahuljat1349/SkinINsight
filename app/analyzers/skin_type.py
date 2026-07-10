"""Skin Type Analyzer"""

import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import SkinType


class SkinTypeAnalyzer(BaseAnalyzer):
    """
    Determines skin type based on oiliness and hydration scores.
    
    Skin types:
    - Oily: High oiliness, medium-low hydration
    - Dry: Low oiliness, low hydration
    - Combination: High oiliness in T-zone, normal elsewhere
    - Normal: Balanced oiliness and hydration
    """
    
    # Thresholds for classification
    OILY_THRESHOLD = 70
    DRY_HYDRATION_THRESHOLD = 40
    NORMAL_OILY_RANGE = (30, 70)
    NORMAL_HYDRATION_RANGE = (40, 80)
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None,
        oiliness: Optional[int] = None,
        hydration: Optional[int] = None
    ) -> SkinType:
        """
        Determine skin type.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask
            regions: Region masks
            oiliness: Pre-calculated oiliness score (0-100)
            hydration: Pre-calculated hydration score (0-100)
            
        Returns:
            SkinType enum value
        """
        # If oiliness and hydration are provided, use them
        if oiliness is not None and hydration is not None:
            return self._classify_by_scores(oiliness, hydration)
        
        # Otherwise, estimate from image
        if skin_mask is not None:
            skin_pixels = self._get_skin_pixels(face_image, skin_mask)
            oiliness = self._estimate_oiliness(skin_pixels)
            hydration = self._estimate_hydration(skin_pixels)
            return self._classify_by_scores(oiliness, hydration)
        
        # Fallback: return Normal
        return SkinType.NORMAL
    
    def _classify_by_scores(self, oiliness: int, hydration: int) -> SkinType:
        """Classify skin type based on scores"""
        # Oily: High oiliness (>70), any hydration
        if oiliness >= self.OILY_THRESHOLD:
            return SkinType.OILY
        
        # Dry: Low hydration (<40), low oiliness (<50)
        if hydration < self.DRY_HYDRATION_THRESHOLD and oiliness < 50:
            return SkinType.DRY
        
        # Combination: Medium oiliness (50-70) with medium hydration (40-70)
        if (50 <= oiliness <= 70 and 
            40 <= hydration <= 70):
            return SkinType.COMBINATION
        
        # Normal: Balanced scores
        if (self.NORMAL_OILY_RANGE[0] <= oiliness <= self.NORMAL_OILY_RANGE[1] and
            self.NORMAL_HYDRATION_RANGE[0] <= hydration <= self.NORMAL_HYDRATION_RANGE[1]):
            return SkinType.NORMAL
        
        # Default to Combination for edge cases
        return SkinType.COMBINATION
    
    def _estimate_oiliness(self, pixels: np.ndarray) -> int:
        """
        Estimate oiliness from image pixels.
        
        Oily skin tends to have:
        - Higher brightness (shininess)
        - Higher saturation
        - More uniform color (less texture)
        """
        if len(pixels) == 0:
            return 50
        
        brightness = self._calculate_brightness(pixels)
        saturation = self._calculate_saturation(pixels)
        
        # Normalize brightness and saturation to 0-100
        # Assuming typical skin brightness is around 128
        brightness_score = min(100, (brightness / 255) * 200)
        saturation_score = min(100, saturation * 200)
        
        # Oiliness score: higher for bright, saturated skin
        oiliness = (brightness_score * 0.6 + saturation_score * 0.4)
        
        return int(np.clip(oiliness, 0, 100))
    
    def _estimate_hydration(self, pixels: np.ndarray) -> int:
        """
        Estimate hydration from image pixels.
        
        Hydrated skin tends to have:
        - Smoother texture (lower contrast)
        - More uniform color
        - Higher brightness (plumpness)
        """
        if len(pixels) == 0:
            return 50
        
        contrast = self._calculate_contrast(pixels)
        brightness = self._calculate_brightness(pixels)
        
        # Normalize to 0-100
        # Lower contrast means more hydrated
        contrast_score = max(0, 100 - (contrast / 255) * 100)
        brightness_score = min(100, (brightness / 255) * 100)
        
        # Hydration score: higher for smooth, bright skin
        hydration = (contrast_score * 0.7 + brightness_score * 0.3)
        
        return int(np.clip(hydration, 0, 100))
