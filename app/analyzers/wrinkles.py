"""Wrinkles Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import WrinkleLevel


class WrinklesAnalyzer(BaseAnalyzer):
    """
    Analyzes wrinkles severity.
    
    Wrinkle levels:
    - Minimal: Few or no visible wrinkles
    - Mild: Some fine lines
    - Moderate: Noticeable wrinkles
    - Severe: Deep wrinkles
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> WrinkleLevel:
        """
        Analyze wrinkles on the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            WrinkleLevel enum value
        """
        # Calculate wrinkle score
        wrinkle_score = self._calculate_wrinkle_score(face_image, skin_mask)
        
        # Classify
        if wrinkle_score > 0.3:
            return WrinkleLevel.SEVERE
        elif wrinkle_score > 0.15:
            return WrinkleLevel.MODERATE
        elif wrinkle_score > 0.05:
            return WrinkleLevel.MILD
        else:
            return WrinkleLevel.MINIMAL
    
    def _calculate_wrinkle_score(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate wrinkle score using edge and texture analysis.
        
        Args:
            image: RGB numpy array
            mask: Optional mask
            
        Returns:
            Wrinkle score (0-1)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply mask if provided
        if mask is not None:
            gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Apply mask to edges
        if mask is not None:
            edges = cv2.bitwise_and(edges, edges, mask=mask)
        
        # Calculate edge density
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        
        if total_pixels == 0:
            return 0.0
        
        edge_density = float(edge_pixels / total_pixels)
        
        # Apply morphological operations to detect line-like structures
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        eroded = cv2.erode(dilated, kernel, iterations=1)
        
        # Find long, thin structures (wrinkles)
        wrinkle_mask = dilated - eroded
        wrinkle_pixels = np.sum(wrinkle_mask > 0)
        
        if total_pixels == 0:
            wrinkle_score = 0.0
        else:
            wrinkle_score = float(wrinkle_pixels / total_pixels)
        
        # Combine edge density and wrinkle detection
        combined_score = (edge_density * 0.4 + wrinkle_score * 0.6)
        
        return combined_score
