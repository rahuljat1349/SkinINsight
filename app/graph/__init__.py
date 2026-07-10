"""LangGraph Pipeline for Skin Insight AI"""

# Avoid circular imports by using lazy imports
__all__ = ["AnalysisState", "create_analysis_graph", "LangGraphPipeline"]


def __getattr__(name):
    if name == "AnalysisState":
        from app.graph.state import AnalysisState
        return AnalysisState
    elif name == "create_analysis_graph":
        from app.graph.graph import create_analysis_graph
        return create_analysis_graph
    elif name == "LangGraphPipeline":
        from app.graph.graph import LangGraphPipeline
        return LangGraphPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
