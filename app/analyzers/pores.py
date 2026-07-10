"""Pores Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import PoreSize


class PoresAnalyzer(BaseAnalyzer):
    """
    Analyzes pore size.
    
    Pore sizes:
    - Small: Minimal visible pores
    - Medium: Noticeable pores
    - Large: Very visible pores
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> PoreSize:
        """
        Analyze pore size on the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            PoreSize enum value
        """
        # Calculate pore visibility score
        pore_score = self._calculate_pore_score(face_image, skin_mask)
        
        # Classify
        if pore_score > 0.25:
            return PoreSize.LARGE
        elif pore_score > 0.1:
            return PoreSize.MEDIUM
        else:
            return PoreSize.SMALL
    
    def _calculate_pore_score(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate pore visibility score.
        
        Args:
            image: RGB numpy array
            mask: Optional mask
            
        Returns:
            Pore score (0-1), higher means more visible pores
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply mask if provided
        if mask is not None:
            gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Detect small dark spots (pores)
        # Pores appear as small dark dots
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        diff = enhanced - blurred
        
        # Threshold for dark spots
        _, thresh = cv2.threshold(diff, -10, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count small circular contours (pores)
        pore_count = 0
        min_radius = 1
        max_radius = 5
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 0:
                # Approximate radius
                radius = np.sqrt(area / np.pi)
                if min_radius < radius < max_radius:
                    # Check if roughly circular
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter ** 2)
                        if circularity > 0.7:  # Roughly circular
                            pore_count += 1
        
        # Calculate pore density
        total_pixels = thresh.size
        if total_pixels == 0:
            return 0.0
        
        pore_density = float(pore_count / (total_pixels / 100))  # Normalize
        
        # Cap at 1.0
        return min(1.0, pore_density * 0.01)
