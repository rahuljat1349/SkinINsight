"""LangGraph-based Pipeline Orchestrator"""

import time
from typing import Any, Dict, Optional
import numpy as np

from app.graph.graph import LangGraphPipeline, create_analysis_graph
from app.schemas.analysis import AnalysisResponse
from app.core.exceptions import (
    NoFaceDetectedError,
    MultipleFacesError,
    FaceTooSmallError,
    PoorLightingError,
    ExcessiveBlurError,
    UnsupportedFormatError,
    ImageTooLargeError,
    LowResolutionError,
    InternalInferenceError
)


class LangGraphPipelineOrchestrator:
    """
    Orchestrates the skin analysis pipeline using LangGraph.
    
    This is the v2.0 implementation that uses LangGraph as the workflow engine.
    
    Workflow:
    1. Decode Image
    2. Detect Face
    3. Validate Face
    4. Align Face
    5. Parse Face
    6. Quality Gate
    7. Parallel Analysis (9 analyzers)
    8. Aggregate Results
    9. Skin Type Determination
    10. Recommendation Generation
    11. LLM Explanation
    12. Response Building
    
    Each node has exactly one responsibility.
    Nodes never decide which node executes next except through predefined conditional edges.
    Business logic lives outside the graph.
    """
    
    # Performance targets (ms)
    TARGET_DECODE_MS = 20
    TARGET_FACE_DETECTION_MS = 80
    TARGET_ALIGNMENT_MS = 20
    TARGET_PARSING_MS = 150
    TARGET_ANALYSIS_MS = 300
    TARGET_RECOMMENDATION_MS = 10
    TARGET_RESPONSE_MS = 10
    TARGET_TOTAL_MS = 700  # Excluding LLM
    
    def __init__(self):
        """Initialize the LangGraph-based pipeline orchestrator"""
        self.pipeline = create_analysis_graph()
    
    def analyze_image(
        self,
        image_bytes: bytes,
        user_info: Optional[Dict[str, str]] = None
    ) -> AnalysisResponse:
        """
        Perform complete skin analysis using LangGraph pipeline.
        
        Args:
            image_bytes: Raw image bytes from upload
            user_info: Optional user-provided info (age_group, skin_type_self, gender, sensitive_skin)
            
        Returns:
            AnalysisResponse with complete results
            
        Raises:
            Various skin analysis exceptions on failure
        """
        start_time = time.time()
        
        try:
            # Execute the LangGraph pipeline
            result = self.pipeline.analyze_image(image_bytes, user_info=user_info)
            
            # Check for errors in result
            if isinstance(result, dict) and result.get("error"):
                self._handle_pipeline_error(result)
            
            # Convert result to AnalysisResponse
            if isinstance(result, dict):
                response = AnalysisResponse(**result)
            else:
                response = result
            
            # Log performance
            total_time = (time.time() - start_time) * 1000
            self._log_performance(total_time)
            
            return response
            
        except NoFaceDetectedError:
            raise
        except MultipleFacesError:
            raise
        except FaceTooSmallError:
            raise
        except PoorLightingError:
            raise
        except ExcessiveBlurError:
            raise
        except UnsupportedFormatError:
            raise
        except ImageTooLargeError:
            raise
        except LowResolutionError:
            raise
        except Exception as e:
            raise InternalInferenceError(str(e))
    
    def _handle_pipeline_error(self, result: Dict[str, Any]) -> None:
        """Handle pipeline errors by raising appropriate exceptions"""
        error_info = result.get("error", {})
        error_code = error_info.get("code", "unknown")
        error_message = error_info.get("message", "An error occurred")
        user_message = error_info.get("user_message", "Please try again")

        # Map error codes to exceptions (they take no args, use defaults)
        error_mapping = {
            "no_face_detected": NoFaceDetectedError,
            "multiple_faces_detected": MultipleFacesError,
            "face_too_small": FaceTooSmallError,
            "poor_lighting": PoorLightingError,
            "excessive_blur": ExcessiveBlurError,
            "unsupported_image_format": UnsupportedFormatError,
            "image_too_large": ImageTooLargeError,
            "low_resolution": LowResolutionError
        }

        exception_class = error_mapping.get(error_code)
        if exception_class:
            raise exception_class()
        raise InternalInferenceError(f"{error_code}: {error_message}")
    
    def _log_performance(self, total_time: float) -> None:
        """Log performance metrics"""
        print(f"LangGraph Pipeline Performance:")
        print(f"  Total: {total_time:.2f} ms")
        print(f"  Target: <{self.TARGET_TOTAL_MS} ms (excluding LLM)")
        
        if total_time > self.TARGET_TOTAL_MS:
            print(f"  WARNING: Total time exceeds target by {total_time - self.TARGET_TOTAL_MS:.2f} ms")


# Singleton instance
pipeline = LangGraphPipelineOrchestrator()


# For backwards compatibility, also export the pipeline directly
langgraph_pipeline = pipeline
