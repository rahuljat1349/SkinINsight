"""LangGraph State Definition"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
import numpy as np


class AnalysisState(TypedDict):
    """
    State that flows through the LangGraph pipeline.
    
    Each node only modifies the fields it owns.
    The state is passed between nodes and contains all
    intermediate results.
    """
    
    # Input
    image_bytes: Optional[bytes]
    user_info: Optional[Dict[str, str]]
    
    # Image processing
    image: Optional[np.ndarray]
    
    # Face detection
    face_metadata: Optional[Dict[str, Any]]
    
    # Face alignment
    aligned_face: Optional[np.ndarray]
    
    # Face parsing
    skin_mask: Optional[np.ndarray]
    regions: Optional[Dict[str, np.ndarray]]
    
    # Quality gate
    quality_check_passed: bool
    quality_errors: Optional[List[str]]
    quality_suggestions: Optional[List[str]]
    
    # Parallel analysis results
    analysis: Optional[Dict[str, Any]]
    
    # Aggregated results
    aggregated_analysis: Optional[Dict[str, Any]]
    skin_type: Optional[str]
    overall_score: Optional[int]
    
    # Recommendations
    recommendations: Optional[List[Dict[str, Any]]]
    
    # LLM explanation
    explanation: Optional[str]
    summary: Optional[str]
    interactions: Optional[List[Dict[str, Any]]]
    home_remedies: Optional[str]
    wishing_message: Optional[str]
    
    # Final response
    response: Optional[Dict[str, Any]]
    
    # Error handling
    errors: Optional[List[str]]
    current_error: Optional[str]
    is_error_state: bool


class ErrorState(TypedDict):
    """State for error handling"""
    errors: List[str]
    current_error: str
    is_error_state: bool


# Default state factory
def create_initial_state(
    image_bytes: Optional[bytes] = None,
    user_info: Optional[Dict[str, str]] = None
) -> AnalysisState:
    """Create initial state for the pipeline"""
    return AnalysisState(
        image_bytes=image_bytes,
        user_info=user_info or {},
        face_metadata=None,
        aligned_face=None,
        skin_mask=None,
        regions=None,
        quality_check_passed=False,
        quality_errors=[],
        quality_suggestions=[],
        analysis=None,
        aggregated_analysis=None,
        skin_type=None,
        overall_score=None,
        recommendations=None,
        explanation=None,
        summary=None,
        interactions=[],
        home_remedies=None,
        wishing_message=None,
        response=None,
        errors=[],
        current_error=None,
        is_error_state=False
    )
