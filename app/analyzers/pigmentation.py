"""Pigmentation Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import PigmentationLevel


class PigmentationAnalyzer(BaseAnalyzer):
    """
    Analyzes skin pigmentation (dark spots, uneven tone).
    
    Pigmentation levels:
    - None: Even skin tone
    - Mild: Minor discoloration
    - Moderate: Noticeable pigmentation
    - Severe: Significant pigmentation issues
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> PigmentationLevel:
        """
        Analyze pigmentation of the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            PigmentationLevel enum value
        """
        if skin_mask is not None:
            skin_pixels = self._get_skin_pixels(face_image, skin_mask)
        else:
            skin_pixels = face_image.reshape(-1, 3)
        
        if len(skin_pixels) == 0:
            return PigmentationLevel.NONE
        
        # Calculate pigmentation score
        pigmentation_score = self._calculate_pigmentation_score(face_image, skin_mask)
        
        # Classify
        if pigmentation_score > 0.3:
            return PigmentationLevel.SEVERE
        elif pigmentation_score > 0.15:
            return PigmentationLevel.MODERATE
        elif pigmentation_score > 0.05:
            return PigmentationLevel.MILD
        else:
            return PigmentationLevel.NONE
    
    def _calculate_pigmentation_score(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate pigmentation score using color variance.
        
        Args:
            image: RGB numpy array
            mask: Optional mask
            
        Returns:
            Pigmentation score (0-1)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply mask if provided
        if mask is not None:
            gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Blur to get local averages
        blurred = cv2.GaussianBlur(gray, (25, 25), 0)
        
        # Calculate difference from local average (spot detection)
        diff = cv2.absdiff(gray.astype(float), blurred.astype(float))
        
        # Normalize difference
        diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
        
        # Threshold for significant spots (dark or light)
        _, dark_spots = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
        
        # Calculate proportion of spotted area
        spot_pixels = np.sum(dark_spots > 0)
        total_pixels = dark_spots.size
        
        if total_pixels == 0:
            return 0.0
        
        # Also consider color variance
        if mask is not None:
            pixels = self._get_skin_pixels(image, mask)
        else:
            pixels = image.reshape(-1, 3)
        
        color_std = np.std(pixels, axis=0)
        avg_color_std = np.mean(color_std) / 255.0
        
        # Combine both measures
        spot_score = float(spot_pixels / total_pixels)
        variance_score = float(np.clip(avg_color_std, 0, 1))
        
        # Weighted combination
        pigmentation_score = (spot_score * 0.6 + variance_score * 0.4)
        
        return pigmentation_score
