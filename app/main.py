"""CutiS - Main Application"""

import logging
import os
import time
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.ratelimit import RateLimiter
from typing import Dict, Optional
from app.core.exceptions import (
    NoFaceDetectedError,
    MultipleFacesError,
    FaceTooSmallError,
    PoorLightingError,
    ExcessiveBlurError,
    UnsupportedFormatError,
    ImageTooLargeError,
    LowResolutionError,
    InternalInferenceError
)
from app.pipeline.langgraph_orchestrator import LangGraphPipelineOrchestrator
from app.schemas.analysis import AnalysisResponse
from app.schemas.errors import ErrorResponse


# Logging setup
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cutis")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered skin analysis API that provides educational insights about skin condition and recommendations.",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("Starting CutiS v%s", settings.app_version)
logger.info("LLM provider: %s, model: %s", settings.llm_provider, settings.llm_model)
logger.info("Pipeline mode: send_image_to_llm=%s", settings.send_image_to_llm)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter: 1 request per 15 seconds per IP
rate_limiter = RateLimiter(max_requests=1, window_seconds=15)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/api/v1/analyze" and request.method == "POST":
        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = rate_limiter.check(client_ip)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                        "user_message": f"Please wait {retry_after} seconds before the next analysis."
                    },
                    "success": False
                },
                headers={"Retry-After": str(retry_after)}
            )
    return await call_next(request)


# Initialize LangGraph pipeline orchestrator
pipeline = LangGraphPipelineOrchestrator()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


@app.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request or image"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Analyze a facial image",
    description="Upload a facial image to get comprehensive skin analysis including skin type, oiliness, hydration, and personalized recommendations."
)
async def analyze_image(
    file: UploadFile = File(..., description="Image file (JPG, JPEG, PNG, WEBP)"),
    age_group: Optional[str] = Form(None, description="Age group (18-24, 25-30, 31-40, 41-50, 50+)"),
    skin_type_self: Optional[str] = Form(None, description="Self-reported skin type (Oily, Dry, Combination)"),
    gender: Optional[str] = Form(None, description="Gender (Male, Female, Non-binary/Other)"),
    sensitive_skin: Optional[str] = Form(None, description="Is skin sensitive? (Yes, No, Sometimes)")
) -> AnalysisResponse:
    """
    Analyze a facial image and return skin insights.
    
    This endpoint:
    - Validates the uploaded image
    - Detects and aligns the face
    - Analyzes various skin characteristics
    - Generates personalized recommendations
    - Returns a comprehensive report
    
    **Image Requirements:**
    - Format: JPG, JPEG, PNG, or WEBP
    - Maximum size: 10 MB
    - One clearly visible face
    - Frontal pose preferred
    - Good lighting
    - Minimal blur
    """
    start_time = time.time()
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        logger.info("Analyze request: file=%s, size=%d bytes, age=%s, skin=%s, gender=%s, sensitive=%s",
                     file.filename, len(image_bytes), age_group, skin_type_self, gender, sensitive_skin)
        
        # Validate file size
        if len(image_bytes) > settings.max_image_size_bytes:
            raise ImageTooLargeError(len(image_bytes), settings.max_image_size_bytes)
        
        # Build user info dict
        user_info: Dict[str, str] = {}
        if age_group:
            user_info["age_group"] = age_group
        if skin_type_self:
            user_info["skin_type_self"] = skin_type_self
        if gender:
            user_info["gender"] = gender
        if sensitive_skin:
            user_info["sensitive_skin"] = sensitive_skin
        
        # Validate image
        try:
            analysis_response = pipeline.analyze_image(image_bytes, user_info=user_info)
        except NoFaceDetectedError as e:
            raise e
        except MultipleFacesError as e:
            raise e
        except FaceTooSmallError as e:
            raise e
        except PoorLightingError as e:
            raise e
        except ExcessiveBlurError as e:
            raise e
        except UnsupportedFormatError as e:
            raise e
        except ImageTooLargeError as e:
            raise e
        except LowResolutionError as e:
            raise e
        except Exception as e:
            raise InternalInferenceError(str(e))
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info("Analysis complete: processing_time=%.0fms, score=%s",
                     processing_time, analysis_response.overall_score)
        
        return analysis_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Analysis failed: %s", str(e), exc_info=True)
        raise InternalInferenceError(str(e))


# Error handlers
@app.exception_handler(NoFaceDetectedError)
async def no_face_detected_handler(request, exc: NoFaceDetectedError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "no_face_detected",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(MultipleFacesError)
async def multiple_faces_handler(request, exc: MultipleFacesError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "multiple_faces_detected",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(FaceTooSmallError)
async def face_too_small_handler(request, exc: FaceTooSmallError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "face_too_small",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(PoorLightingError)
async def poor_lighting_handler(request, exc: PoorLightingError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "poor_lighting",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(ExcessiveBlurError)
async def excessive_blur_handler(request, exc: ExcessiveBlurError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "excessive_blur",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(UnsupportedFormatError)
async def unsupported_format_handler(request, exc: UnsupportedFormatError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "unsupported_image_format",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(ImageTooLargeError)
async def image_too_large_handler(request, exc: ImageTooLargeError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "image_too_large",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(LowResolutionError)
async def low_resolution_handler(request, exc: LowResolutionError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "low_resolution",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


@app.exception_handler(InternalInferenceError)
async def internal_error_handler(request, exc: InternalInferenceError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": exc.message,
                "user_message": exc.user_message
            },
            "success": False
        }
    )


# Mount static files for serving frontend (in production)
# In development, frontend is served separately
if os.getenv("SERVE_FRONTEND", "false").lower() == "true":
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
