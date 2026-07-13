# CutiS - Testing Guide

This guide provides instructions for testing the complete CutiS application, including backend API and frontend integration.

## 🏗️ Prerequisites

### Backend Requirements
- Python 3.10+
- pip (package manager)
- Virtual environment (recommended)

### Frontend Requirements
- Node.js 18.0+
- npm 9.0+

## 📦 Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to project root
cd /path/to/skinpro

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- OpenCV (image processing)
- Pillow (image handling)
- NumPy (numerical computing)
- InsightFace (face detection)
- LangGraph (workflow orchestration)
- And other dependencies...

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Option 1: Manual Startup

**Backend (FastAPI):**
```bash
# In project root
source venv/bin/activate  # Activate venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Vue 3 + Vite):**
```bash
# In frontend directory
npm run dev
```

The application will be available at:
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

### Option 2: Using Startup Script

```bash
# Make executable and run
chmod +x start_dev.sh
./start_dev.sh
```

This will automatically:
1. Create venv if it doesn't exist
2. Install Python dependencies
3. Start backend server
4. Start frontend server
5. Display connection information

## 🧪 Testing the Application

### Backend API Testing

#### Health Check
```bash
curl http://localhost:8000/health
# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

#### Root Endpoint
```bash
curl http://localhost:8000/
# Expected response:
# {"name": "CutiS", "version": "1.0.0", "docs": "/docs"}
```

#### Image Analysis
```bash
# Using curl to upload an image
curl -X POST -F "file=@/path/to/your/face_photo.jpg" \
  http://localhost:8000/api/v1/analyze

# Expected response (success):
# {
#   "overall_score": 85,
#   "skin_type": "Combination",
#   "analysis": { ... },
#   "recommendations": [...],
#   "summary": "...",
#   "disclaimer": "..."
# }

# Expected response (error):
# {
#   "error": {
#     "code": "no_face_detected",
#     "message": "No face detected in the uploaded image",
#     "user_message": "We couldn't detect a face in your photo..."
#   },
#   "success": false
# }
```

### Using Python Test Script

```bash
# Run comprehensive test
python test_application.py
```

This will test:
- ✅ Health endpoints
- ✅ Image validation
- ✅ Error handling
- ✅ Performance
- ✅ API response structure

### Frontend Testing

1. Open your browser and navigate to `http://localhost:5173`
2. Click on "Analyze Your Skin" or navigate to `/analyze`
3. Upload a photo using:
   - File upload (drag & drop or click to browse)
   - Camera capture (if supported by your browser)
4. View the analysis results on the Results page

## 📸 Image Requirements

For best results, upload images that meet these criteria:

| Requirement | Details |
|-------------|---------|
| **Format** | JPG, JPEG, PNG, WEBP |
| **Size** | Maximum 10MB |
| **Resolution** | Minimum 256x256 pixels |
| **Faces** | Exactly one clearly visible face |
| **Pose** | Frontal (facing camera directly) |
| **Lighting** | Good, even lighting (no harsh shadows) |
| **Focus** | Sharp, in focus (no blur) |

## 🎯 Test Cases to Verify

### Backend Tests
- [ ] Health endpoint returns 200 OK
- [ ] Root endpoint returns application info
- [ ] API docs endpoint is accessible
- [ ] Invalid image format returns proper error
- [ ] Oversized image returns proper error
- [ ] No face detected returns proper error
- [ ] Multiple faces detected returns proper error
- [ ] Poor lighting returns proper error
- [ ] Excessive blur returns proper error

### Frontend Tests
- [ ] Home page loads correctly
- [ ] Navigation to Analyze page works
- [ ] Image upload component works
- [ ] Camera capture works (if supported)
- [ ] Upload progress is shown
- [ ] Error messages are displayed properly
- [ ] Results page shows analysis data
- [ ] Recommendations are displayed
- [ ] Summary is shown
- [ ] Responsive design on mobile

### Integration Tests
- [ ] Frontend can connect to backend API
- [ ] Image upload from frontend to backend works
- [ ] Error responses are handled gracefully
- [ ] Loading states work correctly
- [ ] FormData is properly constructed

## 🔧 Development Tips

### Common Issues and Solutions

**Issue: InsightFace models not found**
```bash
# The models will be automatically downloaded on first run
# If you get errors, try:
pip install --upgrade insightface
```

**Issue: Port 8000 already in use**
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

**Issue: Frontend can't connect to backend**
- Ensure backend is running
- Check CORS settings (should be configured for development)
- Verify API base URL in frontend (defaults to `/api`)

**Issue: Camera not working in browser**
- Ensure you're using HTTPS in production
- Check browser permissions
- Try a different browser

### Environment Variables

**Backend:**
```bash
# .env file
APP_NAME=CutiS
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000
MAX_IMAGE_SIZE_MB=10
INSIGHTFACE_MODEL_PATH=models/insightface
FACE_PARSING_MODEL_PATH=models/face_parsing
```

**Frontend:**
```bash
# .env file in frontend directory
VITE_API_BASE_URL=http://localhost:8000
```

## 📊 Performance Expectations

| Stage | Target Time |
|-------|-------------|
| Decode Image | < 20ms |
| Face Detection | < 80ms |
| Face Alignment | < 20ms |
| Face Parsing | < 150ms |
| Parallel Analysis | < 300ms |
| Recommendation Engine | < 10ms |
| Response Builder | < 10ms |
| **Total (excluding LLM)** | **< 700ms** |

## 🎨 Frontend Components

### Pages
- `HomeView.vue` - Landing page with introduction
- `AnalyzeView.vue` - Image upload and analysis page
- `ResultsView.vue` - Analysis results display
- `AboutView.vue` - About the application
- `NotFoundView.vue` - 404 page

### Components
- `ImageUpload.vue` - Drag & drop image uploader with camera support
- `TheHeader.vue` - Navigation header
- `TheFooter.vue` - Application footer
- Various UI components for displaying results

### Stores (Pinia)
- `analysisStore.ts` - Manages analysis state and API calls
- Handles image upload, progress tracking, error management

## 🔍 Debugging

### Backend Debugging
```bash
# Run with debug logging
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

### Frontend Debugging
```bash
# Run with debug mode
cd frontend
npm run dev
# Open browser dev tools (F12)
```

### API Testing with Python
```python
import requests

url = "http://localhost:8000/api/v1/analyze"
files = {'file': open('/path/to/photo.jpg', 'rb')}
response = requests.post(url, files=files)

if response.status_code == 200:
    result = response.json()
    print("Success:", result)
else:
    error = response.json()
    print("Error:", error)
```

## ✅ Verification Checklist

Before deploying to production, ensure all of these are working:

- [ ] Backend starts without errors
- [ ] All API endpoints are responsive
- [ ] Health checks pass
- [ ] Image validation works correctly
- [ ] Face detection works with real images
- [ ] Analysis pipeline completes successfully
- [ ] Error handling returns user-friendly messages
- [ ] Frontend loads without errors
- [ ] Image upload from frontend works
- [ ] Camera capture works (on supported devices)
- [ ] Results display correctly
- [ ] Responsive design works on mobile devices
- [ ] All error scenarios are handled gracefully
- [ ] Performance meets targets (< 1 second total)

## 🎯 Next Steps

1. **Test with real face images** - The backend will work with actual photos
2. **Fine-tune validation thresholds** - Adjust lighting/blur thresholds as needed
3. **Implement LLM integration** - Connect the ExplainerNode to actual LLM API
4. **Performance optimization** - Profile and optimize slow components
5. **Deployment** - Containerize with Docker and deploy to production

## 📞 Support

For issues or questions:
- Check this testing guide
- Review error messages in console logs
- Ensure all dependencies are installed
- Verify environment variables are set correctly
- Check browser console for frontend errors

---

**Last Updated:** 2026-07-09
**Version:** 2.0 (LangGraph)
