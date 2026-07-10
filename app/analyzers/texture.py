"""Texture Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer


class TextureAnalyzer(BaseAnalyzer):
    """
    Analyzes skin texture and returns a smoothness score.
    
    Smoothness score:
    - 0: Very rough texture
    - 100: Very smooth texture
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> int:
        """
        Analyze texture smoothness of the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            Smoothness score (0-100)
        """
        # Calculate smoothness score
        smoothness = self._calculate_smoothness(face_image, skin_mask)
        
        # Convert to 0-100 scale
        return int(np.clip(smoothness * 100, 0, 100))
    
    def _calculate_smoothness(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate texture smoothness.
        
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
        
        # Method 1: Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        edge_density = float(edge_pixels / total_pixels) if total_pixels > 0 else 0
        
        # Method 2: Variance of Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize variance (typical range for skin is 10-200)
        normalized_variance = min(1.0, max(0, variance / 200))
        
        # Method 3: Local binary pattern texture
        lbp_smoothness = self._calculate_lbp_smoothness(gray)
        
        # Combine methods
        # Lower edge density and variance = smoother
        smoothness = (
            (1 - edge_density) * 0.4 +
            (1 - normalized_variance) * 0.3 +
            lbp_smoothness * 0.3
        )
        
        return smoothness
    
    def _calculate_lbp_smoothness(self, image: np.ndarray) -> float:
        """
        Calculate smoothness using Local Binary Patterns.
        
        Args:
            image: Grayscale image
            
        Returns:
            Smoothness score (0-1)
        """
        # Simple LBP implementation
        height, width = image.shape
        lbp_result = np.zeros_like(image, dtype=np.uint8)
        
        # LBP parameters
        radius = 1
        n_points = 8
        
        # Calculate LBP for each pixel
        for i in range(radius, height - radius):
            for j in range(radius, width - radius):
                center = image[i, j]
                pattern = 0
                
                # Sample points on a circle
                for p in range(n_points):
                    x = i + radius * np.cos(2 * np.pi * p / n_points)
                    y = j - radius * np.sin(2 * np.pi * p / n_points)
                    
                    x = int(round(x))
                    y = int(round(y))
                    
                    if x < 0 or x >= height or y < 0 or y >= width:
                        continue
                    
                    if image[x, y] >= center:
                        pattern |= (1 << p)
                
                lbp_result[i, j] = pattern
        
        # Calculate texture uniformity
        # Uniform patterns (0-2 transitions) indicate smooth texture
        uniform_patterns = [0, 1, 2, 3, 4, 58, 61, 62, 124, 127, 191, 253, 254, 255]
        
        uniform_count = np.sum(np.isin(lbp_result, uniform_patterns))
        total = lbp_result.size
        
        if total == 0:
            return 0.5
        
        uniform_ratio = float(uniform_count / total)
        
        # Higher uniform pattern ratio = smoother texture
        return uniform_ratio
