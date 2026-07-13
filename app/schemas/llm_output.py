"""LLM Structured Output Schema"""

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.analysis import (
    AcneAnalysis,
    IngredientInteraction,
    IngredientRecommendation,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    SkinType,
    WrinkleLevel,
)


class LLMOutput(BaseModel):
    """Structured output from the LLM"""

    overall_score: int = Field(ge=0, le=100, description="Overall skin health score (0-100)")
    skin_type: SkinType = Field(description="Determined skin type")
    oiliness: int = Field(ge=0, le=100, description="Oiliness score (0-100, higher = more oily)")
    hydration: int = Field(ge=0, le=100, description="Hydration score (0-100, higher = more hydrated)")
    redness: RednessLevel = Field(description="Redness severity level")
    pigmentation: PigmentationLevel = Field(description="Pigmentation severity level")
    wrinkles: WrinkleLevel = Field(description="Wrinkle severity level")
    pores: PoreSize = Field(description="Pore size category")
    acne: AcneAnalysis = Field(description="Acne severity and count")
    texture: Optional[int] = Field(default=None, ge=0, le=100, description="Texture smoothness score")
    skin_tone: Optional[str] = Field(default=None, description="Skin tone description")

    explanation: str = Field(description="Natural-language explanation of the analysis")
    summary: str = Field(description="Concise summary of findings")
    recommendations: list[IngredientRecommendation] = Field(
        description="Personalized skincare ingredient recommendations"
    )
    interactions: list[IngredientInteraction] = Field(
        default=[],
        description="Ingredient interactions to be mindful of"
    )
    home_remedies: str = Field(default="", description="Suggested natural home remedies")
    wishing_message: str = Field(default="", description="Friendly closing message")
