"""Main LangGraph Pipeline for Skin Analysis"""

import logging
from typing import Any, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import cv2

logger = logging.getLogger(__name__)

from langgraph.graph import StateGraph as Graph, START, END

from app.graph.state import AnalysisState, create_initial_state
from app.graph.nodes.image_decoder import ImageDecoderNode
from app.graph.nodes.face_detector import FaceDetectorNode
from app.graph.nodes.face_validator import FaceValidatorNode
from app.graph.nodes.face_aligner import FaceAlignerNode
from app.graph.nodes.face_parser import FaceParserNode
from app.graph.nodes.quality_gate import QualityGateNode
from app.graph.nodes.aggregator import AggregatorNode
from app.graph.nodes.recommendation_node import RecommendationNode
from app.graph.nodes.explainer import ExplainerNode
from app.graph.nodes.response_builder import ResponseBuilderNode
from app.graph.nodes.error_handler import ErrorHandlerNode
from app.graph.nodes.direct_llm_node import DirectLLMNode
from app.core.config import settings


# Conditional edge functions
def check_error_and_continue(node_name: str) -> Callable[[AnalysisState], str]:
    """Factory for creating error check functions"""
    def check(state: AnalysisState) -> str:
        if state.get("is_error_state", False):
            return "error_handler"
        return node_name
    return check


def start_router(state: AnalysisState) -> str:
    """Route based on pipeline mode: false=CV, true=LLM, hybrid=CV+LLM"""
    mode = settings.send_image_to_llm
    if mode == "true":
        return "direct_llm"
    return "image_decoder"


def hybrid_router(state: AnalysisState) -> str:
    """After response_builder, run direct LLM if hybrid mode"""
    if settings.send_image_to_llm == "hybrid" and not state.get("is_error_state", False):
        return "direct_llm"
    return END


def check_quality_passed(state: AnalysisState) -> str:
    """Check if quality gate passed"""
    if state.get("is_error_state", False):
        return "error_handler"
    if not state.get("quality_check_passed", False):
        return "error_handler"
    return "parallel_analyzers"


def check_analysis_exists(state: AnalysisState) -> str:
    """Check if analysis results exist"""
    if state.get("is_error_state", False):
        return "error_handler"
    analysis = state.get("analysis", {})
    if not analysis:
        state["is_error_state"] = True
        state["current_error"] = "No analysis results available"
        return "error_handler"
    return "aggregator"


class LangGraphPipeline:
    """
    Main LangGraph pipeline for skin analysis.
    
    Implements the workflow from spec:
    
    START -> Decode Image -> Detect Face -> Validate Face ->
    Align Face -> Parse Face -> Quality Gate -> Parallel Analysis ->
    Aggregate Results -> Skin Type -> Recommendation Engine -> 
    LLM Explanation -> Response Builder -> END
    
    Error paths route to Error Handler -> END
    """
    
    def __init__(self):
        """Initialize the LangGraph pipeline"""
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow"""
        graph = Graph(AnalysisState)
        
        # Initialize all nodes
        # Sequential processing nodes
        graph.add_node("image_decoder", ImageDecoderNode())
        graph.add_node("face_detector", FaceDetectorNode())
        graph.add_node("face_validator", FaceValidatorNode())
        graph.add_node("face_aligner", FaceAlignerNode())
        graph.add_node("face_parser", FaceParserNode())
        graph.add_node("quality_gate", QualityGateNode())
        
        # Parallel analyzer node (custom implementation for parallel execution)
        graph.add_node("parallel_analyzers", self._run_parallel_analyzers)
        
        # Post-analysis nodes
        graph.add_node("aggregator", AggregatorNode())
        
        # Skin type determination (separate from parallel analyzers)
        from app.analyzers.skin_type import SkinTypeAnalyzer
        graph.add_node("skin_type_analyzer", self._create_skin_type_node(SkinTypeAnalyzer()))
        
        graph.add_node("recommendation_engine", RecommendationNode())
        graph.add_node("explainer", ExplainerNode())
        graph.add_node("response_builder", ResponseBuilderNode())
        graph.add_node("error_handler", ErrorHandlerNode())
        graph.add_node("direct_llm", DirectLLMNode())
        graph.add_node("hybrid_merger", self._hybrid_merger)
        
        # Define the workflow edges
        
        # START -> Direct LLM or Decode Image
        graph.add_conditional_edges(
            START,
            start_router,
            {"direct_llm": "direct_llm", "image_decoder": "image_decoder"}
        )
        
        # Direct LLM -> Response Builder (for pure LLM mode)
        graph.add_conditional_edges(
            "direct_llm",
            check_error_and_continue("response_builder"),
            {"response_builder": "response_builder", "error_handler": "error_handler"}
        )
        
        # Decode Image -> Detect Face
        graph.add_conditional_edges(
            "image_decoder",
            check_error_and_continue("face_detector"),
            {"face_detector": "face_detector", "error_handler": "error_handler"}
        )
        
        # Detect Face -> Validate Face
        graph.add_conditional_edges(
            "face_detector",
            check_error_and_continue("face_validator"),
            {"face_validator": "face_validator", "error_handler": "error_handler"}
        )
        
        # Validate Face -> Align Face (conditional)
        graph.add_conditional_edges(
            "face_validator",
            check_error_and_continue("face_aligner"),
            {"face_aligner": "face_aligner", "error_handler": "error_handler"}
        )
        
        # Align Face -> Parse Face
        graph.add_conditional_edges(
            "face_aligner",
            check_error_and_continue("face_parser"),
            {"face_parser": "face_parser", "error_handler": "error_handler"}
        )
        
        # Parse Face -> Quality Gate
        graph.add_conditional_edges(
            "face_parser",
            check_error_and_continue("quality_gate"),
            {"quality_gate": "quality_gate", "error_handler": "error_handler"}
        )
        
        # Quality Gate -> Parallel Analyzers (conditional on quality passing)
        graph.add_conditional_edges(
            "quality_gate",
            check_quality_passed,
            {"parallel_analyzers": "parallel_analyzers", "error_handler": "error_handler"}
        )
        
        # Parallel Analyzers -> Aggregator
        graph.add_conditional_edges(
            "parallel_analyzers",
            check_analysis_exists,
            {"aggregator": "aggregator", "error_handler": "error_handler"}
        )
        
        # Aggregator -> Skin Type Analyzer
        graph.add_conditional_edges(
            "aggregator",
            check_error_and_continue("skin_type_analyzer"),
            {"skin_type_analyzer": "skin_type_analyzer", "error_handler": "error_handler"}
        )
        
        # Skin Type Analyzer -> Recommendation Engine
        graph.add_conditional_edges(
            "skin_type_analyzer",
            check_error_and_continue("recommendation_engine"),
            {"recommendation_engine": "recommendation_engine", "error_handler": "error_handler"}
        )
        
        # Recommendation Engine -> Explainer
        graph.add_conditional_edges(
            "recommendation_engine",
            check_error_and_continue("explainer"),
            {"explainer": "explainer", "error_handler": "error_handler"}
        )
        
        # Explainer -> Response Builder
        graph.add_conditional_edges(
            "explainer",
            check_error_and_continue("response_builder"),
            {"response_builder": "response_builder", "error_handler": "error_handler"}
        )
        
        # Response Builder -> Hybrid Merger, Direct LLM, or END
        graph.add_conditional_edges(
            "response_builder",
            hybrid_router,
            {"direct_llm": "direct_llm", END: END}
        )
        
        # Hybrid Merger -> END
        graph.add_conditional_edges(
            "hybrid_merger",
            lambda state: "error_handler" if state.get("is_error_state", False) else END,
            {"error_handler": "error_handler", END: END}
        )
        
        # Error Handler -> END
        graph.add_edge("error_handler", END)
        
        return graph
    
    def _run_parallel_analyzers(self, state: AnalysisState) -> AnalysisState:
        """
        Execute all analyzer nodes in parallel.
        
        This node runs:
        - Oiliness Analyzer
        - Hydration Analyzer
        - Redness Analyzer
        - Pigmentation Analyzer
        - Acne Analyzer
        - Wrinkles Analyzer
        - Pores Analyzer
        - Texture Analyzer
        - Skin Tone Analyzer
        
        All analyzers receive:
        - aligned_face
        - skin_mask
        - regions
        """
        from app.analyzers.oiliness import OilinessAnalyzer
        from app.analyzers.hydration import HydrationAnalyzer
        from app.analyzers.redness import RednessAnalyzer
        from app.analyzers.pigmentation import PigmentationAnalyzer
        from app.analyzers.acne import AcneAnalyzer
        from app.analyzers.wrinkles import WrinklesAnalyzer
        from app.analyzers.pores import PoresAnalyzer
        from app.analyzers.texture import TextureAnalyzer
        from app.analyzers.skin_tone import SkinToneAnalyzer
        
        aligned_face = state.get("aligned_face")
        skin_mask = state.get("skin_mask")
        regions = state.get("regions")
        
        if aligned_face is None:
            new_state = state.copy()
            new_state["current_error"] = "No aligned face available for parallel analysis"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No aligned face for parallel analysis"]
            return new_state
        
        # Resize masks to match aligned_face dimensions
        target_h, target_w = aligned_face.shape[:2]
        if skin_mask is not None and skin_mask.shape[:2] != (target_h, target_w):
            skin_mask = cv2.resize(skin_mask, (target_w, target_h), interpolation=cv2.INTER_NEAREST)
        if regions:
            resized_regions = {}
            for name, mask in regions.items():
                if mask.shape[:2] != (target_h, target_w):
                    resized_regions[name] = cv2.resize(mask, (target_w, target_h), interpolation=cv2.INTER_NEAREST)
                else:
                    resized_regions[name] = mask
            regions = resized_regions
        
        try:
            # Initialize analyzers
            analyzer_map = {
                "oiliness": OilinessAnalyzer(),
                "hydration": HydrationAnalyzer(),
                "redness": RednessAnalyzer(),
                "pigmentation": PigmentationAnalyzer(),
                "acne": AcneAnalyzer(),
                "wrinkles": WrinklesAnalyzer(),
                "pores": PoresAnalyzer(),
                "texture": TextureAnalyzer(),
                "skin_tone": SkinToneAnalyzer()
            }
            
            # Run all analyzers in parallel
            results = {}
            with ThreadPoolExecutor(max_workers=len(analyzer_map)) as executor:
                # Submit all tasks
                futures = {}
                for name, analyzer in analyzer_map.items():
                    futures[executor.submit(analyzer.analyze, aligned_face, skin_mask, regions)] = name
                
                # Collect results
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        results[name] = future.result()
                    except Exception as e:
                        logger.error("Error in analyzer %s: %s", name, e)
                        results[name] = self._get_default_result(name)
            
            # Update state
            new_state = state.copy()
            new_state["analysis"] = results
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Parallel analysis failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
    
    def _create_skin_type_node(self, analyzer):
        """Create a skin type analyzer node"""
        from app.graph.state import AnalysisState
        
        class SkinTypeNode:
            def __init__(self):
                self.analyzer = analyzer
            
            def __call__(self, state: AnalysisState) -> AnalysisState:
                aligned_face = state.get("aligned_face")
                skin_mask = state.get("skin_mask")
                regions = state.get("regions")
                analysis = state.get("analysis", {})
                
                if aligned_face is None:
                    new_state = state.copy()
                    new_state["current_error"] = "No aligned face for skin type analysis"
                    new_state["is_error_state"] = True
                    new_state["errors"] = state.get("errors", []) + ["No aligned face for skin type"]
                    return new_state
                
                try:
                    oiliness = analysis.get("oiliness", 50)
                    hydration = analysis.get("hydration", 50)
                    
                    skin_type = self.analyzer.analyze(
                        aligned_face, skin_mask, regions,
                        oiliness=oiliness, hydration=hydration
                    )
                    
                    new_state = state.copy()
                    new_state["skin_type"] = skin_type.value if hasattr(skin_type, 'value') else str(skin_type)
                    new_state["errors"] = state.get("errors", [])
                    return new_state
                except Exception as e:
                    error_msg = f"Skin type analysis failed: {str(e)}"
                    new_state = state.copy()
                    new_state["current_error"] = error_msg
                    new_state["is_error_state"] = True
                    new_state["errors"] = state.get("errors", []) + [error_msg]
                    return new_state
        
        return SkinTypeNode()
    
    def _get_default_result(self, analyzer_name: str) -> Any:
        """Get default result for a failed analyzer"""
        from app.schemas.analysis import (
            AcneAnalysis, AcneSeverity, PigmentationLevel, 
            PoreSize, RednessLevel, WrinkleLevel
        )
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
    
    def _hybrid_merger(self, state: AnalysisState) -> AnalysisState:
        """Merge CV pipeline results with Direct LLM results for hybrid mode"""
        llm_summary = state.get("summary")
        llm_explanation = state.get("explanation")
        llm_home = state.get("home_remedies")
        llm_wishing = state.get("wishing_message")
        llm_recs = state.get("recommendations")
        llm_interactions = state.get("interactions")

        if not any([llm_summary, llm_explanation, llm_home, llm_wishing, llm_recs]):
            return state

        cv_response = state.get("response")
        if not cv_response:
            return state

        merged = dict(cv_response)
        if llm_summary:
            merged["summary"] = llm_summary
        if llm_explanation:
            merged["explanation"] = llm_explanation
        if llm_home:
            merged["home_remedies"] = llm_home
        if llm_wishing:
            merged["wishing_message"] = llm_wishing
        if llm_recs:
            merged["recommendations"] = llm_recs
        if llm_interactions:
            merged["interactions"] = llm_interactions

        new_state = state.copy()
        new_state["response"] = merged
        new_state["errors"] = state.get("errors", [])
        return new_state

    def analyze_image(
        self,
        image_bytes: bytes,
        user_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete skin analysis using LangGraph pipeline.
        
        Args:
            image_bytes: Raw image bytes from upload
            user_info: Optional user-provided info (age_group, skin_type_self, gender, sensitive_skin)
            
        Returns:
            Final response dictionary or error information
        """
        # Create initial state
        initial_state = create_initial_state(image_bytes, user_info=user_info)
        
        try:
            # Execute the graph
            final_state = self.app.invoke(initial_state)
            
            # Return response or error
            response = final_state.get("response")
            if response:
                return response
            
            # If there's an error, return error information
            error_info = {
                "error": {
                    "code": final_state.get("error_code", "unknown_error"),
                    "message": final_state.get("current_error", "An error occurred"),
                    "user_message": final_state.get("user_error_message", "An error occurred"),
                    "suggestion": final_state.get("error_suggestion", "Please try again"),
                    "errors": final_state.get("errors", [])
                },
                "success": False
            }
            return error_info
            
        except Exception as e:
            # Handle any exceptions from the graph execution
            return {
                "error": {
                    "code": "graph_execution_error",
                    "message": str(e),
                    "user_message": "An error occurred during analysis",
                    "suggestion": "Please try again with a different image",
                    "errors": [str(e)]
                },
                "success": False
            }


def create_analysis_graph() -> LangGraphPipeline:
    """
    Factory function to create the LangGraph pipeline.
    
    This is the main entry point for the LangGraph-based analysis.
    """
    return LangGraphPipeline()
