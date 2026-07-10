"""Analyzer Nodes for LangGraph Pipeline"""

from typing import Any, Dict, List, Optional
import numpy as np

from app.graph.state import AnalysisState
from app.analyzers.base import BaseAnalyzer
from app.analyzers.oiliness import OilinessAnalyzer
from app.analyzers.hydration import HydrationAnalyzer
from app.analyzers.redness import RednessAnalyzer
from app.analyzers.pigmentation import PigmentationAnalyzer
from app.analyzers.acne import AcneAnalyzer
from app.analyzers.wrinkles import WrinklesAnalyzer
from app.analyzers.pores import PoresAnalyzer
from app.analyzers.texture import TextureAnalyzer
from app.analyzers.skin_tone import SkinToneAnalyzer
from app.analyzers.skin_type import SkinTypeAnalyzer


class BaseAnalyzerNode:
    """Base class for analyzer nodes"""
    
    def __init__(self, analyzer: BaseAnalyzer, field_name: str):
        self.analyzer = analyzer
        self.field_name = field_name
        self.name = f"analyzer_{field_name}"
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Run analyzer on aligned face and skin mask"""
        aligned_face = state.get("aligned_face")
        skin_mask = state.get("skin_mask")
        regions = state.get("regions")
        
        if aligned_face is None:
            new_state = state.copy()
            new_state["current_error"] = f"No aligned face available for {self.field_name} analysis"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [f"No aligned face for {self.field_name}"]
            return new_state
        
        try:
            # Run analysis
            result = self.analyzer.analyze(aligned_face, skin_mask, regions)
            
            # Update analysis results
            analysis = state.get("analysis", {})
            analysis[self.field_name] = result
            
            new_state = state.copy()
            new_state["analysis"] = analysis
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"{self.field_name} analysis failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state


class OilinessAnalyzerNode(BaseAnalyzerNode):
    """Oiliness analyzer node"""
    def __init__(self):
        super().__init__(OilinessAnalyzer(), "oiliness")


class HydrationAnalyzerNode(BaseAnalyzerNode):
    """Hydration analyzer node"""
    def __init__(self):
        super().__init__(HydrationAnalyzer(), "hydration")


class RednessAnalyzerNode(BaseAnalyzerNode):
    """Redness analyzer node"""
    def __init__(self):
        super().__init__(RednessAnalyzer(), "redness")


class PigmentationAnalyzerNode(BaseAnalyzerNode):
    """Pigmentation analyzer node"""
    def __init__(self):
        super().__init__(PigmentationAnalyzer(), "pigmentation")


class AcneAnalyzerNode(BaseAnalyzerNode):
    """Acne analyzer node"""
    def __init__(self):
        super().__init__(AcneAnalyzer(), "acne")


class WrinklesAnalyzerNode(BaseAnalyzerNode):
    """Wrinkles analyzer node"""
    def __init__(self):
        super().__init__(WrinklesAnalyzer(), "wrinkles")


class PoresAnalyzerNode(BaseAnalyzerNode):
    """Pores analyzer node"""
    def __init__(self):
        super().__init__(PoresAnalyzer(), "pores")


class TextureAnalyzerNode(BaseAnalyzerNode):
    """Texture analyzer node"""
    def __init__(self):
        super().__init__(TextureAnalyzer(), "texture")


class SkinToneAnalyzerNode(BaseAnalyzerNode):
    """Skin tone analyzer node"""
    def __init__(self):
        super().__init__(SkinToneAnalyzer(), "skin_tone")


class SkinTypeAnalyzerNode:
    """
    Skin type analyzer node - special case as it depends on other analysis results
    """
    def __init__(self):
        self.name = "analyzer_skin_type"
        self.analyzer = SkinTypeAnalyzer()
        self.field_name = "skin_type"
    
    def __call__(self, state: AnalysisState) -> AnalysisState:
        """Determine skin type based on analysis results"""
        aligned_face = state.get("aligned_face")
        skin_mask = state.get("skin_mask")
        regions = state.get("regions")
        analysis = state.get("analysis", {})
        
        if aligned_face is None:
            new_state = state.copy()
            new_state["current_error"] = "No aligned face available for skin type analysis"
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + ["No aligned face for skin type"]
            return new_state
        
        try:
            # Get required analysis results
            oiliness = analysis.get("oiliness", 50)
            hydration = analysis.get("hydration", 50)
            
            # Run skin type analysis
            skin_type = self.analyzer.analyze(
                aligned_face,
                skin_mask,
                regions,
                oiliness=oiliness,
                hydration=hydration
            )
            
            new_state = state.copy()
            new_state["skin_type"] = skin_type.value if hasattr(skin_type, 'value') else str(skin_type)
            new_state["errors"] = state.get("errors", [])
            
            return new_state
            
        except Exception as e:
            error_msg = f"Skin type analysis failed: {str(e)}"
            new_state = state.copy()
            new_state["current_error"] = error_msg
            new_state["is_error_state"] = True
            new_state["errors"] = state.get("errors", []) + [error_msg]
            return new_state
