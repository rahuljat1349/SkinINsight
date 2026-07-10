"""Edge Conditions for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
from langgraph.graph import END

from app.graph.state import AnalysisState


def should_continue_after_validation(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue after face validation.
    
    Returns:
    - "face_aligner" if validation passed
    - "error_handler" if validation failed
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "face_aligner"


def should_continue_after_quality_gate(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue after quality gate.
    
    Returns:
    - "face_parser" if quality check passed
    - "error_handler" if quality check failed
    """
    if state.get("is_error_state", False):
        return "error_handler"
    if not state.get("quality_check_passed", False):
        return "error_handler"
    return "face_parser"


def should_continue_after_face_parsing(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue after face parsing.
    
    Returns:
    - "quality_gate" if face parsing succeeded
    - "error_handler" if face parsing failed
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "quality_gate"


def should_continue_to_analysis(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue to parallel analysis.
    
    Returns:
    - "parallel_analyzers" if all previous steps succeeded
    - "error_handler" if any step failed
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "parallel_analyzers"


def should_continue_to_aggregator(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue to aggregator.
    
    Returns:
    - "aggregator" if analysis has results
    - "error_handler" if analysis failed
    """
    if state.get("is_error_state", False):
        return "error_handler"
    
    analysis = state.get("analysis", {})
    if not analysis:
        state["is_error_state"] = True
        state["current_error"] = "No analysis results available"
        return "error_handler"
    
    return "aggregator"


def should_continue_to_skin_type(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue to skin type analysis.
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "skin_type_analyzer"


def should_continue_to_recommendations(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue to recommendation engine.
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "recommendation_engine"


def should_continue_to_explainer(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue to LLM explainer.
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "explainer"


def should_continue_to_response_builder(state: AnalysisState) -> str:
    """
    Determine if pipeline should continue to response builder.
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return "response_builder"


def should_end_after_response(state: AnalysisState) -> str:
    """
    Determine if pipeline should end after response building.
    """
    if state.get("is_error_state", False):
        return "error_handler"
    return END


def should_end_after_error_handler(state: AnalysisState) -> str:
    """
    Always end after error handler.
    """
    return END
