"""Skin Tone Analyzer"""

import cv2
import numpy as np
from typing import Optional

from app.analyzers.base import BaseAnalyzer


class SkinToneAnalyzer(BaseAnalyzer):
    """
    Estimates skin tone for educational purposes.
    
    Uses the Fitzpatrick scale or similar classification.
    This is for educational purposes only and not for medical diagnosis.
    """
    
    # Common skin tone classifications
    SKIN_TONES = [
        "Very Fair",
        "Fair",
        "Light",
        "Medium",
        "Olive",
        "Tan",
        "Brown",
        "Dark Brown",
        "Deep Dark"
    ]
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> Optional[str]:
        """
        Estimate skin tone.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            Skin tone description or None
        """
        if skin_mask is not None:
            skin_pixels = self._get_skin_pixels(face_image, skin_mask)
        else:
            skin_pixels = face_image.reshape(-1, 3)
        
        if len(skin_pixels) == 0:
            return None
        
        # Calculate average skin color
        mean_color = self._calculate_mean_color(skin_pixels)
        
        # Convert to LAB color space for better color difference perception
        lab = cv2.cvtColor(np.uint8([[mean_color]]), cv2.COLOR_RGB2LAB)
        l_value = lab[0, 0, 0]  # Lightness (0-255)
        
        # Classify based on lightness
        if l_value > 220:
            return "Very Fair"
        elif l_value > 190:
            return "Fair"
        elif l_value > 160:
            return "Light"
        elif l_value > 130:
            return "Medium"
        elif l_value > 100:
            return "Olive"
        elif l_value > 70:
            return "Tan"
        elif l_value > 50:
            return "Brown"
        elif l_value > 30:
            return "Dark Brown"
        else:
            return "Deep Dark"
    
    def get_skin_tone_description(self, tone: str) -> str:
        """
        Get description for a skin tone.
        
        Args:
            tone: Skin tone name
            
        Returns:
            Description
        """
        descriptions = {
            "Very Fair": "Very light skin that burns easily",
            "Fair": "Light skin that tans minimally",
            "Light": "Light to medium skin that tans gradually",
            "Medium": "Medium skin that tans well",
            "Olive": "Light brown or olive skin",
            "Tan": "Brown skin that tans deeply",
            "Brown": "Dark brown skin",
            "Dark Brown": "Very dark brown skin",
            "Deep Dark": "Deepest dark skin tones"
        }
        return descriptions.get(tone, "Unknown skin tone")
