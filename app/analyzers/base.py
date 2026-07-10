"""Base Analyzer Class"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.schemas.analysis import (
    AcneAnalysis, 
    AcneSeverity, 
    PigmentationLevel, 
    PoreSize, 
    RednessLevel,
    SkinType, 
    WrinkleLevel
)


class BaseAnalyzer(ABC):
    """
    Base class for all skin analyzers.
    
    Each analyzer receives:
    - Aligned face image (RGB numpy array)
    - Skin mask (binary numpy array)
    
    Each analyzer should return a simple value or dict that can be
    aggregated by the pipeline.
    """
    
    @abstractmethod
    def analyze(
        self, 
        face_image: np.ndarray, 
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[Dict[str, np.ndarray]] = None
    ) -> Any:
        """
        Analyze the face image.
        
        Args:
            face_image: RGB numpy array (H x W x 3)
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            Analysis result (type depends on specific analyzer)
        """
        pass
    
    def _get_skin_pixels(
        self, 
        image: np.ndarray, 
        mask: np.ndarray
    ) -> np.ndarray:
        """Extract pixels within a mask"""
        if mask is None:
            return image.reshape(-1, 3)
        
        masked = image[mask > 0]
        return masked.reshape(-1, 3)
    
    def _get_region_pixels(
        self,
        image: np.ndarray,
        region_mask: np.ndarray
    ) -> np.ndarray:
        """Extract pixels from a specific region"""
        return self._get_skin_pixels(image, region_mask)
    
    def _calculate_mean_color(
        self, 
        pixels: np.ndarray
    ) -> np.ndarray:
        """Calculate mean RGB color"""
        if len(pixels) == 0:
            return np.array([0, 0, 0])
        return np.mean(pixels, axis=0)
    
    def _calculate_std_color(
        self, 
        pixels: np.ndarray
    ) -> np.ndarray:
        """Calculate standard deviation of RGB colors"""
        if len(pixels) == 0:
            return np.array([0, 0, 0])
        return np.std(pixels, axis=0)
    
    def _calculate_brightness(
        self, 
        pixels: np.ndarray
    ) -> float:
        """Calculate average brightness (0-255)"""
        if len(pixels) == 0:
            return 0.0
        return np.mean(pixels)
    
    def _calculate_contrast(
        self, 
        pixels: np.ndarray
    ) -> float:
        """Calculate color contrast"""
        if len(pixels) == 0:
            return 0.0
        rgb_std = np.std(pixels, axis=0)
        return np.mean(rgb_std)
    
    def _calculate_saturation(
        self, 
        pixels: np.ndarray
    ) -> float:
        """Calculate average saturation (0-1)"""
        if len(pixels) == 0:
            return 0.0
        
        # Convert to HSV
        hsv_pixels = np.zeros_like(pixels, dtype=np.float32)
        for i, pixel in enumerate(pixels):
            rgb = pixel.astype(np.float32) / 255.0
            max_val = np.max(rgb)
            min_val = np.min(rgb)
            delta = max_val - min_val
            
            # Saturation
            if max_val > 0:
                saturation = delta / max_val
            else:
                saturation = 0
            
            hsv_pixels[i] = [0, saturation, max_val]
        
        return float(np.mean(hsv_pixels[:, 1]))
