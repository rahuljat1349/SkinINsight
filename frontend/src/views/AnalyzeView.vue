<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysisStore'
import { ref, computed, watch, onMounted } from 'vue'
import ImageUpload from '@/components/ImageUpload.vue'
import SkinQuestionnaire from '@/components/SkinQuestionnaire.vue'

const router = useRouter()
const store = useAnalysisStore()
const step = ref(1)

const hasFile = computed(() => !!store.uploadState.file)
const isAnalyzing = computed(() => store.analysisState.isLoading)

const hasAllInfo = computed(() =>
  store.userInfo.age_group &&
  store.userInfo.skin_type_self &&
  store.userInfo.gender &&
  store.userInfo.sensitive_skin
)

const canAnalyze = computed(() => hasFile.value && hasAllInfo.value && !isAnalyzing.value)

// Auto-advance to step 2 when a file is selected
watch(hasFile, (val) => {
  if (val && step.value === 1) step.value = 2
})

const handleAnalyze = async () => {
  if (!canAnalyze.value) return
  try {
    await store.analyzeImage()
    router.push({ name: 'results' })
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}

onMounted(() => {
  store.clear()
  step.value = 1
})
</script>

<template>
  <div class="analyze-view">
    <div class="container container-narrow">
      <!-- Header -->
      <div class="page-header">
        <h1 class="page-title">Analyze Your Skin</h1>
        <p class="page-subtitle">
          Upload a photo and tell us about yourself for a personalized skin analysis.
        </p>
      </div>

      <!-- Step indicator -->
      <div class="steps-bar">
        <div class="step-dot" :class="{ active: step >= 1, done: step > 1 }">
          <span v-if="step > 1" class="step-check">&#10003;</span>
          <span v-else class="step-num">1</span>
          <p class="step-label">Upload Photo</p>
        </div>
        <div class="step-line" :class="{ done: step > 1 }"></div>
        <div class="step-dot" :class="{ active: step >= 2 }">
          <span class="step-num">2</span>
          <p class="step-label">About You</p>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="store.analysisState.error" class="error-alert">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <div class="error-content">
          <h4>Analysis Error</h4>
          <p>{{ store.analysisState.error.error.user_message }}</p>
        </div>
        <button @click="store.setAnalysisError(null)" class="error-close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Step 1: Upload -->
      <div v-if="step === 1" class="step-panel">
        <div class="upload-card">
          <ImageUpload />
        </div>
      </div>

      <!-- Step 2: Questionnaire + Analyze -->
      <div v-if="step === 2" class="step-panel">
        <SkinQuestionnaire />

        <button
          class="continue-btn"
          :disabled="!canAnalyze"
          @click="handleAnalyze"
        >
          <template v-if="isAnalyzing">
            <span class="btn-spinner"></span>
            Analyzing...
          </template>
          <template v-else>
            Analyze My Skin
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </template>
        </button>
        <p v-if="!hasAllInfo && hasFile" class="continue-hint">Please answer all questions above to continue.</p>

        <button class="back-link" @click="step = 1">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Choose a different photo
        </button>
      </div>

      <!-- Requirements -->
      <section class="requirements-section">
        <h2 class="section-title">For Best Results</h2>
        <p class="section-subtitle">Follow these guidelines to ensure accurate analysis.</p>
        <div class="req-grid">
          <div class="req-card">
            <div class="req-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
            <h4>Image Format</h4>
            <p>JPG, JPEG, PNG, or WEBP</p>
          </div>
          <div class="req-card">
            <div class="req-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M20 7h-9" />
                <path d="M14 17H5" />
                <circle cx="17" cy="17" r="3" />
                <circle cx="7" cy="7" r="3" />
              </svg>
            </div>
            <h4>File Size</h4>
            <p>Max 10MB, min 256×256 px</p>
          </div>
          <div class="req-card">
            <div class="req-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <circle cx="12" cy="12" r="10" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </div>
            <h4>One Face</h4>
            <p>Only one face should be visible</p>
          </div>
          <div class="req-card">
            <div class="req-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                <circle cx="12" cy="12" r="4" />
              </svg>
            </div>
            <h4>Frontal Pose</h4>
            <p>Face the camera directly</p>
          </div>
          <div class="req-card">
            <div class="req-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                <path d="M9 18l6-6-6-6" />
              </svg>
            </div>
            <h4>Good Lighting</h4>
            <p>Avoid harsh shadows</p>
          </div>
          <div class="req-card">
            <div class="req-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                <polyline points="7.5 4.21 12 6.81 16.5 4.21" />
                <polyline points="7.5 19.79 7.5 14.6 3 12" />
                <polyline points="21 12 16.5 19.79 16.5 14.6" />
                <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                <line x1="12" y1="22.08" x2="12" y2="12" />
              </svg>
            </div>
            <h4>Minimal Blur</h4>
            <p>Photo must be in focus</p>
          </div>
        </div>
      </section>

      <!-- Privacy -->
      <div class="privacy-card">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
        <div>
          <h4>Your Privacy Matters</h4>
          <p>Images are processed in memory and never stored. Your data stays private.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analyze-view {
  padding: 1rem 0 4rem;
}

.container-narrow {
  max-width: 800px;
}

/* Header */
.page-header {
  text-align: center;
  padding: 2rem 0 1.5rem;
}

.page-title {
  font-size: 2.25rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  max-width: 520px;
  margin: 0 auto;
}

/* Steps Bar */
.steps-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 2rem;
}

.step-dot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.step-num,
.step-check {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 700;
  border: 2px solid var(--border);
  color: var(--text-muted);
  background: var(--surface);
  transition: all var(--t-base);
}

.step-dot.active .step-num {
  border-color: var(--primary);
  background: var(--primary);
  color: #fff;
}

.step-dot.done .step-check {
  border-color: var(--primary);
  background: var(--primary);
  color: #fff;
}

.step-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
  white-space: nowrap;
}

.step-dot.active .step-label {
  color: var(--primary);
  font-weight: 600;
}

.step-line {
  width: 60px;
  height: 2px;
  background: var(--border);
  margin: 0 0.5rem;
  margin-bottom: 1.5rem;
  transition: background var(--t-base);
}

.step-line.done {
  background: var(--primary);
}

/* Step panels */
.step-panel {
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Button spinner */
.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Continue button */
.continue-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
  padding: 0.875rem 1.5rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--t-base);
}

.continue-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.continue-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.continue-hint {
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
}

/* Back link */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  transition: color var(--t-fast);
  margin-top: 1rem;
}

.back-link:hover {
  color: var(--primary);
}

/* Error Alert */
.error-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: var(--error-light);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--r-md);
  color: var(--error);
  margin-bottom: 1.5rem;
  position: relative;
}

.error-alert svg { flex-shrink: 0; margin-top: 2px; }

.error-content h4 { font-size: 0.95rem; font-weight: 600; margin-bottom: 0.15rem; }
.error-content p { font-size: 0.875rem; color: var(--text-secondary); }

.error-close {
  position: absolute; top: 0.5rem; right: 0.5rem;
  color: var(--error); padding: 0.25rem; border-radius: var(--r-sm);
  transition: background var(--t-fast);
  display: flex;
}
.error-close:hover { background: rgba(239, 68, 68, 0.15); }

/* Upload Card */
.upload-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: var(--sp-xl);
  box-shadow: var(--shadow-md);
}

/* Requirements */
.requirements-section {
  padding: 2.5rem 0 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 0.35rem;
}

.section-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: var(--sp-lg);
}

.req-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.req-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all var(--t-base);
}

.req-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.req-icon {
  width: 40px;
  height: 40px;
  background: rgba(99, 102, 241, 0.06);
  border-radius: var(--r-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  flex-shrink: 0;
}

.req-card h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.1rem;
}

.req-card p {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Privacy */
.privacy-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  max-width: 500px;
  margin: 0 auto;
}

.privacy-card svg {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--primary);
}

.privacy-card h4 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.privacy-card p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title { font-size: 1.75rem; }
  .req-grid { grid-template-columns: repeat(2, 1fr); }
  .privacy-card { flex-direction: column; text-align: center; }
}

@media (max-width: 480px) {
  .req-grid { grid-template-columns: 1fr; }
}
</style>
