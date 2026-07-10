"""Aggregator Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
import numpy as np

from app.graph.state import AnalysisState
from app.schemas.analysis import (
    AcneAnalysis,
    AcneSeverity,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    WrinkleLevel
)


class AggregatorNode:
    """
    Node that aggregates individual analyzer results into a structured analysis object.
    
    Responsibilities:
    - Merge analyzer outputs
    - Validate and set defaults
    - Calculate overall score
    """
    
    def __init__(self):
        self.name = "aggregator"
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Aggregate analysis results"""
        analysis = state.get("analysis", {})
        skin_type = state.get("skin_type")
        
        if not analysis:
            new_state = state.copy()
            new_state["current_error"] = "No analysis results to aggregate"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No analysis results to aggregate"]
            return new_state
        
        try:
            # Aggregate results with defaults
            aggregated = self._aggregate_results(analysis)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(aggregated)
            
            # Update state
            new_state = state.copy()
            new_state["aggregated_analysis"] = aggregated
            new_state["skin_type"] = skin_type if skin_type else aggregated.get("skin_type")
            new_state["overall_score"] = overall_score
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Aggregation failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate and validate analysis results"""
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
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall skin health score (0-100)"""
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
