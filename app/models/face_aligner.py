"""Face Alignment Module"""

import cv2
import numpy as np
from typing import Tuple

from app.models.face_detector import FaceDetector


class FaceAligner:
    """
    Face alignment using facial landmarks.
    
    Normalizes face images for consistent analysis by:
    - Rotating to upright position
    - Scaling to standard size
    - Centering the face
    """
    
    # Standard face size for alignment
    STANDARD_SIZE = (224, 224)
    
    # Reference facial landmarks for alignment (5-point landmarks)
    # Order: left_eye, right_eye, nose, left_mouth_corner, right_mouth_corner
    REFERENCE_LANDMARKS = np.array([
        [0.35, 0.41],  # Left eye
        [0.65, 0.41],  # Right eye
        [0.50, 0.55],  # Nose
        [0.35, 0.70],  # Left mouth corner
        [0.65, 0.70],  # Right mouth corner
    ], dtype=np.float32)
    
    def __init__(self, face_detector: FaceDetector):
        self.face_detector = face_detector
        
    def align_face(
        self, 
        image: np.ndarray,
        output_size: Tuple[int, int] = STANDARD_SIZE
    ) -> np.ndarray:
        """
        Align a face image to standard position.
        
        Args:
            image: RGB numpy array (H x W x 3)
            output_size: Target size for the aligned face
            
        Returns:
            Aligned RGB numpy array of shape output_size
        """
        # Get landmarks
        landmarks = self.face_detector.get_face_landmarks(image)
        
        # Extract 5 key landmarks (assuming InsightFace returns 106 landmarks)
        # Map InsightFace landmarks to our 5-point reference
        if len(landmarks) >= 106:
            # InsightFace 106-point landmarks
            key_landmarks = np.array([
                landmarks[36],   # Left eye (approx)
                landmarks[45],   # Right eye (approx)
                landmarks[30],   # Nose tip
                landmarks[48],   # Left mouth corner
                landmarks[54],   # Right mouth corner
            ], dtype=np.float32)
        elif len(landmarks) >= 5:
            # Use first 5 landmarks if available
            key_landmarks = np.array(landmarks[:5], dtype=np.float32)
        else:
            # Fallback: just crop and resize using bbox
            bbox = self.face_detector.get_face_bbox(image)
            return self._crop_and_resize(image, bbox, output_size)
        
        # Normalize landmark coordinates to [0, 1] range
        image_height, image_width = image.shape[:2]
        normalized_landmarks = key_landmarks.copy()
        normalized_landmarks[:, 0] /= image_width
        normalized_landmarks[:, 1] /= image_height
        
        # Calculate similarity transform
        tform = self._get_similarity_transform(
            normalized_landmarks, 
            self.REFERENCE_LANDMARKS
        )
        
        # Apply transform
        aligned_image = cv2.warpAffine(
            image,
            tform,
            (output_size[0], output_size[1]),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return aligned_image
    
    def _get_similarity_transform(
        self, 
        src_points: np.ndarray, 
        dst_points: np.ndarray
    ) -> np.ndarray:
        """
        Calculate similarity transform between two sets of points.
        
        Args:
            src_points: Source points (N x 2)
            dst_points: Destination points (N x 2)
            
        Returns:
            2x3 affine transformation matrix
        """
        # Calculate mean and subtract from points
        src_mean = np.mean(src_points, axis=0)
        dst_mean = np.mean(dst_points, axis=0)
        
        src_centered = src_points - src_mean
        dst_centered = dst_points - dst_mean
        
        # Calculate scale and rotation
        src_std = np.sqrt(np.sum(src_centered ** 2))
        dst_std = np.sqrt(np.sum(dst_centered ** 2))
        
        scale = dst_std / src_std
        
        # Calculate rotation
        covariance = np.dot(src_centered.T, dst_centered)
        dst_norm = np.linalg.norm(dst_centered, axis=0)
        src_norm = np.linalg.norm(src_centered, axis=0)
        
        # Avoid division by zero
        if src_norm[0] * dst_norm[0] + src_norm[1] * dst_norm[1] > 0:
            rotation = covariance / (src_norm * dst_norm).T
        else:
            rotation = np.eye(2)
        
        # Handle reflection case
        if np.linalg.det(rotation) < 0:
            rotation = np.array([[1, 0], [0, -1]]) @ rotation
        
        # Build transformation matrix
        transform = np.eye(3)
        transform[:2, :2] = scale * rotation
        transform[:2, 2] = dst_mean - scale * rotation @ src_mean
        
        return transform[:2, :]
    
    def _crop_and_resize(
        self, 
        image: np.ndarray, 
        bbox: Tuple[int, int, int, int],
        output_size: Tuple[int, int]
    ) -> np.ndarray:
        """
        Simple crop and resize as fallback alignment.
        
        Args:
            image: RGB numpy array
            bbox: (x1, y1, x2, y2) bounding box
            output_size: Target size
            
        Returns:
            Cropped and resized image
        """
        x1, y1, x2, y2 = bbox
        
        # Add padding to bbox
        padding = 20
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(image.shape[1], x2 + padding)
        y2 = min(image.shape[0], y2 + padding)
        
        # Crop
        cropped = image[y1:y2, x1:x2]
        
        # Resize
        resized = cv2.resize(cropped, output_size, interpolation=cv2.INTER_LINEAR)
        
        return resized
    
    def get_aligned_face_with_mask(
        self,
        image: np.ndarray,
        output_size: Tuple[int, int] = STANDARD_SIZE
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get aligned face and a binary mask of the face region.
        
        Args:
            image: RGB numpy array
            output_size: Target size
            
        Returns:
            Tuple of (aligned_image, face_mask)
        """
        aligned_face = self.align_face(image, output_size)
        
        # Create a simple mask (ellipse covering most of the aligned face)
        mask = np.zeros(output_size, dtype=np.uint8)
        center = (output_size[0] // 2, output_size[1] // 2)
        axes = (output_size[0] // 2 * 0.8, output_size[1] // 2 * 0.9)
        angle = 0
        
        cv2.ellipse(mask, (center, axes, angle), 255, -1)
        
        return aligned_face, mask
