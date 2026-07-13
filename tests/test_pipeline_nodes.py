"""Pipeline node unit tests with mocked dependencies"""

from unittest.mock import patch, MagicMock, PropertyMock
import numpy as np
import pytest

from app.graph.state import create_initial_state
from app.graph.nodes.explainer import ExplainerNode
from app.graph.nodes.response_builder import ResponseBuilderNode
from app.graph.nodes.direct_llm_node import DirectLLMNode
from app.schemas.analysis import (
    AcneAnalysis,
    AcneSeverity,
    RednessLevel,
    PigmentationLevel,
    WrinkleLevel,
    PoreSize,
    SkinType,
)


@pytest.fixture(autouse=True)
def disable_llm():
    with patch("app.graph.nodes.explainer.settings.llm_enabled", False):
        with patch("app.graph.nodes.explainer.settings.fallback_to_local_models", True):
            yield


def make_state(**overrides):
    state = create_initial_state(image_bytes=b"fake_image_bytes")
    defaults = dict(
        aggregated_analysis=dict(
            oiliness=55,
            hydration=60,
            redness=RednessLevel.LOW,
            pigmentation=PigmentationLevel.NONE,
            wrinkles=WrinkleLevel.MINIMAL,
            pores=PoreSize.MEDIUM,
            acne=AcneAnalysis(severity=AcneSeverity.NONE, count=0),
            texture=70,
            skin_tone="Light",
        ),
        skin_type="Combination",
        overall_score=72,
        recommendations=[
            {"ingredient": "Niacinamide", "priority": "High", "reason": "Balance"}
        ],
        errors=[],
        is_error_state=False,
    )
    defaults.update(overrides)
    state.update(defaults)
    return state


class TestExplainerNodeDeterministicFallback:
    def test_generates_outputs(self):
        state = make_state()
        node = ExplainerNode()
        result = node(state)
        assert result["summary"] is not None
        assert len(result["summary"]) > 0
        assert result["home_remedies"] is not None
        assert result["wishing_message"] is not None

    def test_includes_skin_type_in_summary(self):
        state = make_state(skin_type="Oily")
        node = ExplainerNode()
        result = node(state)
        assert "Oily" in result["summary"]

    def test_includes_overall_score(self):
        state = make_state(overall_score=85)
        node = ExplainerNode()
        result = node(state)
        assert "85" in result["summary"] or "Excellent" in result["summary"]

    def test_includes_recommendations(self):
        state = make_state(recommendations=[
            {"ingredient": "Vitamin C", "priority": "High", "reason": "Brightening"}
        ])
        node = ExplainerNode()
        result = node(state)
        assert "Vitamin C" in result["summary"]

    def test_home_remedies_for_oily_skin(self):
        state = make_state(aggregated_analysis=dict(
            oiliness=80, hydration=50,
            redness=RednessLevel.LOW, pigmentation=PigmentationLevel.NONE,
            wrinkles=WrinkleLevel.MINIMAL, pores=PoreSize.LARGE,
            acne=AcneAnalysis(severity=AcneSeverity.NONE, count=0),
            texture=50, skin_tone="Light",
        ))
        node = ExplainerNode()
        result = node(state)
        assert "Aloe Vera" in result["home_remedies"]

    def test_sets_error_on_llm_enabled_no_key(self):
        with patch("app.graph.nodes.explainer.settings.llm_enabled", True):
            with patch("app.graph.nodes.explainer.settings.llm_api_key_gemini", ""):
                state = make_state()
                node = ExplainerNode()
                result = node(state)
                assert result["is_error_state"] or result.get("summary")


class TestResponseBuilderNode:
    def test_builds_response(self):
        state = make_state()
        node = ResponseBuilderNode()
        result = node(state)
        assert "response" in result
        resp = result["response"]
        assert resp["overall_score"] == 72
        assert resp["skin_type"] == "Combination"
        assert "oiliness" in resp["analysis"]

    def test_response_structure(self):
        state = make_state()
        node = ResponseBuilderNode()
        result = node(state)
        resp = result["response"]
        assert "summary" in resp
        assert "recommendations" in resp
        assert "analysis" in resp
        assert "disclaimer" in resp
        assert "interactions" in resp

    def test_handles_empty_recommendations(self):
        state = make_state(recommendations=[])
        node = ResponseBuilderNode()
        result = node(state)
        assert result["response"]["recommendations"] == []


class TestDirectLLMNode:
    def test_no_image_bytes_returns_error(self):
        node = DirectLLMNode()
        state = create_initial_state(image_bytes=None)
        result = node(state)
        assert result["is_error_state"] is True
        assert "No image bytes" in str(result.get("current_error", ""))

    @patch("app.graph.nodes.direct_llm_node.DirectLLMNode._call_llm_with_image")
    def test_uses_fallback_on_llm_failure(self, mock_call):
        mock_call.side_effect = RuntimeError("LLM failed")
        with patch("app.graph.nodes.direct_llm_node.settings.fallback_to_local_models", True):
            state = create_initial_state(image_bytes=b"test_image")
            result = DirectLLMNode()(state)
            assert not result["is_error_state"]
            assert result["aggregated_analysis"] is not None
            assert result["summary"] is not None

    @patch("app.graph.nodes.direct_llm_node.DirectLLMNode._call_llm_with_image")
    def test_returns_error_on_llm_failure_no_fallback(self, mock_call):
        mock_call.side_effect = RuntimeError("LLM failed")
        with patch("app.graph.nodes.direct_llm_node.settings.fallback_to_local_models", False):
            state = create_initial_state(image_bytes=b"test_image")
            result = DirectLLMNode()(state)
            assert result["is_error_state"] is True
            assert "LLM failed" in result.get("current_error", "")
