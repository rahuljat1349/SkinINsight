"""Face Parsing / Segmentation Module"""

import cv2
import numpy as np
from typing import Dict, Tuple

from app.models.face_detector import FaceDetector


class FaceParser:
    """
    Face parsing for skin region segmentation.
    
    Segments the face into different regions:
    - Skin
    - Forehead
    - Left cheek
    - Right cheek
    - Nose
    - Chin
    
    Excludes: Hair, Eyes, Lips, Beard, Background
    """
    
    # Region definitions based on facial landmarks
    REGIONS = {
        "skin": "All facial skin area",
        "forehead": "Forehead region",
        "left_cheek": "Left cheek region",
        "right_cheek": "Right cheek region",
        "nose": "Nose region",
        "chin": "Chin region"
    }
    
    def __init__(self, face_detector: FaceDetector):
        self.face_detector = face_detector
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """
        Initialize face parsing model.
        
        For MVP, we'll use a simple geometric approach based on landmarks.
        In production, this would use a pre-trained segmentation model.
        """
        # Try to load a pre-trained model if available
        # For now, we'll use landmark-based segmentation
        pass
    
    def parse_face(
        self, 
        image: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Parse face into regions.
        
        Args:
            image: RGB numpy array (H x W x 3)
            
        Returns:
            Dictionary mapping region names to binary masks
        """
        # Get landmarks
        landmarks = self.face_detector.get_face_landmarks(image)
        image_height, image_width = image.shape[:2]
        
        masks = {}
        
        # Create skin mask (approx face oval)
        masks["skin"] = self._create_skin_mask(image, landmarks)
        
        # Create region masks based on landmarks
        if len(landmarks) >= 106:
            # InsightFace 106 landmarks
            masks["forehead"] = self._create_forehead_mask(image, landmarks)
            masks["left_cheek"] = self._create_cheek_mask(image, landmarks, side="left")
            masks["right_cheek"] = self._create_cheek_mask(image, landmarks, side="right")
            masks["nose"] = self._create_nose_mask(image, landmarks)
            masks["chin"] = self._create_chin_mask(image, landmarks)
        else:
            # Fallback: divide skin mask into regions
            masks["forehead"] = self._create_region_mask(masks["skin"], "forehead")
            masks["left_cheek"] = self._create_region_mask(masks["skin"], "left_cheek")
            masks["right_cheek"] = self._create_region_mask(masks["skin"], "right_cheek")
            masks["nose"] = self._create_region_mask(masks["skin"], "nose")
            masks["chin"] = self._create_region_mask(masks["skin"], "chin")
        
        return masks
    
    def _create_skin_mask(
        self, 
        image: np.ndarray, 
        landmarks: list
    ) -> np.ndarray:
        """Create a skin mask covering the entire face area"""
        image_height, image_width = image.shape[:2]
        mask = np.zeros((image_height, image_width), dtype=np.uint8)
        
        # Get face bounding box
        try:
            bbox = self.face_detector.get_face_bbox(image)
            x1, y1, x2, y2 = bbox
            
            # Create ellipse covering face area
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            width = x2 - x1
            height = y2 - y1
            
            # Draw ellipse
            cv2.ellipse(
                mask,
                ((center_x, center_y), (width // 2, height // 2), 0),
                255,
                -1
            )
            
            # Also fill the bounding box to ensure full coverage
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            
        except Exception:
            # Fallback: use a simple center ellipse
            center = (image_width // 2, image_height // 2)
            axes = (min(image_width, image_height) // 2, min(image_width, image_height) // 2)
            cv2.ellipse(mask, (center, axes, 0), 255, -1)
        
        return mask
    
    def _create_forehead_mask(
        self, 
        image: np.ndarray, 
        landmarks: list
    ) -> np.ndarray:
        """Create forehead region mask"""
        image_height, image_width = image.shape[:2]
        mask = np.zeros((image_height, image_width), dtype=np.uint8)
        
        try:
            # Get relevant landmarks
            # Approximate positions for forehead
            # Using landmarks around the top of the face
            points = []
            for i in range(0, 20):  # Top landmarks
                if i < len(landmarks):
                    points.append((landmarks[i][0], landmarks[i][1]))
            
            if points:
                # Create polygon from points
                pts = np.array(points, np.int32)
                cv2.fillPoly(mask, [pts], 255)
                
        except Exception:
            pass
        
        return mask
    
    def _create_cheek_mask(
        self, 
        image: np.ndarray, 
        landmarks: list,
        side: str = "left"
    ) -> np.ndarray:
        """Create cheek region mask"""
        image_height, image_width = image.shape[:2]
        mask = np.zeros((image_height, image_width), dtype=np.uint8)
        
        try:
            # For now, create a simple rectangular region for cheek
            bbox = self.face_detector.get_face_bbox(image)
            x1, y1, x2, y2 = bbox
            
            face_width = x2 - x1
            face_height = y2 - y1
            
            if side == "left":
                cheek_x1 = x1
                cheek_x2 = x1 + face_width // 3
            else:  # right
                cheek_x1 = x2 - face_width // 3
                cheek_x2 = x2
            
            cheek_y1 = y1 + face_height // 4
            cheek_y2 = y2 - face_height // 4
            
            # Create rectangle
            cv2.rectangle(
                mask,
                (cheek_x1, cheek_y1),
                (cheek_x2, cheek_y2),
                255,
                -1
            )
            
            # Smooth with ellipse
            center_x = (cheek_x1 + cheek_x2) // 2
            center_y = (cheek_y1 + cheek_y2) // 2
            axes = ((cheek_x2 - cheek_x1) // 2, (cheek_y2 - cheek_y1) // 2)
            cv2.ellipse(
                mask,
                ((center_x, center_y), axes, 0),
                255,
                -1
            )
            
        except Exception:
            pass
        
        return mask
    
    def _create_nose_mask(
        self, 
        image: np.ndarray, 
        landmarks: list
    ) -> np.ndarray:
        """Create nose region mask"""
        image_height, image_width = image.shape[:2]
        mask = np.zeros((image_height, image_width), dtype=np.uint8)
        
        try:
            bbox = self.face_detector.get_face_bbox(image)
            x1, y1, x2, y2 = bbox
            
            face_width = x2 - x1
            face_height = y2 - y1
            
            nose_x1 = x1 + face_width * 2 // 5
            nose_x2 = x1 + face_width * 3 // 5
            nose_y1 = y1 + face_height // 3
            nose_y2 = y1 + face_height * 2 // 3
            
            cv2.rectangle(
                mask,
                (nose_x1, nose_y1),
                (nose_x2, nose_y2),
                255,
                -1
            )
            
        except Exception:
            pass
        
        return mask
    
    def _create_chin_mask(
        self, 
        image: np.ndarray, 
        landmarks: list
    ) -> np.ndarray:
        """Create chin region mask"""
        image_height, image_width = image.shape[:2]
        mask = np.zeros((image_height, image_width), dtype=np.uint8)
        
        try:
            bbox = self.face_detector.get_face_bbox(image)
            x1, y1, x2, y2 = bbox
            
            face_height = y2 - y1
            
            chin_y1 = y2 - face_height // 3
            chin_y2 = y2
            
            # Chin is roughly the bottom third of the face
            cv2.rectangle(
                mask,
                (x1, chin_y1),
                (x2, chin_y2),
                255,
                -1
            )
            
        except Exception:
            pass
        
        return mask
    
    def _create_region_mask(
        self, 
        skin_mask: np.ndarray,
        region: str
    ) -> np.ndarray:
        """Create a simple region mask from the skin mask"""
        height, width = skin_mask.shape
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Simple division of skin mask into regions
        non_zero = np.nonzero(skin_mask)
        if len(non_zero[0]) == 0:
            return mask
        
        min_y, max_y = np.min(non_zero[0]), np.max(non_zero[0])
        min_x, max_x = np.min(non_zero[1]), np.max(non_zero[1])
        
        face_height = max_y - min_y
        face_width = max_x - min_x
        
        if region == "forehead":
            y_start = min_y
            y_end = min_y + face_height // 4
            cv2.rectangle(mask, (min_x, y_start), (max_x, y_end), 255, -1)
        elif region == "left_cheek":
            x_start = min_x
            x_end = min_x + face_width // 3
            y_start = min_y + face_height // 4
            y_end = min_y + face_height * 3 // 4
            cv2.rectangle(mask, (x_start, y_start), (x_end, y_end), 255, -1)
        elif region == "right_cheek":
            x_start = max_x - face_width // 3
            x_end = max_x
            y_start = min_y + face_height // 4
            y_end = min_y + face_height * 3 // 4
            cv2.rectangle(mask, (x_start, y_start), (x_end, y_end), 255, -1)
        elif region == "nose":
            x_start = min_x + face_width // 3
            x_end = max_x - face_width // 3
            y_start = min_y + face_height // 4
            y_end = min_y + face_height * 2 // 4
            cv2.rectangle(mask, (x_start, y_start), (x_end, y_end), 255, -1)
        elif region == "chin":
            y_start = max_y - face_height // 3
            y_end = max_y
            cv2.rectangle(mask, (min_x, y_start), (max_x, y_end), 255, -1)
        
        # Apply skin mask to only include skin areas
        mask = cv2.bitwise_and(mask, skin_mask)
        
        return mask
