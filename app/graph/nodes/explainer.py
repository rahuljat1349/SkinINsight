"""Explainer Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
import concurrent.futures

from app.graph.state import AnalysisState
from app.core.config import settings
from app.schemas.llm_output import LLMOutput


class ExplainerNode:
    """
    Node that uses LLM to generate natural language explanations.
    """

    FALLBACK_SUMMARY = (
        "**Educational Note:** Our AI analysis completed the visual assessment of your skin, "
        "but we were unable to generate the full AI-powered explanation at this time. "
        "Below are your raw analysis scores — use them as a starting point for your skincare journey. "
        "For personalized medical advice, please consult a qualified dermatologist."
    )

    def __init__(self):
        self.name = "explainer"
        self.llm_enabled = settings.llm_enabled
        self.llm_model = settings.llm_model
        self.fallback_enabled = settings.fallback_to_local_models

    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Generate LLM explanation"""
        aggregated = state.get("aggregated_analysis", {})
        skin_type = state.get("skin_type")
        recommendations = state.get("recommendations", [])
        overall_score = state.get("overall_score", 0)
        user_info = state.get("user_info", {})

        if not self.llm_enabled:
            if self.fallback_enabled:
                return self._fallback_state(state, aggregated, skin_type, recommendations, overall_score)
            raise RuntimeError("LLM is disabled and no fallback configured")

        try:
            prompt = self._build_prompt(
                aggregated, skin_type, recommendations, overall_score, user_info
            )
            return self._call_llm(prompt, state)

        except Exception as e:
            if self.fallback_enabled:
                return self._fallback_state(state, aggregated, skin_type, recommendations, overall_score)
            error_msg = f"LLM explanation failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state

    def _fallback_state(
        self,
        state: AnalysisState,
        aggregated: Dict[str, Any],
        skin_type: Optional[str],
        recommendations: List[Dict[str, Any]],
        overall_score: int,
    ) -> AnalysisState:
        outputs = self._generate_deterministic_outputs(skin_type, aggregated, recommendations, overall_score)
        new_state = state.copy()
        new_state["summary"] = outputs["summary"]
        new_state["explanation"] = outputs["summary"]
        new_state["home_remedies"] = outputs["home_remedies"]
        new_state["wishing_message"] = outputs["wishing_message"]
        new_state["recommendations"] = recommendations or []
        new_state["interactions"] = []
        new_state["errors"] = state.get("errors", [])
        return new_state
    
    def _build_prompt(
        self,
        aggregated: Dict[str, Any],
        skin_type: Optional[str],
        recommendations: List[Dict[str, Any]],
        overall_score: int,
        user_info: Optional[Dict[str, str]] = None
    ) -> str:
        """Build prompt for LLM"""
        
        # Format analysis results
        analysis_str = self._format_analysis(aggregated, skin_type, overall_score)
        
        # Format user-provided info
        user_info_str = ""
        if user_info:
            parts = []
            if user_info.get("age_group"):
                parts.append(f"- Age Group: {user_info['age_group']} (provided by user)")
            if user_info.get("skin_type_self"):
                parts.append(f"- Self-Reported Skin Type: {user_info['skin_type_self']} (provided by user)")
            if user_info.get("gender"):
                parts.append(f"- Gender: {user_info['gender']} (provided by user)")
            if user_info.get("sensitive_skin"):
                parts.append(f"- Skin Sensitivity: {user_info['sensitive_skin']} (provided by user)")
            if parts:
                user_info_str = (
                    "\nThe user has also provided the following information about themselves:\n"
                    + "\n".join(parts)
                    + "\n\nPlease take this information into account when generating your recommendations and explanations."
                )
        
        prompt = f"""You are a knowledgeable skincare consultant providing educational insights.

{analysis_str}
{user_info_str}
Based on the analysis data above and any user-provided information, please provide:
1. A clear explanation of the skin analysis results
2. Educational information about what these findings mean
3. A concise summary
4. Specific skincare ingredient recommendations tailored to this analysis
5. Home remedies — suggest practical, natural home remedies the user can try (as a plain text paragraph)
6. A warm, friendly wishing message to close the analysis

IMPORTANT CONSTRAINTS:
- DO provide educational information about skin health
- DO explain what the analysis indicates
- DO summarize the key findings
- DO generate relevant ingredient recommendations with reasons
- DO suggest how to use recommended ingredients safely
- DO take user-provided information (age, skin type perception, gender, sensitivity) into account when tailoring recommendations
- DO acknowledge that this is an AI-generated analysis and may not be perfect
- DO emphasize that every individual is unique and there is no one-size-fits-all approach to skincare
- DO NOT make any statements that discriminate based on race, ethnicity, skin color, or origin
- DO NOT diagnose medical conditions
- DO NOT prescribe medication or specific treatments
- DO NOT invent observations not present in the data
- DO NOT use medical terminology for diagnosis
- Always include a disclaimer that this is educational only and not a medical diagnosis

Respond in a friendly, informative, and inclusive tone."""
        
        return prompt
    
    def _format_analysis(
        self,
        aggregated: Dict[str, Any],
        skin_type: Optional[str],
        overall_score: int
    ) -> str:
        """Format analysis results for prompt"""
        lines = []
        lines.append(f"Skin Type: {skin_type or 'Unknown'}")
        lines.append(f"Overall Skin Health Score: {overall_score}/100")
        lines.append("")
        lines.append("Analysis Results:")
        lines.append(f"  Oiliness: {aggregated.get('oiliness', 'N/A')} (0-100, higher = more oily)")
        lines.append(f"  Hydration: {aggregated.get('hydration', 'N/A')} (0-100, higher = more hydrated)")
        lines.append(f"  Redness: {aggregated.get('redness', 'N/A')}")
        lines.append(f"  Pigmentation: {aggregated.get('pigmentation', 'N/A')}")
        lines.append(f"  Wrinkles: {aggregated.get('wrinkles', 'N/A')}")
        lines.append(f"  Pores: {aggregated.get('pores', 'N/A')}")
        lines.append(f"  Texture: {aggregated.get('texture', 'N/A')} (0-100, higher = smoother)")
        acne = aggregated.get("acne", {})
        acne_severity = acne.severity if hasattr(acne, "severity") else "N/A"
        lines.append(f"  Acne: {acne_severity}")
        lines.append(f"  Skin Tone: {aggregated.get('skin_tone', 'N/A')}")
        
        return "\n".join(lines)
    
    def _call_llm(self, prompt: str, state: AnalysisState) -> AnalysisState:
        """Call LLM via LangChain with structured output"""
        from langchain_core.messages import SystemMessage, HumanMessage

        provider = settings.llm_provider
        api_key = settings.llm_api_key_gemini if provider == "gemini" else settings.llm_api_key
        model_name = settings.llm_model

        request_timeout = 30

        if provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model=model_name or "gemini-3.5-flash",
                google_api_key=api_key,
                temperature=0.3,
                max_tokens=2000,
                request_timeout=request_timeout,
            )
        else:
            from langchain_mistralai import ChatMistralAI
            llm = ChatMistralAI(
                model=model_name or "mistral-small-latest",
                api_key=api_key,
                temperature=0.3,
                max_tokens=2000,
                timeout=request_timeout,
            )

        structured_llm = llm.with_structured_output(LLMOutput)
        messages = [
            SystemMessage(content=(
                "You are a knowledgeable skincare consultant. "
                "Never diagnose, prescribe medication, or invent observations."
            )),
            HumanMessage(content=prompt),
        ]

        timeout = request_timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(structured_llm.invoke, messages)
            result = future.result(timeout=timeout)

        new_state = state.copy()
        new_state["explanation"] = result.explanation or result.summary
        new_state["summary"] = result.summary or result.explanation
        new_state["recommendations"] = [
            r.model_dump() for r in (result.recommendations or [])
        ]
        new_state["interactions"] = [
            i.model_dump() for i in (result.interactions or [])
        ]
        new_state["home_remedies"] = result.home_remedies or ""
        new_state["wishing_message"] = result.wishing_message or ""
        new_state["errors"] = state.get("errors", [])
        return new_state

    def _generate_deterministic_outputs(
        self,
        skin_type: Optional[str],
        aggregated: Optional[Dict[str, Any]],
        recommendations: Optional[List[Dict[str, Any]]],
        overall_score: int,
    ) -> Dict[str, str]:
        redness = aggregated.get("redness", "N/A") if aggregated else "N/A"
        oiliness = aggregated.get("oiliness", 50) if aggregated else 50
        hydration = aggregated.get("hydration", 50) if aggregated else 50
        wrinkles = aggregated.get("wrinkles", "N/A") if aggregated else "N/A"
        pores = aggregated.get("pores", "N/A") if aggregated else "N/A"

        home = [
            "Here are some gentle natural approaches you can consider alongside your regular skincare routine:",
        ]
        if isinstance(oiliness, (int, float)) and oiliness > 60:
            home.append("- **Aloe Vera** — Apply fresh aloe vera gel to help balance oil production and soothe the skin.")
            home.append("- **Green Tea Toner** — Brew green tea, let it cool, and use as a gentle toner.")
        if isinstance(hydration, (int, float)) and hydration < 40:
            home.append("- **Honey Mask** — Raw honey is a natural humectant. Apply for 15 minutes and rinse.")
            home.append("- **Cucumber Slices** — Place cool cucumber slices on your face to boost hydration.")
        if "High" in str(redness) or "Moderate" in str(redness):
            home.append("- **Chamomile Compress** — Brew chamomile tea, cool it, and use as a compress to calm redness.")
            home.append("- **Oatmeal Mask** — Finely ground oatmeal mixed with yogurt soothes sensitive or red skin.")
        if "Moderate" in str(wrinkles) or "Severe" in str(wrinkles):
            home.append("- **Aloe Vera & Vitamin E** — Mix aloe vera gel with vitamin E oil and apply nightly.")
        if "Large" in str(pores):
            home.append("- **Ice Cubes** — Gently rub an ice cube wrapped in a cloth to temporarily tighten pores.")
        home.append("")
        home.append("> **Remember:** Home remedies are complementary — not a replacement for professional skincare advice. Always patch-test new ingredients.")

        wishing = (
            "Thank you for using **CutiS**! Your skin is unique, and this analysis is a starting point "
            "for your skincare journey. Small, consistent steps lead to the best results. "
            "For personalized medical advice, please consult a qualified dermatologist."
        )

        summary_parts = [self.FALLBACK_SUMMARY]
        if skin_type:
            summary_parts.append(f"**Skin Type:** {skin_type}")
        if overall_score:
            label = "Excellent" if overall_score >= 80 else "Good" if overall_score >= 60 else "Fair" if overall_score >= 40 else "Needs Improvement"
            summary_parts.append(f"**Overall Score:** {overall_score}/100 — {label}")
        if aggregated:
            summary_parts.append("")
            summary_parts.append("### Analysis Results")
            summary_parts.append(f"- **Oiliness:** {oiliness}/100")
            summary_parts.append(f"- **Hydration:** {hydration}/100")
            summary_parts.append(f"- **Redness Level:** {redness}")
            summary_parts.append(f"- **Pigmentation:** {aggregated.get('pigmentation', 'N/A')}")
            summary_parts.append(f"- **Wrinkles:** {wrinkles}")
            summary_parts.append(f"- **Pores:** {pores}")
            summary_parts.append(f"- **Texture:** {aggregated.get('texture', 50)}/100")
            acne = aggregated.get("acne", {})
            summary_parts.append(f"- **Acne:** {getattr(acne, 'severity', 'N/A')}")
        if recommendations:
            summary_parts.append("")
            summary_parts.append("### Recommended Ingredients")
            for rec in recommendations[:5]:
                summary_parts.append(f"- **{rec.get('ingredient', 'Unknown')}** ({rec.get('priority', 'Medium')}): {rec.get('reason', '')}")
        summary_parts.append("")
        summary_parts.append("---")
        summary_parts.append("*This analysis is AI-generated and for educational purposes only.*")

        return {
            "summary": "\n\n".join(summary_parts),
            "home_remedies": "\n\n".join(home),
            "wishing_message": wishing,
        }
