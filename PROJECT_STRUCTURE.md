# CutiS - Project Structure

## Overview

This document describes the complete file structure of the CutiS project, which includes:

- **Backend**: FastAPI (Python) application with AI-powered skin analysis
- **Frontend**: Vue 3 + TypeScript + Vite web application
- **Docker**: Containerized deployment

## Complete File Structure

```
skinpro/
├── spec.md                          # Product specification
├── README.md                        # Main documentation
├── PROJECT_STRUCTURE.md             # This file
├── Dockerfile                       # Docker configuration
├── .dockerignore                    # Docker ignore rules
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
│
├── app/                             # Backend Application
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── api/                         # API route handlers
│   │   └── __init__.py
│   │
│   ├── analyzers/                   # Skin analysis modules
│   │   ├── __init__.py
│   │   ├── base.py                  # Base analyzer class
│   │   ├── oiliness.py              # Oiliness analyzer (0-100)
│   │   ├── hydration.py             # Hydration analyzer (0-100)
│   │   ├── skin_type.py             # Skin type classifier
│   │   ├── redness.py               # Redness analyzer (Low/Moderate/High)
│   │   ├── pigmentation.py          # Pigmentation analyzer
│   │   ├── acne.py                  # Acne analyzer with severity and count
│   │   ├── wrinkles.py              # Wrinkles analyzer
│   │   ├── pores.py                 # Pores analyzer (Small/Medium/Large)
│   │   ├── texture.py               # Texture smoothness analyzer
│   │   └── skin_tone.py             # Skin tone estimator
│   │
│   ├── core/                        # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                # Application configuration
│   │   ├── exceptions.py            # Custom exception classes
│   │   └── image_validator.py        # Image validation logic
│   │
│   ├── llm/                         # LLM integration (for future)
│   │   └── __init__.py
│   │
│   ├── models/                      # ML models and face processing
│   │   ├── __init__.py
│   │   ├── face_detector.py         # InsightFace face detection
│   │   ├── face_aligner.py          # Face alignment and normalization
│   │   └── face_parser.py           # Face segmentation into regions
│   │
│   ├── pipeline/                    # Pipeline orchestration
│   │   ├── __init__.py
│   │   └── orchestrator.py          # Main pipeline coordinator
│   │
│   ├── recommendations/             # Recommendation engine
│   │   ├── __init__.py
│   │   └── engine.py                # Rule-based ingredient recommendations
│   │
│   └── schemas/                     # Pydantic data models
│       ├── __init__.py
│       ├── analysis.py              # Analysis result schemas
│       ├── errors.py                # Error response schemas
│       └── image.py                 # Image validation schemas
│
├── frontend/                        # Frontend Application
│   ├── index.html                   # HTML entry point
│   ├── favicon.svg                  # Favicon
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.ts               # Vite configuration
│   ├── tsconfig.json                # TypeScript configuration
│   └── tsconfig.node.json           # TypeScript node configuration
│   
│   └── src/                        # Frontend source code
│       ├── main.ts                  # Application entry point
│       ├── vite-env.d.ts            # Vite environment types
│       ├── App.vue                 # Root Vue component
│       │
│       ├── assets/                 # Static assets
│       │   └── main.css             # Global CSS styles
│       │
│       ├── components/             # Vue components
│       │   ├── TheHeader.vue        # Site header
│       │   ├── TheFooter.vue        # Site footer
│       │   └── ImageUpload.vue      # Image upload with drag & drop
│       │
│       ├── composables/            # Vue composables (empty)
│       │   └── (future)
│       │
│       ├── router/                 # Vue Router
│       │   └── index.ts             # Route definitions
│       │
│       ├── stores/                 # Pinia stores
│       │   ├── index.ts
│       │   └── analysisStore.ts     # Analysis state management
│       │
│       ├── types/                  # TypeScript type definitions
│       │   └── index.ts             # Type definitions for analysis data
│       │
│       └── views/                  # Page views
│           ├── HomeView.vue         # Landing page
│           ├── AnalyzeView.vue      # Analysis page with upload
│           ├── ResultsView.vue      # Results display
│           ├── AboutView.vue        # About page
│           └── NotFoundView.vue     # 404 page
│
└── tests/                          # Tests (empty - to be added)
    └── __init__.py
```

## Backend Details

### Technology Stack
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.10+
- **Dependencies**:
  - `fastapi` - Web framework
  - `uvicorn` - ASGI server
  - `pydantic` - Data validation
  - `insightface` - Face detection
  - `opencv-python` - Image processing
  - `numpy` - Numerical operations
  - `onnxruntime` - ONNX model inference
  - `Pillow` - Image handling

### Key Features
1. **Image Validation**: Format, size, blur, lighting checks
2. **Face Detection**: Uses InsightFace for accurate detection
3. **Face Alignment**: Normalizes face position and scale
4. **Face Parsing**: Segments face into regions (skin, forehead, cheeks, etc.)
5. **Parallel Analysis**: 10 analyzers run concurrently
6. **Recommendation Engine**: Rule-based ingredient suggestions
7. **Error Handling**: Custom exceptions with user-friendly messages
8. **Configuration**: Environment-based settings

### API Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/analyze` - Main analysis endpoint (multipart form-data)

### Performance Targets
| Component | Target |
|-----------|--------|
| Face Detection | <100 ms |
| Face Parsing | <150 ms |
| Parallel Analysis | <300 ms |
| Recommendation Engine | <20 ms |
| **Total Pipeline** | **<700 ms** |

## Frontend Details

### Technology Stack
- **Framework**: Vue 3
- **Language**: TypeScript
- **Build Tool**: Vite 5
- **State Management**: Pinia
- **Router**: Vue Router 4
- **Styling**: CSS Variables + Scoped Styles
- **Dependencies**:
  - `vue`, `pinia`, `vue-router`
  - `@vitejs/plugin-vue`, `@vitejs/plugin-vue-jsx`
  - `typescript`, `vite`

### Key Features
1. **Responsive Design**: Mobile-first, fully responsive
2. **Image Upload**: Drag & drop, file selection, preview
3. **Form Validation**: Client-side image validation
4. **Loading States**: Spinner, progress bar, processing indicators
5. **Error Handling**: User-friendly error messages
6. **State Management**: Pinia store for analysis data
7. **Routing**: Multi-page navigation
8. **Typography**: Google Fonts (Inter)

### Page Structure
- **Home**: Landing page with upload component and feature overview
- **Analyze**: Dedicated analysis page with requirements guide
- **Results**: Comprehensive results display with:
  - Overall score (circular progress)
  - Skin type badge
  - Image preview
  - Analysis details (8-10 metrics)
  - AI summary
  - Personalized recommendations (ingredient cards)
  - Action buttons (Analyze Again, Home)
- **About**: Information about the application
- **404**: Not found page

### CSS Architecture
- **Variables**: CSS custom properties for theming
- **Scoped Styles**: Component-scoped styles
- **Global Styles**: Base reset, typography, animations
- **Utility Classes**: Container, spacing, etc.
- **Responsive**: Media queries for all screen sizes

## Docker Configuration

### Build Process
- Multi-stage build for smaller final image
- Build stage: Installs dependencies
- Production stage: Copies only necessary files

### Runtime
- Exposes port 8000
- Health check endpoint
- Mountable models volume
- Environment variables support

## File Count Summary

| Category | Count |
|----------|-------|
| Backend Python files | 25+ |
| Frontend Vue/TS files | 15+ |
| Configuration files | 8 |
| **Total** | **48+** |

## Next Steps

1. **Install Dependencies**:
   ```bash
   # Backend
   cd skinpro
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Run Development Servers**:
   ```bash
   # Backend (port 8000)
   python -m uvicorn app.main:app --reload
   
   # Frontend (port 3000)
   npm run dev
   ```

3. **Build for Production**:
   ```bash
   # Backend: Already production-ready
   
   # Frontend
   npm run build
   
   # Docker
   docker build -t cutis .
   docker run -p 8000:8000 cutis
   ```

4. **Access**:
   - Backend API: http://localhost:8000/docs
   - Frontend: http://localhost:3000
   - Production: http://localhost:8000 (if serving frontend from backend)

## Notes

- The backend is fully functional and can be tested independently
- The frontend connects to `/api` proxy (configured in vite.config.ts)
- InsightFace models are downloaded automatically on first run
- All images are processed in memory and not stored
- The system prioritizes privacy and user data protection
