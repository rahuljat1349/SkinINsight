"""Recommendation Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional

from app.graph.state import AnalysisState
from app.recommendations.engine import RecommendationEngine
from app.schemas.analysis import (
    AcneSeverity,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    SkinType,
    WrinkleLevel
)


class RecommendationNode:
    """
    Node that generates deterministic skincare recommendations.
    
    Pure deterministic rules - no LLM used here.
    
    Input:
    - Aggregated analysis results
    - Skin type
    
    Output:
    - List of ingredient recommendations
    """
    
    def __init__(self):
        self.name = "recommendation_engine"
        self.engine = RecommendationEngine()
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Generate recommendations"""
        aggregated = state.get("aggregated_analysis", {})
        skin_type = state.get("skin_type")
        
        if not aggregated:
            new_state = state.copy()
            new_state["current_error"] = "No aggregated analysis results for recommendations"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No analysis results for recommendations"]
            return new_state
        
        try:
            # Convert skin_type string to SkinType enum if needed
            if isinstance(skin_type, str):
                skin_type_enum = self._string_to_skin_type(skin_type)
            else:
                skin_type_enum = skin_type
            
            # Generate recommendations
            acne = aggregated.get("acne")
            acne_severity = acne.severity if hasattr(acne, "severity") else AcneSeverity.NONE
            acne_count = acne.count if hasattr(acne, "count") else None

            recommendations = self.engine.generate_recommendations(
                skin_type=skin_type_enum,
                oiliness=aggregated.get("oiliness", 50),
                hydration=aggregated.get("hydration", 50),
                redness=aggregated.get("redness", RednessLevel.LOW),
                pigmentation=aggregated.get("pigmentation", PigmentationLevel.NONE),
                acne_severity=acne_severity,
                wrinkles=aggregated.get("wrinkles", WrinkleLevel.MINIMAL),
                pores=aggregated.get("pores", PoreSize.MEDIUM),
                texture=aggregated.get("texture"),
                acne_count=acne_count
            )
            
            # Convert recommendations to dict format for state
            recommendations_list = []
            for rec in recommendations:
                recommendations_list.append({
                    "ingredient": rec.ingredient,
                    "priority": rec.priority,
                    "reason": rec.reason,
                    "suggested_frequency": rec.suggested_frequency,
                    "usage_notes": rec.usage_notes,
                    "precautions": rec.precautions
                })
            
            new_state = state.copy()
            new_state["recommendations"] = recommendations_list
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Recommendation generation failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
    
    def _string_to_skin_type(self, skin_type_str: str) -> SkinType:
        """Convert string to SkinType enum"""
        mapping = {
            "Oily": SkinType.OILY,
            "Dry": SkinType.DRY,
            "Combination": SkinType.COMBINATION,
            "Normal": SkinType.NORMAL
        }
        return mapping.get(skin_type_str, SkinType.NORMAL)
