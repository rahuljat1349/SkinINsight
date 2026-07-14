<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'

const store = useAnalysisStore()

const fileInput = ref<HTMLInputElement | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)
const stream = ref<MediaStream | null>(null)
const cameraMode = ref(false)
const cameraError = ref<string | null>(null)
const capturedPreview = ref<string | null>(null)
const capturedBlob = ref<Blob | null>(null)

// Computed properties
const isDragging = computed(() => store.uploadState.isDragging)
const previewUrl = computed(() => store.uploadState.previewUrl)
const hasFile = computed(() => !!store.uploadState.file)
const validationError = computed(() => store.uploadState.validationError)
const isProcessing = computed(() => store.uploadState.isProcessing)
const uploadProgress = computed(() => store.uploadState.uploadProgress)

// Cleanup camera on unmount
onUnmounted(() => stopCamera())

// --- Camera ---
const startCamera = async () => {
  cameraError.value = null
  cameraMode.value = true
  try {
    const s = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' }
    })
    stream.value = s
    if (videoRef.value) {
      videoRef.value.srcObject = s
    }
  } catch (err: any) {
    cameraError.value = err.message || 'Camera access denied. Please allow camera permissions.'
    cameraMode.value = false
  }
}

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(t => t.stop())
    stream.value = null
  }
  cameraMode.value = false
  cameraError.value = null
}

const capturePhoto = () => {
  const video = videoRef.value
  if (!video || !stream.value) return

  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.drawImage(video, 0, 0)
  canvas.toBlob((blob) => {
    if (!blob) return

    capturedBlob.value = blob
    capturedPreview.value = URL.createObjectURL(blob)

    const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
    const { valid, error } = store.validateImage(file)
    if (!valid && error) {
      store.setValidationError(error)
      return
    }
    store.setFile(file)
    stopCamera()
  }, 'image/jpeg', 0.92)
}

const switchToUpload = () => {
  stopCamera()
  capturedPreview.value = null
  capturedBlob.value = null
  if (!hasFile) {
    store.setFile(null)
  }
}

// --- File handling ---
const handleDragOver = (e: DragEvent) => {
  if (cameraMode.value) return
  e.preventDefault()
  store.setDragging(true)
}

const handleDragLeave = (e: DragEvent) => {
  if (cameraMode.value) return
  e.preventDefault()
  store.setDragging(false)
}

const handleDrop = (e: DragEvent) => {
  if (cameraMode.value) return
  e.preventDefault()
  store.setDragging(false)
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = (file: File) => {
  store.setValidationError(null)
  const { valid, error } = store.validateImage(file)
  if (!valid && error) {
    store.setValidationError(error)
    return
  }
  store.setFile(file)
}

const triggerFileInput = () => {
  if (cameraMode.value) return
  fileInput.value?.click()
}

const removeFile = () => {
  store.setFile(null)
  capturedPreview.value = null
  capturedBlob.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

watch(isProcessing, (processing) => {
  if (!processing) {
    store.setUploadProgress(0)
  }
})

const handleNext = () => {
  document.dispatchEvent(new CustomEvent('__next'))
}

</script>

<template>
  <div class="image-upload" :class="{ 'is-dragging': isDragging }" @dragover="handleDragOver" @dragleave="handleDragLeave" @drop="handleDrop">
    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/jpg,image/png,image/webp"
      @change="handleFileChange"
      class="file-input"
      :disabled="isProcessing"
    />

    <!-- Mode toggle -->
    <div class="mode-toggle" v-if="!hasFile && !isProcessing">
      <button
        class="mode-btn"
        :class="{ active: !cameraMode }"
        @click="switchToUpload"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        Upload
      </button>
      <button
        class="mode-btn"
        :class="{ active: cameraMode }"
        @click="startCamera"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
          <circle cx="12" cy="13" r="4" />
        </svg>
        Camera
      </button>
    </div>

    <!-- Upload area -->
    <div
      class="upload-area"
      @click="triggerFileInput"
      :class="{
        'has-file': hasFile,
        'has-error': validationError || cameraError,
        'is-processing': isProcessing,
        'is-camera': cameraMode && !hasFile
      }"
    >
      <!-- Camera view -->
      <div v-if="cameraMode && !hasFile && !cameraError" class="camera-view" @click.stop>
        <video ref="videoRef" autoplay playsinline class="camera-video"></video>
        <button class="capture-btn" @click="capturePhoto" title="Capture photo">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="9" fill="currentColor" opacity="0.2" />
            <circle cx="12" cy="12" r="9" />
            <circle cx="12" cy="12" r="4" />
          </svg>
        </button>
        <button class="camera-close" @click="switchToUpload" title="Close camera">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Camera error -->
      <div v-else-if="cameraError && !hasFile" class="error-state">
        <svg class="error-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
          <line x1="1" y1="1" x2="23" y2="23" />
        </svg>
        <p class="error-text">{{ cameraError }}</p>
        <p class="error-hint">Click "Upload" to choose a file instead</p>
      </div>

      <!-- Processing state -->
      <div v-else-if="isProcessing" class="processing-state">
        <div class="spinner"></div>
        <p class="processing-text">Analyzing your image...</p>
        <div v-if="uploadProgress > 0" class="progress-bar">
          <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
        </div>
      </div>

      <!-- Preview (file or captured) -->
      <div v-else-if="previewUrl">
        <div class="preview-container">
          <img :src="previewUrl" alt="Preview" class="preview-image" />
          <button class="remove-btn" @click.stop="removeFile" title="Remove image">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        </div>
        <div class="next-wrapper">
          <button class="next-btn" @click="handleNext">
            <span>Next</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Validation error -->
      <div v-else-if="validationError && !cameraMode" class="error-state">
        <svg class="error-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <p class="error-text">{{ validationError }}</p>
        <p class="error-hint">Click to try again</p>
      </div>

      <!-- Default upload state -->
      <div v-else class="default-state">
        <svg class="upload-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        <h3 class="upload-title">Upload Your Photo</h3>
        <p class="upload-hint">
          Drag & drop your facial image here, or click to browse
        </p>
        <ul class="requirements">
          <li>JPG, JPEG, PNG, or WEBP format</li>
          <li>Maximum 10MB</li>
          <li>One clearly visible face</li>
          <li>Good lighting, minimal blur</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.image-upload {
  position: relative;
}

.file-input {
  display: none;
}

.upload-area {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--surface);
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.upload-area:hover {
  border-color: var(--primary);
  background: var(--background);
}

.upload-area.is-dragging {
  border-color: var(--primary);
  background: rgba(99, 102, 241, 0.05);
}

.upload-area.has-error {
  border-color: var(--error);
  background: rgba(239, 68, 68, 0.05);
}

.upload-area.is-processing {
  cursor: default;
  pointer-events: none;
}

/* Preview */
.preview-container {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.preview-image {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: block;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: var(--error);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.remove-btn:hover {
  background: #dc2626;
  transform: scale(1.05);
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}

/* Next button below image */
.next-wrapper {
  text-align: center;
  margin-top: 1rem;
}

.next-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--t-base);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25);
}

.next-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
}

/* Processing State */
.processing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.processing-text {
  color: var(--text-secondary);
  font-weight: 500;
}

.progress-bar {
  width: 200px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--error);
}

.error-icon {
  color: var(--error);
  opacity: 0.8;
}

.error-text {
  font-weight: 500;
  color: var(--error);
}

.error-hint {
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* Default State */
.default-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  color: var(--primary);
  opacity: 0.8;
}

.upload-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.upload-hint {
  color: var(--text-secondary);
}

.requirements {
  margin-top: 1rem;
  padding: 0;
  list-style: none;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.requirements li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.requirements li::before {
  content: '\\2022';
  color: var(--primary);
}

@media (max-width: 768px) {
/* Mode toggle */
.mode-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn.active {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(99, 102, 241, 0.06);
}

.mode-btn:hover {
  border-color: var(--primary);
}

/* Camera view */
.camera-view {
  width: 100%;
  max-width: 400px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.camera-video {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  background: #000;
}

.capture-btn {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 4px solid white;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.capture-btn:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.05);
}

.capture-btn svg {
  color: white;
}

.camera-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.camera-close:hover {
  background: rgba(0, 0, 0, 0.7);
}

.upload-area {
    padding: 1.5rem;
    min-height: 250px;
  }
  
  .preview-container {
    height: 250px;
  }
  
  .upload-title {
    font-size: 1.125rem;
  }
}
</style>
