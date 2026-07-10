"""Graph Nodes for Skin Analysis Pipeline"""

__all__ = []

# Try to import all nodes - they may have circular dependencies
try:
    from app.graph.nodes.image_decoder import ImageDecoderNode
    __all__.append("ImageDecoderNode")
except ImportError:
    pass

try:
    from app.graph.nodes.face_detector import FaceDetectorNode
    __all__.append("FaceDetectorNode")
except ImportError:
    pass

try:
    from app.graph.nodes.face_validator import FaceValidatorNode
    __all__.append("FaceValidatorNode")
except ImportError:
    pass

try:
    from app.graph.nodes.face_aligner import FaceAlignerNode
    __all__.append("FaceAlignerNode")
except ImportError:
    pass

try:
    from app.graph.nodes.face_parser import FaceParserNode
    __all__.append("FaceParserNode")
except ImportError:
    pass

try:
    from app.graph.nodes.quality_gate import QualityGateNode
    __all__.append("QualityGateNode")
except ImportError:
    pass

try:
    from app.graph.nodes.aggregator import AggregatorNode
    __all__.append("AggregatorNode")
except ImportError:
    pass

try:
    from app.graph.nodes.recommendation_node import RecommendationNode
    __all__.append("RecommendationNode")
except ImportError:
    pass

try:
    from app.graph.nodes.explainer import ExplainerNode
    __all__.append("ExplainerNode")
except ImportError:
    pass

try:
    from app.graph.nodes.response_builder import ResponseBuilderNode
    __all__.append("ResponseBuilderNode")
except ImportError:
    pass

try:
    from app.graph.nodes.error_handler import ErrorHandlerNode
    __all__.append("ErrorHandlerNode")
except ImportError:
    pass
