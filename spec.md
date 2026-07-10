# Skin Insight AI — Technical Specification (v2.0)

## Architecture

- **Frontend:** Vue 3 + Vite + TypeScript + Pinia
- **Backend:** FastAPI (Python 3.10+)
- **Workflow Engine:** LangGraph
- **CV Models:** InsightFace (detection), Face Parsing (BiSeNet / CelebAMask-HQ)
- **ML Runtime:** ONNX Runtime + PyTorch
- **LLM Providers:** Mistral (default) or Gemini, via LangChain `.with_structured_output()`
- **Deployment:** Docker

---

## Design Principles

The system is **not an AI agent**.

It is a deterministic computer vision pipeline orchestrated by LangGraph.

- Each node has exactly one responsibility
- Nodes never decide which node executes next except through predefined conditional edges
- Business logic lives outside the graph

---

## High-Level Architecture

```
Browser (Vue 3)
   │
   │ POST /api/v1/analyze (multipart/form-data)
   ▼
FastAPI
   │
   │ Rate limit check (1 req / 60s per IP)
   ▼
LangGraph Pipeline
   │
   ├── Image Decode
   ├── Face Detection (InsightFace)
   ├── Face Validation (single face, min size, resolution)
   ├── Face Alignment (normalize rotation / scale / position)
   ├── Face Parsing (skin mask, forehead, cheeks, chin)
   ├── Quality Gate (brightness, blur, occlusion, parser confidence)
   ├── Parallel Analysis (9 analyzers via ThreadPoolExecutor)
   │   ├── Oiliness / Hydration / Redness / Pigmentation
   │   ├── Acne / Wrinkles / Pores / Texture / Skin Tone
   ├── Aggregator (merge into single structured dict)
   ├── Skin Type Determination
   ├── Recommendation Engine (deterministic fallback)
   └── LLM Explanation (LangChain with_structured_output)
       └── Generates: explanation, summary, recommendations,
           interactions, home_remedies, wishing_message
   │
   ▼
Response Builder → JSON Response
```

---

## LangGraph State (`AnalysisState`)

```python
class AnalysisState(TypedDict):
    # Input
    image_bytes: Optional[bytes]
    user_info: Optional[Dict[str, str]]   # age_group, skin_type_self, gender, sensitive_skin

    # Image processing
    image: Optional[np.ndarray]
    face_metadata: Optional[Dict]
    aligned_face: Optional[np.ndarray]
    skin_mask: Optional[np.ndarray]
    regions: Optional[Dict[str, np.ndarray]]

    # Quality gate
    quality_check_passed: bool
    quality_errors: Optional[List[str]]

    # Parallel analysis results
    analysis: Optional[Dict[str, Any]]

    # Aggregated results
    aggregated_analysis: Optional[Dict]
    skin_type: Optional[str]
    overall_score: Optional[int]

    # Recommendations & LLM output
    recommendations: Optional[List[Dict]]
    explanation: Optional[str]
    summary: Optional[str]
    interactions: Optional[List[Dict]]
    home_remedies: Optional[str]
    wishing_message: Optional[str]

    # Final response
    response: Optional[Dict]

    # Error handling
    errors: Optional[List[str]]
    current_error: Optional[str]
    is_error_state: bool
```

Each node only modifies the fields it owns.

---

## Workflow Graph

```
START → Decode Image
         ↓
       Detect Face
         ↓
       Validate Face ──→ ERROR (no face, multiple faces, too small, low res)
         ↓
       Align Face
         ↓
       Parse Face
         ↓
       Quality Gate ──→ ERROR (poor lighting, blur, occlusion)
         ↓
       Parallel Analysis (9 analyzers concurrently)
         ↓
       Aggregator ──→ ERROR (no analysis results)
         ↓
       Skin Type Determination
         ↓
       Recommendation Engine
         ↓
       LLM Explanation ──→ deterministic fallback on failure
         ↓
       Response Builder ──→ END
```

All conditional edges route to Error Handler when `is_error_state == True`.

---

## Node Specifications

### 1. Image Decoder
- **Input:** raw image bytes
- **Output:** numpy array (RGB)
- **Failure:** invalid / corrupt image → `unsupported_image_format`

### 2. Face Detector
- **Model:** InsightFace (buffalo_l)
- **Output:** bbox, landmarks, confidence
- **State:** `face_metadata`

### 3. Face Validator
- **Checks:** single face, minimum face size, minimum resolution
- **Failures:** `no_face_detected`, `multiple_faces_detected`, `face_too_small`, `low_resolution`

### 4. Face Aligner
- **Model:** InsightFace (get_aligner)
- **Output:** 256×256 aligned face
- **State:** `aligned_face`

### 5. Face Parser
- **Model:** Face Parsing (CelebAMask-HQ / BiSeNet)
- **Output:** skin mask, region masks (forehead, cheeks, chin, nose)
- **State:** `skin_mask`, `regions`

### 6. Quality Gate
- **Checks:** brightness, blur (Laplacian), occlusion ratio, parser confidence
- **Failures:** `poor_lighting`, `excessive_blur`

### 7. Parallel Analyzers (ThreadPoolExecutor)
All analyzers receive `(aligned_face, skin_mask, regions)` and run concurrently:

| Analyzer       | Output Type                    | Range / Values                      |
|----------------|--------------------------------|-------------------------------------|
| Oiliness       | int                            | 0–100                               |
| Hydration      | int                            | 0–100                               |
| Redness        | RednessLevel (enum)            | Low / Moderate / High               |
| Pigmentation   | PigmentationLevel (enum)       | None / Mild / Moderate / Severe     |
| Acne           | AcneAnalysis (severity + count)| None / Mild / Moderate / Severe     |
| Wrinkles       | WrinkleLevel (enum)            | Minimal / Mild / Moderate / Severe  |
| Pores          | PoreSize (enum)                | Small / Medium / Large              |
| Texture        | int                            | 0–100 (higher = smoother)           |
| Skin Tone      | str (hex color)                | Educational reference only          |

### 8. Aggregator
- Merges all analyzer outputs into a single `Dict[str, Any]`
- Calculates `overall_score` from weighted metrics
- Determines `skin_type` from oiliness + hydration + pore data

### 9. Recommendation Engine
- **Pure deterministic rules** (used only as LLM fallback)
- Maps analysis metrics to ingredient suggestions
- Produces: `List[IngredientRecommendation]`

### 10. LLM Explainer
- **Only node that calls an external LLM**
- Uses LangChain `ChatMistralAI` or `ChatGoogleGenerativeAI` with `.with_structured_output()`
- Pydantic output model:

```python
class LLMOutput(BaseModel):
    explanation: str
    summary: str
    recommendations: list[Recommendation]
    interactions: list[Interaction]
    home_remedies: str
    wishing_message: str
```

- Prompt includes: analysis metrics, user-provided info (age, skin type, gender, sensitivity)
- Falls back to deterministic `_generate_deterministic_summary()` if LLM unavailable
- **LLM is instructed to:**
  - Educate, explain, summarize
  - Include home remedies and a friendly wishing message
  - Acknowledge AI limitations
  - Emphasize individual uniqueness, avoid race/ethnicity discrimination
  - **NOT** diagnose, prescribe, or invent observations

### 11. Response Builder
- Converts state into `AnalysisResponse` Pydantic model
- Fields: `overall_score`, `skin_type`, `analysis`, `recommendations`, `interactions`, `summary`, `home_remedies`, `wishing_message`, `disclaimer`

### 12. Error Handler
- Catches all errors from conditional edges
- Returns structured error response with `code`, `message`, `user_message`

---

## API

### `POST /api/v1/analyze`

**Content-Type:** `multipart/form-data`

| Field           | Type   | Required | Description                                   |
|-----------------|--------|----------|-----------------------------------------------|
| `file`          | File   | Yes      | Image (JPG, JPEG, PNG, WEBP, max 10 MB)      |
| `age_group`     | String | No       | `18-24`, `25-30`, `31-40`, `41-50`, `50+`   |
| `skin_type_self`| String | No       | `Oily`, `Dry`, `Combination`                 |
| `gender`        | String | No       | `Male`, `Female`, `Non-binary / Other`       |
| `sensitive_skin`| String | No       | `Yes`, `No`, `Sometimes`                     |

### Response (200)

```json
{
  "overall_score": 75,
  "skin_type": "Combination",
  "analysis": { "oiliness": 65, "hydration": 50, ... },
  "recommendations": [...],
  "interactions": [...],
  "summary": "...",
  "home_remedies": "...",
  "wishing_message": "...",
  "disclaimer": "This analysis is AI-generated..."
}
```

### Error Response (4xx / 5xx)

```json
{
  "error": {
    "code": "poor_lighting",
    "message": "Image has poor lighting conditions",
    "user_message": "Poor lighting"
  },
  "success": false
}
```

### Rate Limiting

- **1 request per 60 seconds per IP**
- Returns HTTP 429 with `Retry-After` header and `rate_limit_exceeded` error code
- In-memory sliding-window implementation (`app/core/ratelimit.py`)

---

## Performance Targets

| Stage             | Target   |
|-------------------|----------|
| Decode            | <20 ms   |
| Face Detection    | <80 ms   |
| Alignment         | <20 ms   |
| Parsing           | <150 ms  |
| Parallel Analysis | <300 ms  |
| Aggregation       | <10 ms   |
| Recommendation    | <10 ms   |
| Response Builder  | <10 ms   |
| **Pipeline total**| **<1 s** |

LLM generation is excluded (typically 2–5 s depending on provider).

---

## Error Handling

| Code                       | Condition                         |
|----------------------------|-----------------------------------|
| `no_face_detected`         | InsightFace returns no faces      |
| `multiple_faces_detected`  | More than 1 face in frame         |
| `face_too_small`           | Bounding box below minimum        |
| `low_resolution`           | Image below 256×256 px            |
| `poor_lighting`            | Brightness check failed           |
| `excessive_blur`           | Laplacian variance too low        |
| `unsupported_image_format` | Extension not in allowed list     |
| `image_too_large`          | Exceeds `MAX_IMAGE_SIZE_BYTES`    |
| `rate_limit_exceeded`      | More than 1 POST per 60s per IP   |
| `internal_error`           | Unhandled exception in pipeline   |

---

## Frontend Routes

| Path          | View          | Description                        |
|---------------|---------------|------------------------------------|
| `/`           | HomeView      | Hero, steps, CTA                   |
| `/analyze`    | AnalyzeView   | Questionnaire + ImageUpload/Camera |
| `/results`    | ResultsView   | Analysis results dashboard         |
| `/about`      | AboutView     | About / disclaimers                |
| `/:pathMatch(.*)*` | NotFoundView | 404 page                       |

---

## Frontend Components

| Component           | Purpose                                         |
|---------------------|-------------------------------------------------|
| `ImageUpload.vue`   | File upload (drag & drop), camera capture       |
| `SkinQuestionnaire.vue` | Pill-based form for age, skin type, gender, sensitivity |
| `TheHeader.vue`     | Glass-effect navbar with logo                   |
| `TheFooter.vue`     | Footer with links                               |

---

## Future Graph Extensions

New analyzers can be added without modifying existing nodes:

- Eye bags / dark circles
- Acne scars
- UV damage estimation
- Skin elasticity
- Facial symmetry
- Skincare routine generator
- Product recommendation engine
- Progress tracking over time (requires persistence)
- Before/after comparison
- Explainability heatmaps

Each becomes a new node in the parallel analyzer stage, followed by aggregation.

---

## Guiding Principle

LangGraph is used as an **orchestration framework** — not as an autonomous agent.

Computer vision models produce measurements. The recommendation engine applies deterministic skincare rules. The LLM's sole responsibility is to transform structured outputs into clear, educational explanations while respecting medical safety constraints.
