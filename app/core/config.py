"""Application Configuration"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "CutiS"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Image settings
    max_image_size_mb: int = 10
    max_image_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    supported_image_formats: set[str] = {"jpg", "jpeg", "png", "webp"}
    min_face_size_pixels: int = 100  # Minimum face width/height in pixels
    min_image_resolution: tuple[int, int] = (256, 256)  # Minimum width, height
    
    # Face detection
    face_detection_confidence_threshold: float = 0.5
    
    # Model paths (can be overridden by environment)
    insightface_model_path: str = "models/insightface"
    face_parsing_model_path: str = "models/face_parsing"
    
    # LLM settings
    llm_enabled: bool = True
    llm_provider: str = "mistral"  # "mistral" or "gemini"
    llm_api_key: str = ""  # Mistral API key (from LLM_API_KEY env)
    llm_api_key_gemini: str = ""  # Gemini API key (from LLM_API_KEY_GEMINI env)
    llm_model: str = "mistral-small-latest"
    llm_timeout_seconds: int = 30

    # Pipeline mode
    send_image_to_llm: str = "false"  # "false" = CV only, "true" = LLM only, "hybrid" = both
    fallback_to_local_models: bool = False  # If True, use deterministic fallback when LLM fails
    
    # Performance targets
    target_face_detection_ms: int = 100
    target_face_parsing_ms: int = 150
    target_analysis_ms: int = 300
    target_recommendation_ms: int = 20
    target_total_pipeline_ms: int = 700
    
    # CORS
    cors_origins: list[str] = ["*"]  # Allow all in development
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()


# Convenience access
settings = get_settings()
