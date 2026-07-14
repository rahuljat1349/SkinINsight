<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysisStore'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ImageUpload from '@/components/ImageUpload.vue'
import SkinQuestionnaire from '@/components/SkinQuestionnaire.vue'

const router = useRouter()
const store = useAnalysisStore()

const showQuestions = ref(false)
const hasFile = computed(() => !!store.uploadState.file)
const isAnalyzing = computed(() => store.analysisState.isLoading)

const handleAnalyze = async () => {
  if (!hasFile.value) return
  try {
    await store.analyzeImage()
    router.push({ name: 'results' })
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}

const onNext = () => {
  showQuestions.value = true
}

onMounted(() => {
  document.addEventListener('__next', onNext)
})

onUnmounted(() => {
  document.removeEventListener('__next', onNext)
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

      <!-- Error Alert -->
      <div v-if="store.analysisState.error" class="error-alert">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <div class="error-content">
          <h4>Analysis Error</h4>
          <p>{{ store.analysisState.error?.error?.user_message || 'An unknown error occurred' }}</p>
        </div>
        <button @click="store.setAnalysisError(null)" class="error-close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Upload / Questionnaire / Loading Card -->
      <div class="upload-card">
        <template v-if="!showQuestions && !isAnalyzing">
          <ImageUpload />
        </template>

        <template v-else-if="showQuestions && !isAnalyzing">
          <div class="section-divider">
            <span>Tell us about yourself</span>
          </div>
          <SkinQuestionnaire @analyze="handleAnalyze" />
        </template>

        <template v-else>
          <div class="analyzing-card">
            <div class="big-spinner"></div>
            <h3>Analyzing your skin...</h3>
            <p>This usually takes a few seconds.</p>
          </div>
        </template>
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.section-divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.section-divider::before,
.section-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* Analyzing state */
.analyzing-card {
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-md);
}

.analyzing-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.analyzing-card p {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.big-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto 1rem;
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
  min-height: 400px;
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
  .upload-card { min-height: 340px; padding: 1.25rem; }
}

@media (max-width: 480px) {
  .req-grid { grid-template-columns: 1fr; }
}
</style>
