# CutiS

> AI-powered skin analysis — upload a photo or capture from camera to get educational insights about your skin condition, type, and suitable skincare ingredients.

**Important:** This is NOT a medical diagnostic tool. It does not replace professional dermatological advice.

## Features

- **Image Upload** — drag & drop or browse for a facial photo
- **Camera Capture** — take a selfie directly in the browser
- **Pre-Analysis Questionnaire** — tell us your age group, skin type, gender, and sensitivity for better-tailored insights
- **Face Detection & Alignment** — InsightFace with automatic frontalization
- **Skin Quality Gate** — checks for poor lighting, excessive blur, occlusion
- **Comprehensive Analysis** across 9 dimensions:
  - Oiliness (0–100), Hydration (0–100), Texture (0–100)
  - Redness, Pigmentation, Acne, Wrinkles (severity levels)
  - Pores (Small / Medium / Large), Skin Tone
- **AI-Generated Recommendations** — LLM suggests 5–6 personalized ingredients with reasons, usage notes, and precautions
- **Ingredient Interactions** — LLM flags incompatible ingredient pairs that should not be used together
- **Home Remedies** — LLM-generated natural remedy suggestions
- **Personalized Wishing Message** — friendly closing message from the AI
- **AI Summary** — human-readable explanation of findings
- **Privacy Focused** — images processed in memory, never stored
- **Rate Limiting** — 1 request per 60 seconds per IP

## Architecture

```
Frontend (Vue 3 + TypeScript + Vite + Pinia)
├── HomeView        — Hero, steps, upload/getting-started
├── AnalyzeView     — Questionnaire + ImageUpload + Camera
├── ResultsView     — Score ring, analysis grid, recs, interactions, remedies
└── Components     — ImageUpload, SkinQuestionnaire, TheHeader, TheFooter

Backend (FastAPI + LangGraph)
├── Image Decode & Validation
├── Face Detection (InsightFace)
├── Face Alignment
├── Face Parsing (skin segmentation)
├── Quality Gate (brightness, blur, occlusion)
├── Parallel Analysis (9 analyzers via ThreadPoolExecutor)
│   ├── Oiliness / Hydration / Redness / Pigmentation
│   ├── Acne / Wrinkles / Pores / Texture / Skin Tone
├── Aggregator
├── Skin Type Determination
├── Recommendation Engine (deterministic fallback)
├── LLM Explanation (LangChain with_structured_output)
│   └── Produces: explanation, summary, recommendations,
│       interactions, home_remedies, wishing_message
└── Response Builder

LLM Providers (switchable via .env)
├── Mistral (default, API key in .env)
└── Gemini (set LLM_PROVIDER=gemini)
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your LLM API key(s)

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on **http://localhost:3000** and proxies API requests to port 8000.

## API Endpoints

| Method | Path                | Description                        |
|--------|---------------------|------------------------------------|
| GET    | `/`                 | Root info                          |
| GET    | `/health`           | Health check                       |
| POST   | `/api/v1/analyze`   | Analyze a facial image             |

### POST `/api/v1/analyze`

**Content-Type:** `multipart/form-data`

**Form fields:**

| Field           | Required | Description                                                   |
|-----------------|----------|---------------------------------------------------------------|
| `file`          | yes      | Image file (JPG, JPEG, PNG, WEBP, max 10 MB)                 |
| `age_group`     | no       | One of: `18-24`, `25-30`, `31-40`, `41-50`, `50+`            |
| `skin_type_self`| no       | One of: `Oily`, `Dry`, `Combination`                         |
| `gender`        | no       | One of: `Male`, `Female`, `Non-binary / Other`               |
| `sensitive_skin`| no       | One of: `Yes`, `No`, `Sometimes`                              |

### Response

```json
{
  "overall_score": 82,
  "skin_type": "Combination",
  "analysis": {
    "oiliness": 74,
    "hydration": 61,
    "redness": "Low",
    "pigmentation": "Moderate",
    "wrinkles": "Minimal",
    "pores": "Medium",
    "acne": { "severity": "Mild", "count": 5 },
    "texture": 65,
    "skin_tone": "Medium"
  },
  "recommendations": [{ "ingredient": "Niacinamide", "priority": "High", "reason": "...", "suggested_frequency": "...", "usage_notes": "...", "precautions": "..." }],
  "interactions": [{ "ingredients": ["Vitamin C", "Retinol"], "reason": "...", "suggestion": "..." }],
  "summary": "Your skin type is Combination...",
  "home_remedies": "Try a soothing oatmeal mask twice a week...",
  "wishing_message": "Thank you for letting us help you on your skincare journey!",
  "disclaimer": "This analysis is AI-generated and may contain inaccuracies..."
}
```

### Error Codes

| Code                       | Meaning                        |
|----------------------------|--------------------------------|
| `no_face_detected`         | No face found                  |
| `multiple_faces_detected`  | More than one face             |
| `face_too_small`           | Face too small for analysis    |
| `poor_lighting`            | Image too dark or uneven       |
| `excessive_blur`           | Image out of focus             |
| `unsupported_image_format` | Not JPG/PNG/WEBP               |
| `image_too_large`          | Exceeds 10 MB                  |
| `low_resolution`           | Below 256×256 px               |
| `rate_limit_exceeded`      | More than 1 request per 60s    |

## Project Structure

```
skinpro/
├── app/
│   ├── analyzers/          # 9 skin analysis modules
│   ├── core/               # Config, exceptions, ratelimit, image validation
│   ├── graph/              # LangGraph pipeline: state, nodes, graph definition
│   │   ├── nodes/          # image_decoder, face_detector, explainer, response_builder, etc.
│   │   ├── graph.py        # Graph wiring
│   │   └── state.py        # AnalysisState TypedDict
│   ├── models/             # InsightFace, face parser, ONNX models
│   ├── pipeline/           # LangGraphOrchestrator
│   ├── schemas/            # Pydantic models for analysis, errors
│   ├── recommendations/    # Deterministic fallback engine
│   └── main.py             # FastAPI app, routes, middleware
├── frontend/
│   ├── src/
│   │   ├── components/     # ImageUpload, SkinQuestionnaire, TheHeader, TheFooter
│   │   ├── views/          # HomeView, AnalyzeView, ResultsView, AboutView
│   │   ├── stores/         # Pinia analysis store
│   │   ├── types/          # TypeScript interfaces
│   │   └── router/         # Vue Router config
│   ├── public/             # Favicon, static assets
│   └── index.html          # Entry point with animated loader
├── spec.md                 # Technical specification
├── README.md               # This file
├── .env.example            # Environment template
└── requirements.txt        # Python dependencies
```

## Configuration (`.env`)

```bash
DEBUG=true
LLM_ENABLED=true
LLM_PROVIDER=mistral          # or "gemini"
LLM_API_KEY=your_mistral_key
LLM_API_KEY_GEMINI=your_gemini_key
LLM_MODEL=mistral-small-latest
CORS_ORIGINS=["http://localhost:3000"]
```

## Performance Targets

| Stage             | Target   |
|-------------------|----------|
| Decode            | <20 ms   |
| Face Detection    | <80 ms   |
| Alignment         | <20 ms   |
| Parsing           | <150 ms  |
| Parallel Analysis | <300 ms  |
| Recommendation    | <10 ms   |
| Response Builder  | <10 ms   |
| **Total**         | **<1 s** |

LLM generation time is excluded (typically 2–5 s).

## Security & Privacy

- All image processing is done in memory — no images are stored on disk
- Images are discarded immediately after analysis completes
- No third-party image processing services
- Rate limiting prevents abuse (1 req / 60s per IP)
- LLM API keys stored server-side in `.env`, never exposed to the client

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `pytest` and `npx vue-tsc --noEmit`
5. Submit a pull request

## License

Proprietary. All rights reserved.
