<script setup lang="ts">
import { useAnalysisStore } from '@/stores/analysisStore'
import { ref, watch, onMounted, onUnmounted } from 'vue'
import ImageUpload from '@/components/ImageUpload.vue'
import SkinQuestionnaire from '@/components/SkinQuestionnaire.vue'
import ResultsView from '@/views/ResultsView.vue'

const store = useAnalysisStore()

const showQuestions = ref(false)
const showResults = ref(false)
const isAnalyzing = ref(false)

watch(() => store.analysisState.data, (data) => {
  if (!data && showResults.value) {
    showResults.value = false
    showQuestions.value = false
  }
})

const scrollToUpload = () => {
  document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })
}

const handleNext = () => {
  showQuestions.value = true
}

const handleAnalyze = async () => {
  isAnalyzing.value = true
  try {
    await store.analyzeImage()
    showResults.value = true
    showQuestions.value = false
  } catch (error) {
    console.error('Analysis failed:', error)
  } finally {
    isAnalyzing.value = false
  }
}

const resetAll = () => {
  store.clear()
  showQuestions.value = false
  showResults.value = false
}

onMounted(() => document.addEventListener('__next', handleNext))
onUnmounted(() => document.removeEventListener('__next', handleNext))
</script>

<template>
  <div class="home-view">
    <!-- Hero -->
    <section class="hero">
      <div class="container">
        <div class="hero-grid">
          <div class="hero-content">
            <span class="hero-badge">AI-Powered Skin Analysis</span>
            <h1 class="hero-title">
              <span class="text-gradient">Discover</span> Your Skin's True Potential
            </h1>
            <p class="hero-subtitle">
              Upload a photo and get a comprehensive analysis of your skin type, condition,
              and personalized ingredient recommendations — all powered by AI.
            </p>
            <div class="hero-actions">
              <button class="btn btn-primary btn-lg" @click="scrollToUpload">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Start Analysis
              </button>
              <RouterLink to="/about" class="btn btn-ghost btn-lg">
                Learn More
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </RouterLink>
            </div>
            <div class="hero-note">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
              <span>This is an educational tool — not a medical diagnosis.</span>
            </div>
          </div>
          <div class="hero-visual">
            <div class="hero-glow"></div>
            <div class="hero-graphic">
              <svg viewBox="0 0 200 200" fill="none">
                <defs>
                  <linearGradient id="hg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#6366f1" stop-opacity="0.15" />
                    <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.08" />
                  </linearGradient>
                </defs>
                <circle cx="100" cy="100" r="90" fill="url(#hg)" stroke="var(--border)" stroke-width="1" />
                <circle cx="100" cy="100" r="65" fill="none" stroke="var(--border)" stroke-width="0.8" stroke-dasharray="4 6" />
                <circle cx="100" cy="100" r="40" fill="none" stroke="var(--border)" stroke-width="0.6" stroke-dasharray="2 4" />
                <circle cx="100" cy="100" r="20" fill="var(--primary)" opacity="0.08" />
                <path d="M100 40 A60 60 0 0 1 152 62" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" opacity="0.6" />
                <path d="M100 160 A60 60 0 0 1 48 138" stroke="var(--secondary)" stroke-width="2" stroke-linecap="round" opacity="0.6" />
                <circle cx="100" cy="100" r="6" fill="var(--primary)" opacity="0.3" />
                <circle cx="140" cy="75" r="3" fill="var(--primary)" opacity="0.4" />
                <circle cx="65" cy="130" r="4" fill="var(--secondary)" opacity="0.35" />
                <circle cx="135" cy="130" r="2.5" fill="var(--warning)" opacity="0.3" />
                <circle cx="70" cy="72" r="3.5" fill="var(--success)" opacity="0.3" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Upload / Questions / Results -->
    <section class="upload-section" id="upload-section">
      <div class="container">
        <div v-if="!showResults" class="upload-card">
          <h2 class="section-title">Get Started</h2>
          <p class="section-subtitle">
            Upload a clear photo of your face to begin your skin analysis journey.
          </p>
          <div class="upload-wrapper">
            <template v-if="!showQuestions && !isAnalyzing">
              <ImageUpload />
            </template>
            <template v-else-if="showQuestions && !isAnalyzing">
              <SkinQuestionnaire @analyze="handleAnalyze" />
            </template>
            <template v-else>
              <div class="analyzing-state">
                <div class="spinner"></div>
                <p>Analyzing your skin...</p>
              </div>
            </template>
          </div>
          <div v-if="!store.uploadState.file && !showQuestions && !isAnalyzing" class="features-row">
            <div class="feature-item">
              <div class="feature-icon icon-skin">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                  <line x1="9" y1="9" x2="9.01" y2="9" />
                  <line x1="15" y1="9" x2="15.01" y2="9" />
                </svg>
              </div>
              <div>
                <h4>Skin Type</h4>
                <p>Oily, Dry, Combination, or Normal</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon icon-analysis">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </div>
              <div>
                <h4>Deep Analysis</h4>
                <p>Oiliness, hydration, pores, and more</p>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon icon-recs">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              </div>
              <div>
                <h4>Recommendations</h4>
                <p>Personalized ingredients and routines</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="results-container">
          <ResultsView />
          <div class="reset-bar">
            <button class="btn btn-ghost" @click="resetAll">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="1 4 1 10 7 10" />
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
              </svg>
              Start New Analysis
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section v-if="!showResults" class="steps-section">
      <div class="container">
        <h2 class="section-title">How It Works</h2>
        <p class="section-subtitle">Three simple steps to get your personalized skin analysis.</p>
        <div class="steps-row">
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <h4>Upload Photo</h4>
            <p>Take or upload a clear, well-lit photo of your face.</p>
          </div>
          <div class="steps-connector">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <h4>AI Analysis</h4>
            <p>Our computer vision models analyze your skin characteristics.</p>
          </div>
          <div class="steps-connector">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </div>
            <h4>Get Results</h4>
            <p>Receive insights, scores, and ingredient recommendations.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
}

/* ── Hero ── */

.hero {
  position: relative;
  padding: 3rem 0 4rem;
  overflow: hidden;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  background: rgba(99, 102, 241, 0.08);
  padding: 0.35rem 0.85rem;
  border-radius: var(--r-full);
  width: fit-content;
  letter-spacing: 0.01em;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.text-gradient {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.15rem;
  color: var(--text-secondary);
  line-height: 1.7;
  max-width: 520px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.hero-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.825rem;
  padding: 0.75rem 1rem;
  background: rgba(245, 158, 11, 0.06);
  border-radius: var(--r-md);
  width: fit-content;
}

.hero-note svg {
  flex-shrink: 0;
  color: var(--warning);
}

/* Hero Visual */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.hero-glow {
  position: absolute;
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 4s ease-in-out infinite;
}

.hero-graphic {
  position: relative;
  width: 280px;
  height: 280px;
}

.hero-graphic svg {
  width: 100%;
  height: 100%;
  animation: float 5s ease-in-out infinite;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: var(--r-md);
  transition: all var(--t-base);
  cursor: pointer;
}

.btn-lg {
  padding: 0.75rem 1.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.btn-ghost:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(99, 102, 241, 0.04);
}

/* ── Upload Section ── */

.upload-section {
  padding: 2rem 0 4rem;
}

.upload-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: var(--sp-2xl);
  text-align: center;
  box-shadow: var(--shadow-md);
}

.upload-wrapper {
  max-width: 550px;
  margin: 0 auto;
}

.features-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-top: var(--sp-xl);
  padding-top: var(--sp-xl);
  border-top: 1px solid var(--border);
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  text-align: left;
}

.feature-item h4 {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
}

.feature-item p {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon.icon-skin {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary);
}

.feature-icon.icon-analysis {
  background: rgba(139, 92, 246, 0.1);
  color: var(--secondary);
}

.feature-icon.icon-recs {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

/* ── Steps ── */

.steps-section {
  padding: 2rem 0 5rem;
}

.steps-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.step-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: var(--sp-lg);
  text-align: center;
  flex: 1;
  max-width: 280px;
  position: relative;
  transition: all var(--t-base);
}

.step-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}

.step-num {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.step-icon {
  width: 52px;
  height: 52px;
  margin: 0.5rem auto 0.75rem;
  background: rgba(99, 102, 241, 0.06);
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.step-card h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.step-card p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.steps-connector {
  color: var(--text-muted);
  opacity: 0.5;
  flex-shrink: 0;
}

/* ── Responsive ── */

@media (max-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
  .hero-content { align-items: center; }
  .hero-subtitle { max-width: none; }
  .hero-badge { margin: 0 auto; }
  .hero-note { margin: 0 auto; }
  .hero-visual { display: none; }
  .features-row { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .hero { padding: 2rem 0 3rem; }
  .hero-title { font-size: 2.25rem; }
  .hero-actions { flex-direction: column; width: 100%; }
  .hero-actions .btn { width: 100%; justify-content: center; }
  .upload-card { padding: var(--sp-lg); }
  .steps-row { flex-direction: column; gap: 1rem; }
  .steps-connector { transform: rotate(90deg); }
  .step-card { max-width: none; width: 100%; }
}

/* Analyzing state */
.analyzing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 0;
}

.analyzing-state .spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.analyzing-state p {
  color: var(--text-secondary);
  font-weight: 500;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Results container */
.results-container {
  width: 100%;
}

.reset-bar {
  text-align: center;
  margin-top: 1.5rem;
}

.reset-bar .btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
