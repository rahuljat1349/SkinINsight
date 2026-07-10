"""Hydration Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer


class HydrationAnalyzer(BaseAnalyzer):
    """
    Analyzes skin hydration on a scale of 0-100.
    
    Well-hydrated skin has:
    - Smoother texture (fewer visible lines/wrinkles)
    - More even tone
    - Higher elasticity (indirectly: plumpness/brightness)
    - Less flakiness
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> int:
        """
        Analyze hydration of the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            Hydration score (0-100)
        """
        if skin_mask is None:
            skin_pixels = face_image.reshape(-1, 3)
        else:
            skin_pixels = self._get_skin_pixels(face_image, skin_mask)
        
        if len(skin_pixels) == 0:
            return 50
        
        # Calculate texture smoothness
        smoothness = self._calculate_smoothness(face_image, skin_mask)
        
        # Calculate color uniformity
        uniformity = self._calculate_uniformity(skin_pixels)
        
        # Calculate average brightness (plump skin is brighter)
        brightness = self._calculate_brightness(skin_pixels)
        
        # Features normalized to 0-100
        smoothness_score = min(100, smoothness * 150)
        uniformity_score = min(100, uniformity * 150)
        brightness_score = min(100, (brightness / 255) * 100)
        
        # Weighted combination
        hydration = (
            smoothness_score * 0.4 +
            uniformity_score * 0.35 +
            brightness_score * 0.25
        )
        
        return int(np.clip(hydration, 0, 100))
    
    def _calculate_smoothness(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate texture smoothness using edge detection.
        
        Args:
            image: RGB numpy array
            mask: Optional mask
            
        Returns:
            Smoothness score (0-1), higher is smoother
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply mask if provided
        if mask is not None:
            gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Calculate edge density
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        
        if total_pixels == 0:
            return 0.5
        
        # Inverse: fewer edges = smoother
        edge_density = edge_pixels / total_pixels
        smoothness = 1.0 - edge_density
        
        return float(smoothness)
    
    def _calculate_uniformity(self, pixels: np.ndarray) -> float:
        """
        Calculate color uniformity.
        
        Args:
            pixels: RGB pixels array
            
        Returns:
            Uniformity score (0-1), higher is more uniform
        """
        if len(pixels) == 0:
            return 0.5
        
        # Calculate standard deviation for each channel
        std_r = np.std(pixels[:, 0])
        std_g = np.std(pixels[:, 1])
        std_b = np.std(pixels[:, 2])
        
        # Average standard deviation
        avg_std = (std_r + std_g + std_b) / 3
        
        # Normalize to 0-1 (assuming typical std is around 25-50 for skin)
        normalized_std = avg_std / 255.0
        
        # Inverse: lower std = more uniform
        uniformity = 1.0 - min(1.0, normalized_std * 2)
        
        return float(np.clip(uniformity, 0, 1))
