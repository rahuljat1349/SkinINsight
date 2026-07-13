"""Schema validation tests"""

from pydantic import ValidationError
import pytest

from app.schemas.analysis import (
    AnalysisResponse,
    SkinAnalysis,
    SkinType,
    RednessLevel,
    PigmentationLevel,
    WrinkleLevel,
    PoreSize,
    AcneSeverity,
    AcneAnalysis,
    IngredientRecommendation,
    IngredientInteraction,
)
from app.schemas.llm_output import LLMOutput


def make_valid_acne():
    return AcneAnalysis(severity=AcneSeverity.NONE, count=0)


def make_valid_skin_analysis(**overrides):
    data = dict(
        oiliness=50,
        hydration=60,
        redness=RednessLevel.LOW,
        pigmentation=PigmentationLevel.NONE,
        wrinkles=WrinkleLevel.MINIMAL,
        pores=PoreSize.MEDIUM,
        acne=make_valid_acne(),
        texture=70,
        skin_tone="Light",
    )
    data.update(overrides)
    return SkinAnalysis(**data)


class TestSkinAnalysis:
    def test_valid_minimal(self):
        sa = SkinAnalysis(
            oiliness=30,
            hydration=70,
            redness=RednessLevel.LOW,
            pigmentation=PigmentationLevel.NONE,
            wrinkles=WrinkleLevel.MINIMAL,
            pores=PoreSize.MEDIUM,
            acne=make_valid_acne(),
        )
        assert sa.oiliness == 30

    def test_oiliness_out_of_range(self):
        with pytest.raises(ValidationError):
            SkinAnalysis(
                oiliness=150, hydration=50,
                redness=RednessLevel.LOW, pigmentation=PigmentationLevel.NONE,
                wrinkles=WrinkleLevel.MINIMAL, pores=PoreSize.MEDIUM,
                acne=make_valid_acne(),
            )

    def test_hydration_out_of_range(self):
        with pytest.raises(ValidationError):
            SkinAnalysis(
                oiliness=50, hydration=-10,
                redness=RednessLevel.LOW, pigmentation=PigmentationLevel.NONE,
                wrinkles=WrinkleLevel.MINIMAL, pores=PoreSize.MEDIUM,
                acne=make_valid_acne(),
            )

    def test_all_fields(self):
        sa = make_valid_skin_analysis(oiliness=80, hydration=20, texture=90, skin_tone="Olive")
        assert sa.oiliness == 80
        assert sa.hydration == 20
        assert sa.texture == 90
        assert sa.skin_tone == "Olive"


class TestAnalysisResponse:
    def test_valid_full(self):
        resp = AnalysisResponse(
            overall_score=72,
            skin_type=SkinType.COMBINATION,
            analysis=make_valid_skin_analysis(),
            recommendations=[
                IngredientRecommendation(
                    ingredient="Niacinamide",
                    priority="High",
                    reason="Balances oil production",
                )
            ],
            interactions=[
                IngredientInteraction(
                    ingredients=["Vitamin C", "Retinol"],
                    reason="May cause irritation",
                    suggestion="Use at different times of day",
                )
            ],
            summary="Good skin health.",
            home_remedies="Try aloe vera.",
            wishing_message="Take care!",
        )
        assert resp.overall_score == 72
        assert resp.skin_type == SkinType.COMBINATION
        assert len(resp.recommendations) == 1
        assert len(resp.interactions) == 1
        assert resp.home_remedies == "Try aloe vera."

    def test_score_out_of_range(self):
        with pytest.raises(ValidationError):
            AnalysisResponse(
                overall_score=101,
                skin_type=SkinType.NORMAL,
                analysis=make_valid_skin_analysis(),
                recommendations=[],
                summary="Test",
            )

    def test_minimal_defaults(self):
        resp = AnalysisResponse(
            overall_score=50,
            skin_type=SkinType.OILY,
            analysis=make_valid_skin_analysis(),
            recommendations=[],
            summary="Test",
        )
        assert resp.home_remedies == ""
        assert resp.wishing_message == ""
        assert resp.interactions == []
        assert resp.disclaimer


class TestIngredientRecommendation:
    def test_minimal(self):
        rec = IngredientRecommendation(
            ingredient="Vitamin C",
            priority="High",
            reason="Antioxidant",
        )
        assert rec.ingredient == "Vitamin C"

    def test_full(self):
        rec = IngredientRecommendation(
            ingredient="Retinol",
            priority="Medium",
            reason="Anti-aging",
            suggested_frequency="3x/week",
            usage_notes="Apply at night",
            precautions="Use sunscreen",
        )
        assert rec.suggested_frequency == "3x/week"
        assert rec.precautions == "Use sunscreen"


class TestIngredientInteraction:
    def test_minimal(self):
        inter = IngredientInteraction(
            ingredients=["A", "B"],
            reason="Reacts badly",
            suggestion="Don't mix",
        )
        assert inter.ingredients == ["A", "B"]


class TestLLMOutput:
    def test_valid(self):
        out = LLMOutput(
            overall_score=70,
            skin_type=SkinType.DRY,
            oiliness=30,
            hydration=40,
            redness=RednessLevel.MODERATE,
            pigmentation=PigmentationLevel.MILD,
            wrinkles=WrinkleLevel.MILD,
            pores=PoreSize.MEDIUM,
            acne=make_valid_acne(),
            explanation="Test explanation",
            summary="Test summary",
            recommendations=[
                IngredientRecommendation(
                    ingredient="Hyaluronic Acid",
                    priority="High",
                    reason="Hydration",
                )
            ],
        )
        assert out.overall_score == 70
        assert out.skin_type == SkinType.DRY
        assert out.oiliness == 30

    def test_optional_fields_default(self):
        out = LLMOutput(
            overall_score=50,
            skin_type=SkinType.NORMAL,
            oiliness=50,
            hydration=50,
            redness=RednessLevel.LOW,
            pigmentation=PigmentationLevel.NONE,
            wrinkles=WrinkleLevel.MINIMAL,
            pores=PoreSize.MEDIUM,
            acne=make_valid_acne(),
            explanation="",
            summary="",
            recommendations=[],
        )
        assert out.texture is None
        assert out.skin_tone is None
        assert out.home_remedies == ""
        assert out.wishing_message == ""
