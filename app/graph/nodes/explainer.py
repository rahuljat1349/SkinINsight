"""Explainer Node for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.graph.state import AnalysisState
from app.core.config import settings
from app.schemas.analysis import (
    AcneSeverity,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    SkinType,
    WrinkleLevel
)


class ExplainerNode:
    """
    Node that uses LLM to generate natural language explanations.
    
    Only node using an LLM.
    
    Input:
    - Aggregated analysis
    - Recommendations
    
    Output:
    - explanation: Natural-language explanation
    - summary: Brief summary
    
    The LLM must:
    - explain
    - educate
    - summarize
    
    The LLM must not:
    - diagnose
    - prescribe medication
    - invent observations
    """
    
    def __init__(self):
        self.name = "explainer"
        self.llm_enabled = settings.llm_enabled
        self.llm_model = settings.llm_model
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Generate LLM explanation"""
        aggregated = state.get("aggregated_analysis", {})
        skin_type = state.get("skin_type")
        recommendations = state.get("recommendations", [])
        overall_score = state.get("overall_score", 0)
        user_info = state.get("user_info", {})
        
        if not self.llm_enabled:
            # Fallback to deterministic summary generation
            summary = self._generate_deterministic_summary(
                skin_type, aggregated, recommendations, overall_score
            )
            
            new_state = state.copy()
            new_state["summary"] = summary
            new_state["explanation"] = summary  # Use same for explanation if LLM disabled
            new_state["interactions"] = []
            new_state["home_remedies"] = ""
            new_state["wishing_message"] = ""
            new_state["errors"] = state.get("errors", [])
            return new_state
        
        try:
            # Build prompt
            prompt = self._build_prompt(
                aggregated, skin_type, recommendations, overall_score, user_info
            )
            
            # Call LLM
            return self._call_llm(prompt, state)
            
        except Exception as e:
            error_msg = f"LLM explanation failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
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
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for prompt"""
        if not recommendations:
            return "No specific recommendations generated."
        
        lines = ["Recommended Ingredients:"]
        for rec in recommendations:
            lines.append(f"  - {rec.get('ingredient', 'Unknown')}: {rec.get('reason', '')}")
            lines.append(f"    Priority: {rec.get('priority', 'N/A')}")
        
        return "\n".join(lines)
    
    def _call_llm(self, prompt: str, state: AnalysisState) -> AnalysisState:
        """Call LLM via LangChain to generate explanation, summary, recommendations, and interactions"""
        provider = settings.llm_provider
        model_name = settings.llm_model

        api_key = settings.llm_api_key_gemini if provider == "gemini" else settings.llm_api_key
        if not api_key:
            print(f"No API key configured for provider '{provider}', using deterministic fallback")
            summary = self._generate_deterministic_summary(None, None, None, 0)
            new_state = state.copy()
            new_state["summary"] = summary
            new_state["explanation"] = summary
            new_state["interactions"] = []
            new_state["errors"] = state.get("errors", [])
            return new_state

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.messages import SystemMessage, HumanMessage

            if provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model=model_name or "gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=0.3,
                    max_tokens=2000,
                )
            else:
                from langchain_mistralai import ChatMistralAI
                llm = ChatMistralAI(
                    model=model_name or "mistral-small-latest",
                    api_key=api_key,
                    temperature=0.3,
                    max_tokens=2000,
                )

            class Recommendation(BaseModel):
                ingredient: str
                priority: str
                reason: str
                suggested_frequency: Optional[str] = None
                usage_notes: Optional[str] = None
                precautions: Optional[str] = None

            class Interaction(BaseModel):
                ingredients: list[str]
                reason: str
                suggestion: str

            class LLMOutput(BaseModel):
                explanation: str
                summary: str
                recommendations: list[Recommendation]
                interactions: list[Interaction]
                home_remedies: str
                wishing_message: str

            structured_llm = llm.with_structured_output(LLMOutput)

            result = structured_llm.invoke([
                SystemMessage(content=(
                    "You are a knowledgeable skincare consultant. "
                    "Never diagnose, prescribe medication, or invent observations."
                )),
                HumanMessage(content=prompt),
            ])

            new_state = state.copy()
            new_state["explanation"] = result.explanation or result.summary
            new_state["summary"] = result.summary or result.explanation
            new_state["recommendations"] = [
                r.dict() if hasattr(r, 'dict') else r
                for r in (result.recommendations or [])
            ]
            new_state["interactions"] = [
                i.dict() if hasattr(i, 'dict') else i
                for i in (result.interactions or [])
            ]
            new_state["home_remedies"] = getattr(result, "home_remedies", "")
            new_state["wishing_message"] = getattr(result, "wishing_message", "")
            new_state["errors"] = state.get("errors", [])
            return new_state

        except ImportError as e:
            print(f"LangChain package not installed: {e}, using deterministic fallback")
        except Exception as e:
            print(f"LLM call failed ({provider}): {e}, using deterministic fallback")

        summary = self._generate_deterministic_summary(None, None, None, 0)
        new_state = state.copy()
        new_state["summary"] = summary
        new_state["explanation"] = summary
        new_state["recommendations"] = state.get("recommendations", [])
        new_state["interactions"] = []
        new_state["home_remedies"] = ""
        new_state["wishing_message"] = ""
        new_state["errors"] = state.get("errors", [])
        return new_state
    
    def _generate_deterministic_summary(
        self,
        skin_type: Optional[str],
        aggregated: Optional[Dict[str, Any]],
        recommendations: Optional[List[Dict[str, Any]]],
        overall_score: int
    ) -> str:
        """Generate deterministic summary as fallback"""
        summary_parts = []
        
        if skin_type:
            summary_parts.append(f"Your skin type is {skin_type}.")
        
        if aggregated:
            oiliness = aggregated.get("oiliness", 50)
            hydration = aggregated.get("hydration", 50)
            
            if oiliness > 70:
                summary_parts.append("Your skin shows high oiliness.")
            elif oiliness < 30:
                summary_parts.append("Your skin shows low oiliness.")
            else:
                summary_parts.append("Your skin has balanced oil levels.")
            
            if hydration < 40:
                summary_parts.append("Your skin appears dehydrated and could benefit from additional moisture.")
            elif hydration > 70:
                summary_parts.append("Your skin is well-hydrated.")
            else:
                summary_parts.append("Your skin hydration levels are adequate.")
        
        if recommendations:
            summary_parts.append("Based on your analysis, we recommend focusing on:")
            for rec in recommendations[:3]:  # Top 3 recommendations
                summary_parts.append(f"  - {rec.get('ingredient', 'Unknown')}: {rec.get('reason', '')}")
        
        summary_parts.append("\nRemember: This analysis provides educational information only. "
                           "It is not a medical diagnosis. For personalized advice, please consult with a dermatologist.")
        
        return " ".join(summary_parts)
