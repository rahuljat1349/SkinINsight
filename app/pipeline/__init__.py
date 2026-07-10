"""Pipeline Orchestration Module"""

__all__ = ["pipeline", "langgraph_pipeline", "PipelineOrchestrator", "LangGraphPipelineOrchestrator"]


def __getattr__(name):
    if name == "pipeline":
        from app.pipeline.orchestrator import PipelineOrchestrator
        return PipelineOrchestrator()
    elif name == "langgraph_pipeline":
        from app.pipeline.langgraph_orchestrator import LangGraphPipelineOrchestrator
        return LangGraphPipelineOrchestrator()
    elif name == "PipelineOrchestrator":
        from app.pipeline.orchestrator import PipelineOrchestrator
        return PipelineOrchestrator
    elif name == "LangGraphPipelineOrchestrator":
        from app.pipeline.langgraph_orchestrator import LangGraphPipelineOrchestrator
        return LangGraphPipelineOrchestrator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
