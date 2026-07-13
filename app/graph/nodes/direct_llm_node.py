"""Direct-to-LLM Analysis Node — sends raw image to Gemini for full structured output"""

from typing import Any, Dict, Optional
import base64
import concurrent.futures

from app.graph.state import AnalysisState
from app.core.config import settings
from app.schemas.llm_output import LLMOutput
from app.schemas.analysis import (
    AcneAnalysis,
    AcneSeverity,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    WrinkleLevel,
    SkinType,
)


def _encode_image(image_bytes: bytes) -> str:
    from io import BytesIO
    from PIL import Image
    img = Image.open(BytesIO(image_bytes))
    if img.mode == "RGBA":
        img = img.convert("RGB")
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def _default_acne() -> dict:
    return AcneAnalysis(severity=AcneSeverity.NONE, count=0).model_dump()


class DirectLLMNode:
    """
    Sends the raw image directly to Gemini with a structured-output schema.
    Bypasses all CV nodes — the LLM handles both analysis and explanation.
    """

    FALLBACK_NOTE = (
        "**Educational Note:** Our AI was unable to analyze your image at this time. "
        "Default scores are shown below as a reference. "
        "Please try again later or consult a dermatologist for a professional assessment."
    )

    def __init__(self):
        self.name = "direct_llm"
        self.fallback_enabled = settings.fallback_to_local_models

    def __call__(self, state: AnalysisState) -> AnalysisState:
        image_bytes = state.get("image_bytes")
        if not image_bytes:
            new_state = state.copy()
            new_state["current_error"] = "No image bytes available"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No image bytes"]
            return new_state

        user_info = state.get("user_info", {})

        try:
            result = self._call_llm_with_image(image_bytes, user_info)
        except Exception as e:
            if self.fallback_enabled:
                return self._fallback_state(state)
            error_msg = f"Direct LLM analysis failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state

        aggregated = {
            "oiliness": result.oiliness,
            "hydration": result.hydration,
            "redness": result.redness.value if hasattr(result.redness, "value") else result.redness,
            "pigmentation": result.pigmentation.value if hasattr(result.pigmentation, "value") else result.pigmentation,
            "wrinkles": result.wrinkles.value if hasattr(result.wrinkles, "value") else result.wrinkles,
            "pores": result.pores.value if hasattr(result.pores, "value") else result.pores,
            "acne": result.acne.model_dump() if hasattr(result.acne, "model_dump") else _default_acne(),
            "texture": result.texture or 50,
            "skin_tone": result.skin_tone or None,
        }

        recs = [r.model_dump() for r in (result.recommendations or [])]
        interactions = [i.model_dump() for i in (result.interactions or [])]

        new_state = state.copy()
        new_state["aggregated_analysis"] = aggregated
        new_state["skin_type"] = result.skin_type.value if hasattr(result.skin_type, "value") else str(result.skin_type)
        new_state["overall_score"] = result.overall_score
        new_state["recommendations"] = recs
        new_state["explanation"] = result.explanation or result.summary
        new_state["summary"] = result.summary or result.explanation
        new_state["interactions"] = interactions
        new_state["home_remedies"] = result.home_remedies or ""
        new_state["wishing_message"] = result.wishing_message or ""
        new_state["errors"] = state.get("errors", [])
        return new_state

    def _fallback_state(self, state: AnalysisState) -> AnalysisState:
        agg = {
            "oiliness": 50,
            "hydration": 50,
            "redness": RednessLevel.LOW,
            "pigmentation": PigmentationLevel.NONE,
            "wrinkles": WrinkleLevel.MINIMAL,
            "pores": PoreSize.MEDIUM,
            "acne": _default_acne(),
            "texture": 50,
            "skin_tone": None,
        }
        new_state = state.copy()
        new_state["aggregated_analysis"] = agg
        new_state["skin_type"] = SkinType.NORMAL.value
        new_state["overall_score"] = 50
        new_state["recommendations"] = []
        new_state["explanation"] = self.FALLBACK_NOTE
        new_state["summary"] = self.FALLBACK_NOTE
        new_state["interactions"] = []
        new_state["home_remedies"] = ""
        new_state["wishing_message"] = (
            "We were unable to process your image with our AI this time. "
            "Please try again later or consult a dermatologist for professional advice."
        )
        new_state["errors"] = state.get("errors", []) + ["LLM unavailable, using fallback defaults"]
        return new_state

    def _call_llm_with_image(
        self, image_bytes: bytes, user_info: Optional[Dict[str, str]] = None
    ) -> LLMOutput:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        b64 = _encode_image(image_bytes)

        user_info_str = ""
        if user_info:
            parts = []
            for key, label in [
                ("age_group", "Age Group"),
                ("skin_type_self", "Self-Reported Skin Type"),
                ("gender", "Gender"),
                ("sensitive_skin", "Skin Sensitivity"),
            ]:
                if user_info.get(key):
                    parts.append(f"- {label}: {user_info[key]} (provided by user)")
            if parts:
                user_info_str = (
                    "\nThe user has also provided the following information about themselves:\n"
                    + "\n".join(parts)
                    + "\n\nPlease take this into account when tailoring your analysis."
                )

        prompt = (
            "You are a knowledgeable skincare consultant. Analyze the facial image provided and return "
            "a complete structured skin analysis.\n\n"
            f"{user_info_str}"
            "\n\nRate each metric honestly based on what you observe in the image. "
            "Use the full range of each scale — do not default to middle values. "
            "Be specific about what you see.\n\n"
            "IMPORTANT CONSTRAINTS:\n"
            "- Do NOT make discriminatory statements based on race, ethnicity, skin color, or origin\n"
            "- Do NOT diagnose medical conditions\n"
            "- Do NOT prescribe medication\n"
            "- Acknowledge that this is AI-generated and may not be perfect\n"
            "- Emphasize that every individual is unique\n"
            "- Always include a disclaimer that this is educational only\n"
            "Respond in a friendly, informative, and inclusive tone."
        )

        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.llm_api_key_gemini,
            temperature=0.3,
            max_tokens=4000,
            request_timeout=settings.llm_timeout_seconds,
        )

        structured = llm.with_structured_output(LLMOutput)
        messages = [
            SystemMessage(content=(
                "You are a knowledgeable skincare consultant. "
                "Never diagnose, prescribe medication, or discriminate."
            )),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                },
            ]),
        ]

        timeout = settings.llm_timeout_seconds
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(structured.invoke, messages)
            result = future.result(timeout=timeout)

        return result
