"""Redness Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import RednessLevel


class RednessAnalyzer(BaseAnalyzer):
    """
    Analyzes skin redness.
    
    Redness levels:
    - Low: Minimal redness
    - Moderate: Noticeable redness
    - High: Significant redness
    """
    
    # Thresholds for redness detection
    RED_THRESHOLD = 150  # R channel value threshold
    RED_DOMINANCE_THRESHOLD = 0.4  # R should be significantly higher than G and B
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> RednessLevel:
        """
        Analyze redness of the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            RednessLevel enum value
        """
        if skin_mask is not None:
            skin_pixels = self._get_skin_pixels(face_image, skin_mask)
        else:
            skin_pixels = face_image.reshape(-1, 3)
        
        if len(skin_pixels) == 0:
            return RednessLevel.LOW
        
        # Calculate redness score
        redness_score = self._calculate_redness_score(skin_pixels)
        
        # Classify
        if redness_score > 0.25:
            return RednessLevel.HIGH
        elif redness_score > 0.1:
            return RednessLevel.MODERATE
        else:
            return RednessLevel.LOW
    
    def _calculate_redness_score(self, pixels: np.ndarray) -> float:
        """
        Calculate redness score (0-1).
        
        Args:
            pixels: RGB pixels array
            
        Returns:
            Redness score
        """
        if len(pixels) == 0:
            return 0.0
        
        # Extract channels
        r = pixels[:, 0].astype(float)
        g = pixels[:, 1].astype(float)
        b = pixels[:, 2].astype(float)
        
        # Normalize
        total = r + g + b
        # Avoid division by zero
        total[total == 0] = 1
        
        # Red proportion
        r_prop = r / total
        g_prop = g / total
        b_prop = b / total
        
        # Red dominance: R should be significantly higher than G and B
        red_dominant = ((r_prop > g_prop) & (r_prop > b_prop)) & \
                       ((r_prop - g_prop) > 0.1) & \
                       ((r_prop - b_prop) > 0.1)
        
        # Also consider absolute red values
        bright_red = (r > self.RED_THRESHOLD) & \
                     (r > g * 1.2) & \
                     (r > b * 1.2)
        
        # Combine both methods
        red_pixels = red_dominant | bright_red
        
        redness_score = float(np.sum(red_pixels) / len(pixels))
        
        return redness_score
