"""Response Builder Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional

from app.graph.state import AnalysisState
from app.schemas.analysis import AnalysisResponse, SkinAnalysis, IngredientRecommendation, IngredientInteraction
from app.schemas.analysis import (
    AcneAnalysis,
    AcneSeverity,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    SkinType,
    WrinkleLevel
)


class ResponseBuilderNode:
    """
    Node that produces the final API response.
    
    Converts the state into a properly formatted AnalysisResponse.
    """
    
    def __init__(self):
        self.name = "response_builder"
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Build final API response"""
        aggregated = state.get("aggregated_analysis", {})
        skin_type = state.get("skin_type")
        recommendations = state.get("recommendations", [])
        summary = state.get("summary", "")
        explanation = state.get("explanation", "")
        interactions = state.get("interactions", [])
        home_remedies = state.get("home_remedies", "")
        wishing_message = state.get("wishing_message", "")
        overall_score = state.get("overall_score", 0)
        errors = state.get("errors", [])
        
        try:
            # Convert skin_type string to SkinType enum
            skin_type_enum = self._string_to_skin_type(skin_type) if skin_type else SkinType.NORMAL
            
            # Build SkinAnalysis object
            skin_analysis = SkinAnalysis(
                oiliness=aggregated.get("oiliness", 50),
                hydration=aggregated.get("hydration", 50),
                redness=aggregated.get("redness", RednessLevel.LOW),
                pigmentation=aggregated.get("pigmentation", PigmentationLevel.NONE),
                wrinkles=aggregated.get("wrinkles", WrinkleLevel.MINIMAL),
                pores=aggregated.get("pores", PoreSize.MEDIUM),
                acne=aggregated.get("acne", AcneAnalysis(severity=AcneSeverity.NONE, count=0)),
                texture=aggregated.get("texture", 50),
                skin_tone=aggregated.get("skin_tone", None)
            )
            
            # Convert recommendations to proper objects
            recommendation_objects = []
            for rec in recommendations:
                if isinstance(rec, dict):
                    recommendation_objects.append(IngredientRecommendation(
                        ingredient=rec.get("ingredient", ""),
                        priority=rec.get("priority", "Medium"),
                        reason=rec.get("reason", ""),
                        suggested_frequency=rec.get("suggested_frequency"),
                        usage_notes=rec.get("usage_notes"),
                        precautions=rec.get("precautions")
                    ))
                else:
                    recommendation_objects.append(rec)
            
            # Convert interactions to proper objects
            interaction_objects = []
            for interaction in interactions:
                if isinstance(interaction, dict):
                    interaction_objects.append(IngredientInteraction(
                        ingredients=interaction.get("ingredients", []),
                        reason=interaction.get("reason", ""),
                        suggestion=interaction.get("suggestion", "")
                    ))
            
            # Build response
            response = AnalysisResponse(
                overall_score=overall_score,
                skin_type=skin_type_enum,
                analysis=skin_analysis,
                recommendations=recommendation_objects,
                interactions=interaction_objects,
                summary=summary or explanation or "Analysis complete.",
                home_remedies=home_remedies or "",
                wishing_message=wishing_message or "",
                disclaimer="This analysis is AI-generated and may contain inaccuracies. "
                          "We celebrate the uniqueness of every individual — skin comes in all shades and types, "
                          "and there is no one-size-fits-all approach to skincare. "
                          "This information is for educational purposes only and is not a medical diagnosis. "
                          "Always consult with a qualified dermatologist for personalized advice."
            )
            
            new_state = state.copy()
            new_state["response"] = response.dict()
            new_state["errors"] = errors
            
            return new_state
            
        except Exception as e:
            error_msg = f"Response building failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = errors + [error_msg]
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
