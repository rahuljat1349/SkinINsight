"""Acne Analyzer"""

import cv2
import numpy as np
from typing import Optional, Tuple

from app.analyzers.base import BaseAnalyzer
from app.schemas.analysis import AcneAnalysis, AcneSeverity


class AcneAnalyzer(BaseAnalyzer):
    """
    Analyzes acne severity and estimates lesion count.
    
    Acne severity levels:
    - None: No visible acne
    - Mild: Few lesions (<10)
    - Moderate: Several lesions (10-20)
    - Severe: Many lesions (>20)
    """
    
    def analyze(
        self,
        face_image: np.ndarray,
        skin_mask: Optional[np.ndarray] = None,
        regions: Optional[dict] = None
    ) -> AcneAnalysis:
        """
        Analyze acne on the skin.
        
        Args:
            face_image: RGB numpy array
            skin_mask: Binary mask of skin region
            regions: Dictionary of region masks
            
        Returns:
            AcneAnalysis with severity and count
        """
        if skin_mask is not None:
            lesion_count = self._count_lesions(face_image, skin_mask)
        else:
            lesion_count = self._count_lesions(face_image)
        
        # Classify severity
        if lesion_count == 0:
            severity = AcneSeverity.NONE
        elif lesion_count < 10:
            severity = AcneSeverity.MILD
        elif lesion_count < 20:
            severity = AcneSeverity.MODERATE
        else:
            severity = AcneSeverity.SEVERE
        
        return AcneAnalysis(severity=severity, count=lesion_count)
    
    def _count_lesions(
        self,
        image: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> int:
        """
        Count potential acne lesions.
        
        Args:
            image: RGB numpy array
            mask: Optional skin mask
            
        Returns:
            Estimated lesion count
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply mask if provided
        if mask is not None:
            gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Enhance contrast for spot detection
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Detect spots using Laplacian
        laplacian = cv2.Laplacian(enhanced, cv2.CV_64F)
        laplacian = np.uint8(np.absolute(laplacian))
        
        # Threshold
        _, thresh = cv2.threshold(laplacian, 40, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size (acne lesions are typically small)
        min_area = 5  # Minimum area in pixels
        max_area = 100  # Maximum area in pixels
        
        lesion_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Additional filter: check if it's darker than surrounding
                (x, y, w, h) = cv2.boundingRect(contour)
                if self._is_dark_spot(enhanced, x, y, w, h):
                    lesion_count += 1
        
        return lesion_count
    
    def _is_dark_spot(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        w: int,
        h: int
    ) -> bool:
        """
        Check if a region is a dark spot (potential lesion).
        
        Args:
            image: Grayscale image
            x, y, w, h: Bounding box of the region
            
        Returns:
            True if the region is darker than its surroundings
        """
        # Get region
        region = image[y:y+h, x:x+w]
        if region.size == 0:
            return False
        
        region_mean = np.mean(region)
        
        # Get surrounding area (with padding)
        pad = 5
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(image.shape[1], x + w + pad)
        y2 = min(image.shape[0], y + h + pad)
        
        surrounding = image[y1:y2, x1:x2]
        # Exclude the region itself
        if surrounding.shape[0] > h and surrounding.shape[1] > w:
            surrounding = np.concatenate([
                surrounding[:y-y1, :],
                surrounding[y-y1+h:, :]
            ], axis=0)
        
        if surrounding.size == 0:
            return False
        
        surrounding_mean = np.mean(surrounding)
        
        # Spot is dark if it's significantly darker than surroundings
        # and not too dark (could be shadow or hair)
        return (region_mean < surrounding_mean * 0.8) and (region_mean > 30)
