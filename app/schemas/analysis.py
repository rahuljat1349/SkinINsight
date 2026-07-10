"""Analysis Result Schemas"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SkinType(str, Enum):
    """Possible skin types"""
    OILY = "Oily"
    DRY = "Dry"
    COMBINATION = "Combination"
    NORMAL = "Normal"


class SeverityLevel(str, Enum):
    """Severity levels for various skin conditions"""
    NONE = "None"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


class RednessLevel(str, Enum):
    """Redness severity levels"""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class PoreSize(str, Enum):
    """Pore size categories"""
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class WrinkleLevel(str, Enum):
    """Wrinkle severity levels"""
    MINIMAL = "Minimal"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


class PigmentationLevel(str, Enum):
    """Pigmentation severity levels"""
    NONE = "None"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


class AcneSeverity(str, Enum):
    """Acne severity levels"""
    NONE = "None"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"


class AcneAnalysis(BaseModel):
    """Acne analysis result"""
    severity: AcneSeverity
    count: Optional[int] = Field(default=None, ge=0, description="Estimated lesion count")


class SkinAnalysis(BaseModel):
    """Complete skin analysis results"""
    oiliness: int = Field(ge=0, le=100, description="Oiliness score (0-100)")
    hydration: int = Field(ge=0, le=100, description="Hydration score (0-100)")
    redness: RednessLevel
    pigmentation: PigmentationLevel
    wrinkles: WrinkleLevel
    pores: PoreSize
    acne: AcneAnalysis
    texture: Optional[int] = Field(default=None, ge=0, le=100, description="Smoothness score")
    skin_tone: Optional[str] = Field(default=None, description="Skin tone for educational purposes")


class IngredientRecommendation(BaseModel):
    """Recommendation for a skincare ingredient"""
    ingredient: str
    priority: str  # High, Medium, Low
    reason: str
    suggested_frequency: Optional[str] = None
    usage_notes: Optional[str] = None
    precautions: Optional[str] = None


class IngredientInteraction(BaseModel):
    """Warning about incompatible ingredient combinations"""
    ingredients: list[str] = Field(description="The pair of ingredients that should not be used together")
    reason: str = Field(description="Why they shouldn't be combined")
    suggestion: str = Field(description="How to use them safely (e.g. alternate AM/PM)")


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    overall_score: int = Field(ge=0, le=100, description="Overall skin health score")
    skin_type: SkinType
    analysis: SkinAnalysis
    recommendations: list[IngredientRecommendation]
    interactions: list[IngredientInteraction] = Field(
        default=[],
        description="Ingredient combinations to avoid or use carefully"
    )
    summary: str = Field(description="AI-generated summary of findings")
    home_remedies: str = Field(default="", description="AI-suggested home remedies")
    wishing_message: str = Field(default="", description="Friendly closing message")
    disclaimer: str = Field(
        default="Educational information only. This analysis is not a medical diagnosis.",
        description="Safety disclaimer"
    )
