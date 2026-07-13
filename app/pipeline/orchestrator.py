"""Pipeline Orchestrator"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

from app.analyzers.base import BaseAnalyzer
from app.analyzers.oiliness import OilinessAnalyzer
from app.analyzers.hydration import HydrationAnalyzer
from app.analyzers.skin_type import SkinTypeAnalyzer
from app.analyzers.redness import RednessAnalyzer
from app.analyzers.pigmentation import PigmentationAnalyzer
from app.analyzers.acne import AcneAnalyzer
from app.analyzers.wrinkles import WrinklesAnalyzer
from app.analyzers.pores import PoresAnalyzer
from app.analyzers.texture import TextureAnalyzer
from app.analyzers.skin_tone import SkinToneAnalyzer
from app.core.config import settings
from app.core.image_validator import ImageValidator
from app.models.face_detector import FaceDetector
from app.models.face_aligner import FaceAligner
from app.models.face_parser import FaceParser
from app.recommendations.engine import RecommendationEngine
from app.schemas.analysis import (
    AcneAnalysis,
    AcneSeverity,
    AnalysisResponse,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    SkinAnalysis,
    SkinType,
    WrinkleLevel
)


class PipelineOrchestrator:
    """
    Orchestrates the skin analysis pipeline.
    
    Coordinates the flow:
    1. Image validation
    2. Face detection
    3. Face alignment
    4. Face parsing
    5. Parallel analysis (oiliness, hydration, redness, pigmentation, acne, wrinkles, pores, texture)
    6. Feature aggregation
    7. Skin type determination
    8. Recommendation generation
    9. AI explanation
    """
    
    # Target processing times (ms)
    TARGET_FACE_DETECTION_MS = 100
    TARGET_FACE_PARSING_MS = 150
    TARGET_ANALYSIS_MS = 300
    TARGET_RECOMMENDATION_MS = 20
    
    def __init__(self):
        self.settings = settings
        self.image_validator = ImageValidator()
        self.face_detector = FaceDetector()
        self.face_aligner = FaceAligner(self.face_detector)
        self.face_parser = FaceParser(self.face_detector)
        self.recommendation_engine = RecommendationEngine()
        
        # Initialize analyzers
        self.analyzers = self._initialize_analyzers()
    
    def _initialize_analyzers(self) -> Dict[str, BaseAnalyzer]:
        """Initialize all skin analyzers"""
        return {
            "oiliness": OilinessAnalyzer(),
            "hydration": HydrationAnalyzer(),
            "skin_type": SkinTypeAnalyzer(),
            "redness": RednessAnalyzer(),
            "pigmentation": PigmentationAnalyzer(),
            "acne": AcneAnalyzer(),
            "wrinkles": WrinklesAnalyzer(),
            "pores": PoresAnalyzer(),
            "texture": TextureAnalyzer(),
            "skin_tone": SkinToneAnalyzer()
        }
    
    def analyze_image(self, image_bytes: bytes) -> AnalysisResponse:
        """
        Perform complete skin analysis on an image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            AnalysisResponse with complete results
        """
        start_time = time.time()
        
        # Step 1: Image validation
        validation_result = self.image_validator.validate_image(image_bytes)
        
        # Step 2: Load image
        image = self._load_image(image_bytes)
        
        # Step 3: Face detection
        face_detector_start = time.time()
        self.face_detector.detect_faces(image)
        face_detection_time = (time.time() - face_detector_start) * 1000
        
        # Step 4: Face alignment
        face_aligner_start = time.time()
        aligned_face, skin_mask = self.face_aligner.get_aligned_face_with_mask(image)
        alignment_time = (time.time() - face_aligner_start) * 1000
        
        # Step 5: Face parsing
        face_parser_start = time.time()
        regions = self.face_parser.parse_face(image)
        parsing_time = (time.time() - face_parser_start) * 1000
        
        # Step 6: Parallel analysis
        analysis_start = time.time()
        analysis_results = self._run_parallel_analysis(aligned_face, skin_mask, regions)
        analysis_time = (time.time() - analysis_start) * 1000
        
        # Step 7: Feature aggregation
        aggregation_start = time.time()
        aggregated_results = self._aggregate_results(analysis_results)
        aggregation_time = (time.time() - aggregation_start) * 1000
        
        # Step 8: Skin type determination
        skin_type = self.analyzers["skin_type"].analyze(
            aligned_face,
            skin_mask,
            regions,
            oiliness=aggregated_results["oiliness"],
            hydration=aggregated_results["hydration"]
        )
        
        # Step 9: Recommendation generation
        recommendation_start = time.time()
        recommendations = self.recommendation_engine.generate_recommendations(
            skin_type=skin_type,
            oiliness=aggregated_results["oiliness"],
            hydration=aggregated_results["hydration"],
            redness=aggregated_results["redness"],
            pigmentation=aggregated_results["pigmentation"],
            acne_severity=aggregated_results["acne"].severity,
            wrinkles=aggregated_results["wrinkles"],
            pores=aggregated_results["pores"],
            texture=aggregated_results.get("texture"),
            acne_count=aggregated_results["acne"].count
        )
        recommendation_time = (time.time() - recommendation_start) * 1000
        
        # Step 10: Calculate overall score
        overall_score = self._calculate_overall_score(aggregated_results)
        
        # Step 11: Create AI summary (for now, a simple summary)
        summary = self._generate_summary(
            skin_type=skin_type,
            oiliness=aggregated_results["oiliness"],
            hydration=aggregated_results["hydration"],
            redness=aggregated_results["redness"],
            pigmentation=aggregated_results["pigmentation"],
            acne=aggregated_results["acne"],
            wrinkles=aggregated_results["wrinkles"],
            pores=aggregated_results["pores"],
            texture=aggregated_results.get("texture"),
            skin_tone=aggregated_results.get("skin_tone")
        )
        
        # Step 12: Build response
        skin_analysis = SkinAnalysis(
            oiliness=aggregated_results["oiliness"],
            hydration=aggregated_results["hydration"],
            redness=aggregated_results["redness"],
            pigmentation=aggregated_results["pigmentation"],
            wrinkles=aggregated_results["wrinkles"],
            pores=aggregated_results["pores"],
            acne=aggregated_results["acne"],
            texture=aggregated_results.get("texture"),
            skin_tone=aggregated_results.get("skin_tone")
        )
        
        response = AnalysisResponse(
            overall_score=overall_score,
            skin_type=skin_type,
            analysis=skin_analysis,
            recommendations=recommendations,
            summary=summary,
            disclaimer="Educational information only. This analysis is not a medical diagnosis. "
                       "For personalized advice, please consult with a dermatologist."
        )
        
        total_time = (time.time() - start_time) * 1000
        
        # Log performance
        self._log_performance(
            total_time,
            face_detection_time,
            alignment_time,
            parsing_time,
            analysis_time,
            aggregation_time,
            recommendation_time
        )
        
        return response
    
    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        """Load image from bytes as RGB numpy array"""
        from PIL import Image
        from io import BytesIO
        
        image = Image.open(BytesIO(image_bytes))
        return np.array(image.convert("RGB"))
    
    def _run_parallel_analysis(
        self,
        aligned_face: np.ndarray,
        skin_mask: np.ndarray,
        regions: Dict[str, np.ndarray]
    ) -> Dict[str, any]:
        """
        Run all analyzers in parallel.
        
        Args:
            aligned_face: Aligned RGB face image
            skin_mask: Binary skin mask
            regions: Dictionary of region masks
            
        Returns:
            Dictionary of analysis results
        """
        results = {}
        
        # Define analysis tasks
        tasks = [
            ("oiliness", lambda: self.analyzers["oiliness"].analyze(aligned_face, skin_mask, regions)),
            ("hydration", lambda: self.analyzers["hydration"].analyze(aligned_face, skin_mask, regions)),
            ("redness", lambda: self.analyzers["redness"].analyze(aligned_face, skin_mask, regions)),
            ("pigmentation", lambda: self.analyzers["pigmentation"].analyze(aligned_face, skin_mask, regions)),
            ("acne", lambda: self.analyzers["acne"].analyze(aligned_face, skin_mask, regions)),
            ("wrinkles", lambda: self.analyzers["wrinkles"].analyze(aligned_face, skin_mask, regions)),
            ("pores", lambda: self.analyzers["pores"].analyze(aligned_face, skin_mask, regions)),
            ("texture", lambda: self.analyzers["texture"].analyze(aligned_face, skin_mask, regions)),
            ("skin_tone", lambda: self.analyzers["skin_tone"].analyze(aligned_face, skin_mask, regions))
        ]
        
        # Run tasks in parallel
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = {executor.submit(task[1]): task[0] for task in tasks}
            
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    results[task_name] = future.result()
                except Exception as e:
                    logger.error("Error in analyzer %s: %s", task_name, e)
                    # Set default values for failed analyzers
                    results[task_name] = self._get_default_result(task_name)
        
        return results
    
    def _get_default_result(self, analyzer_name: str) -> any:
        """Get default result for a failed analyzer"""
        defaults = {
            "oiliness": 50,
            "hydration": 50,
            "redness": RednessLevel.LOW,
            "pigmentation": PigmentationLevel.NONE,
            "acne": AcneAnalysis(severity=AcneSeverity.NONE, count=0),
            "wrinkles": WrinkleLevel.MINIMAL,
            "pores": PoreSize.MEDIUM,
            "texture": 50,
            "skin_tone": None
        }
        return defaults.get(analyzer_name, None)
    
    def _aggregate_results(self, results: Dict[str, any]) -> Dict[str, any]:
        """
        Aggregate and validate analysis results.
        
        Args:
            results: Raw analysis results
            
        Returns:
            Aggregated results with defaults for missing values
        """
        aggregated = {
            "oiliness": results.get("oiliness", 50),
            "hydration": results.get("hydration", 50),
            "redness": results.get("redness", RednessLevel.LOW),
            "pigmentation": results.get("pigmentation", PigmentationLevel.NONE),
            "acne": results.get("acne", AcneAnalysis(severity=AcneSeverity.NONE, count=0)),
            "wrinkles": results.get("wrinkles", WrinkleLevel.MINIMAL),
            "pores": results.get("pores", PoreSize.MEDIUM),
            "texture": results.get("texture", 50),
            "skin_tone": results.get("skin_tone", None)
        }
        
        # Ensure values are within valid ranges
        aggregated["oiliness"] = max(0, min(100, aggregated["oiliness"]))
        aggregated["hydration"] = max(0, min(100, aggregated["hydration"]))
        aggregated["texture"] = max(0, min(100, aggregated["texture"]))
        
        return aggregated
    
    def _calculate_overall_score(self, results: Dict[str, any]) -> int:
        """
        Calculate overall skin health score (0-100).
        
        Args:
            results: Aggregated analysis results
            
        Returns:
            Overall score
        """
        # Weighted combination of various factors
        # Higher oiliness and lower hydration reduce score
        # Skin concerns reduce score
        
        score = 100  # Start with perfect score
        
        # Oiliness: ideal around 50
        oiliness = results["oiliness"]
        oiliness_penalty = abs(oiliness - 50) * 0.5
        score -= oiliness_penalty
        
        # Hydration: ideal above 60
        hydration = results["hydration"]
        if hydration < 60:
            hydration_penalty = (60 - hydration) * 0.5
            score -= hydration_penalty
        
        # Redness penalty
        redness = results["redness"]
        if redness == RednessLevel.HIGH:
            score -= 15
        elif redness == RednessLevel.MODERATE:
            score -= 8
        
        # Pigmentation penalty
        pigmentation = results["pigmentation"]
        if pigmentation == PigmentationLevel.SEVERE:
            score -= 15
        elif pigmentation == PigmentationLevel.MODERATE:
            score -= 10
        elif pigmentation == PigmentationLevel.MILD:
            score -= 5
        
        # Acne penalty
        acne = results["acne"]
        if acne.severity == AcneSeverity.SEVERE:
            score -= 20
        elif acne.severity == AcneSeverity.MODERATE:
            score -= 12
        elif acne.severity == AcneSeverity.MILD:
            score -= 5
        
        # Wrinkles penalty
        wrinkles = results["wrinkles"]
        if wrinkles == WrinkleLevel.SEVERE:
            score -= 15
        elif wrinkles == WrinkleLevel.MODERATE:
            score -= 10
        elif wrinkles == WrinkleLevel.MILD:
            score -= 5
        
        # Texture bonus (higher is better)
        texture = results.get("texture", 50)
        if texture > 50:
            score += (texture - 50) * 0.2
        else:
            score -= (50 - texture) * 0.2
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        return int(round(score))
    
    def _generate_summary(
        self,
        skin_type: SkinType,
        oiliness: int,
        hydration: int,
        redness: RednessLevel,
        pigmentation: PigmentationLevel,
        acne: AcneAnalysis,
        wrinkles: WrinkleLevel,
        pores: PoreSize,
        texture: Optional[int],
        skin_tone: Optional[str]
    ) -> str:
        """
        Generate a human-readable summary of the analysis.
        
        Args:
            All analysis parameters
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Skin type
        summary_parts.append(f"Your skin type is {skin_type.value}.")
        
        # Oiliness
        if oiliness > 70:
            summary_parts.append("Your skin shows high oiliness.")
        elif oiliness < 30:
            summary_parts.append("Your skin shows low oiliness.")
        else:
            summary_parts.append("Your skin has balanced oil levels.")
        
        # Hydration
        if hydration < 40:
            summary_parts.append("Your skin appears dehydrated and could benefit from additional moisture.")
        elif hydration > 70:
            summary_parts.append("Your skin is well-hydrated.")
        else:
            summary_parts.append("Your skin hydration levels are adequate.")
        
        # Redness
        if redness != RednessLevel.LOW:
            summary_parts.append(f"There is {redness.value.lower()} redness detected in your skin.")
        
        # Pigmentation
        if pigmentation != PigmentationLevel.NONE:
            summary_parts.append(f"Your skin shows {pigmentation.value.lower()} pigmentation concerns.")
        
        # Acne
        if acne.severity != AcneSeverity.NONE:
            count_str = f" approximately {acne.count} lesions" if acne.count else ""
            summary_parts.append(f"Acne of {acne.severity.value.lower()} severity is detected{count_str}.")
        
        # Wrinkles
        if wrinkles != WrinkleLevel.MINIMAL:
            summary_parts.append(f"Your skin shows {wrinkles.value.lower()} wrinkles.")
        
        # Pores
        summary_parts.append(f"Your pores are {pores.value.lower()} in size.")
        
        # Texture
        if texture is not None:
            if texture > 70:
                summary_parts.append("Your skin texture is very smooth.")
            elif texture < 30:
                summary_parts.append("Your skin texture could be improved with proper care.")
            else:
                summary_parts.append("Your skin texture is within a normal range.")
        
        # Skin tone
        if skin_tone:
            summary_parts.append(f"Your skin tone is classified as {skin_tone}.")
        
        # Join all parts
        summary = " ".join(summary_parts)
        
        return summary
    
    def _log_performance(
        self,
        total_time: float,
        face_detection_time: float,
        alignment_time: float,
        parsing_time: float,
        analysis_time: float,
        aggregation_time: float,
        recommendation_time: float
    ):
        """Log performance metrics"""
        logger.info("Pipeline Performance: total=%.0fms, face=%.0fms, align=%.0fms, parse=%.0fms, "
                     "analysis=%.0fms, agg=%.0fms, rec=%.0fms, target=<%dms",
                     total_time, face_detection_time, alignment_time, parsing_time,
                     analysis_time, aggregation_time, recommendation_time,
                     self.settings.target_total_pipeline_ms)
