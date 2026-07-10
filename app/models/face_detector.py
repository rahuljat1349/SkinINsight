"""Face Detection Module using InsightFace"""

import cv2
import numpy as np
from typing import List, Optional, Tuple

from app.core.config import settings
from app.core.exceptions import NoFaceDetectedError, MultipleFacesError, FaceTooSmallError
from app.schemas.image import FaceDetectionResult


class FaceDetector:
    """
    Face detection using InsightFace.
    
    Detects faces in images and provides bounding boxes and landmarks.
    """
    
    def __init__(self):
        self.settings = settings
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize InsightFace model"""
        try:
            from insightface.app import FaceAnalysis
            
            # Initialize face analysis
            self.model = FaceAnalysis(
                name="buffalo_l",
                root=self.settings.insightface_model_path,
                providers=['CPUExecutionProvider']
            )
            self.model.prepare(ctx_id=0, det_thresh=0.5, det_size=(640, 640))
            
        except ImportError as e:
            raise ImportError(
                "InsightFace is required for face detection. "
                "Please install it with: pip install insightface"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize InsightFace model: {e}") from e
    
    def detect_faces(self, image: np.ndarray) -> FaceDetectionResult:
        """
        Detect faces in an image.
        
        Args:
            image: RGB numpy array (H x W x 3)
            
        Returns:
            FaceDetectionResult with detection information
            
        Raises:
            NoFaceDetectedError: If no face is detected
            MultipleFacesError: If multiple faces are detected
            FaceTooSmallError: If the detected face is too small
        """
        if self.model is None:
            raise RuntimeError("Face detection model not initialized")
        
        # Convert to BGR for InsightFace
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Perform detection
        faces = self.model.get(image_bgr)
        
        # Check number of faces
        num_faces = len(faces)
        
        if num_faces == 0:
            raise NoFaceDetectedError()
        
        if num_faces > 1:
            raise MultipleFacesError(num_faces)
        
        # Extract face information
        face = faces[0]
        bbox = face.bbox.astype(int).tolist()
        landmarks = face.kps.astype(int).tolist() if face.kps is not None else []
        confidence = float(face.det_score) if hasattr(face, 'det_score') else 1.0
        
        # Check face size
        face_width = bbox[2] - bbox[0]
        face_height = bbox[3] - bbox[1]
        min_size = self.settings.min_face_size_pixels
        
        if face_width < min_size or face_height < min_size:
            raise FaceTooSmallError(face_width, face_height, min_size)
        
        return FaceDetectionResult(
            faces_detected=num_faces,
            bounding_boxes=[bbox],
            is_valid=True
        )
    
    def get_face_bbox(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Get the bounding box of the first detected face.
        
        Args:
            image: RGB numpy array
            
        Returns:
            Tuple of (x1, y1, x2, y2) coordinates
        """
        result = self.detect_faces(image)
        return tuple(result.bounding_boxes[0])
    
    def get_face_landmarks(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """
        Get facial landmarks for the first detected face.
        
        Args:
            image: RGB numpy array
            
        Returns:
            List of (x, y) landmark coordinates
        """
        if self.model is None:
            raise RuntimeError("Face detection model not initialized")
        
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        faces = self.model.get(image_bgr)
        
        if len(faces) == 0:
            raise NoFaceDetectedError()
        
        face = faces[0]
        landmarks = face.kps.astype(int).tolist() if face.kps is not None else []
        
        return [(int(lm[0]), int(lm[1])) for lm in landmarks]
