<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysisStore'
import { computed, onMounted } from 'vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

const router = useRouter()
const store = useAnalysisStore()

const analysisData = computed(() => store.analysisState.data)
const analysisImage = computed(() => store.analysisState.image)

onMounted(() => {
  if (!analysisData.value) {
    router.replace({ name: 'home' })
  }
})

const goHome = () => {
  store.clear()
  router.push({ name: 'home' })
}

const analyzeAgain = () => {
  store.clear()
  router.push({ name: 'home' })
}

const getScoreColor = (score: number) => {
  if (score >= 80) return 'var(--success)'
  if (score >= 60) return 'var(--warning)'
  return 'var(--error)'
}

const getScoreLabel = (score: number) => {
  if (score >= 80) return 'Excellent'
  if (score >= 60) return 'Good'
  if (score >= 40) return 'Fair'
  return 'Needs Improvement'
}

const getSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'none': case 'minimal': case 'low': return 'var(--success)'
    case 'mild': case 'medium': return 'var(--warning)'
    case 'moderate': case 'high': case 'severe': return 'var(--error)'
    default: return 'var(--text-secondary)'
  }
}
</script>

<template>
  <div class="results-view">
    <div class="container">
      <!-- Header -->
      <div class="results-header">
        <button @click="goHome" class="btn-back">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Home
        </button>
        <h1 class="results-title">Your Results</h1>
      </div>

      <!-- Disclaimer -->
      <div class="disclaimer-banner" v-if="analysisData">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <p>{{ analysisData.disclaimer }}</p>
      </div>

      <template v-if="analysisData">
        <!-- Score + Skin Type -->
        <section class="score-section">
          <div class="score-card">
            <div class="score-ring">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="44" fill="none" stroke="var(--border)" stroke-width="6" />
                <circle
                  cx="50" cy="50" r="44" fill="none"
                  :stroke="getScoreColor(analysisData.overall_score)"
                  stroke-width="6" stroke-linecap="round"
                  :stroke-dasharray="276.46"
                  :stroke-dashoffset="276.46 - (276.46 * analysisData.overall_score / 100)"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div class="score-inner">
                <span class="score-value">{{ analysisData.overall_score }}</span>
                <span class="score-max">/ 100</span>
              </div>
            </div>
            <div class="score-meta">
              <span class="score-label" :style="{ color: getScoreColor(analysisData.overall_score) }">
                {{ getScoreLabel(analysisData.overall_score) }}
              </span>
              <div class="skin-type-pill">
                <span>Skin Type</span>
                <strong>{{ analysisData.skin_type }}</strong>
              </div>
            </div>
          </div>
        </section>

        <!-- Image -->
        <section class="image-section" v-if="analysisImage">
          <div class="image-frame">
            <img :src="analysisImage" alt="Uploaded photo" />
          </div>
        </section>

        <!-- Analysis Grid -->
        <section class="analysis-section">
          <h2 class="section-heading">Analysis Details</h2>
          <div class="analysis-grid">
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
                </svg>
                <span>Oiliness</span>
              </div>
              <div class="metric-value">{{ analysisData.analysis.oiliness }}</div>
              <div class="metric-bar"><div class="bar-fill" :style="{ width: `${analysisData.analysis.oiliness}%` }"></div></div>
            </div>
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
                </svg>
                <span>Hydration</span>
              </div>
              <div class="metric-value">{{ analysisData.analysis.hydration }}</div>
              <div class="metric-bar"><div class="bar-fill fill-hydration" :style="{ width: `${analysisData.analysis.hydration}%` }"></div></div>
            </div>
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
                <span>Redness</span>
              </div>
              <div class="metric-value" :style="{ color: getSeverityColor(analysisData.analysis.redness) }">{{ analysisData.analysis.redness }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <circle cx="12" cy="12" r="6" />
                  <circle cx="12" cy="12" r="2" />
                </svg>
                <span>Pigmentation</span>
              </div>
              <div class="metric-value" :style="{ color: getSeverityColor(analysisData.analysis.pigmentation) }">{{ analysisData.analysis.pigmentation }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                  <line x1="9" y1="9" x2="9.01" y2="9" />
                  <line x1="15" y1="9" x2="15.01" y2="9" />
                </svg>
                <span>Acne</span>
              </div>
              <div class="metric-value" :style="{ color: getSeverityColor(analysisData.analysis.acne.severity) }">
                {{ analysisData.analysis.acne.severity }}
                <span v-if="analysisData.analysis.acne.count" class="count">({{ analysisData.analysis.acne.count }})</span>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 6v6l4 2" />
                </svg>
                <span>Wrinkles</span>
              </div>
              <div class="metric-value" :style="{ color: getSeverityColor(analysisData.analysis.wrinkles) }">{{ analysisData.analysis.wrinkles }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="3" />
                  <circle cx="12" cy="5" r="2" />
                  <circle cx="12" cy="19" r="2" />
                </svg>
                <span>Pores</span>
              </div>
              <div class="metric-value">{{ analysisData.analysis.pores }}</div>
            </div>
            <div class="metric-card" v-if="analysisData.analysis.texture">
              <div class="metric-header">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                </svg>
                <span>Texture</span>
              </div>
              <div class="metric-value">{{ analysisData.analysis.texture }}</div>
              <div class="metric-bar"><div class="bar-fill" :style="{ width: `${analysisData.analysis.texture}%` }"></div></div>
            </div>
          </div>
        </section>

        <!-- Summary -->
        <section class="summary-section" v-if="analysisData.summary">
          <h2 class="section-heading">AI Summary</h2>
          <div class="summary-card">
            <MarkdownRenderer :content="analysisData.summary" />
          </div>
        </section>

        <!-- Recommendations -->
        <section class="recs-section" v-if="analysisData.recommendations?.length">
          <h2 class="section-heading">Recommendations</h2>
          <p class="section-desc">
            Personalized ingredient suggestions based on your analysis.
          </p>
          <div class="recs-grid">
            <div
              v-for="(rec, i) in analysisData.recommendations"
              :key="`rec-${i}`"
              class="rec-card"
              :class="`priority-${rec.priority.toLowerCase()}`"
            >
              <div class="rec-top">
                <h4>{{ rec.ingredient }}</h4>
                <span class="rec-badge">{{ rec.priority }}</span>
              </div>
              <p class="rec-reason">{{ rec.reason }}</p>
              <div class="rec-meta" v-if="rec.suggested_frequency || rec.usage_notes">
                <p v-if="rec.suggested_frequency"><strong>Frequency:</strong> {{ rec.suggested_frequency }}</p>
                <p v-if="rec.usage_notes"><strong>Notes:</strong> {{ rec.usage_notes }}</p>
              </div>
              <div class="rec-caution" v-if="rec.precautions">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span>{{ rec.precautions }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Interactions -->
        <section class="interactions-section" v-if="analysisData.interactions?.length">
          <h2 class="section-heading">Ingredient Interactions</h2>
          <p class="section-desc">
            Which recommended ingredients to be mindful of when combining.
          </p>
          <div class="interactions-grid">
            <div
              v-for="(item, i) in analysisData.interactions"
              :key="`interact-${i}`"
              class="interaction-card"
            >
              <div class="interaction-pair">
                <span class="interaction-badge">{{ item.ingredients[0] }}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                <span class="interaction-badge">{{ item.ingredients[1] }}</span>
              </div>
              <p class="interaction-reason">{{ item.reason }}</p>
              <div class="interaction-suggestion">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4" />
                </svg>
                <span>{{ item.suggestion }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Home Remedies -->
        <section class="remedies-section" v-if="analysisData.home_remedies">
          <h2 class="section-heading">Home Remedies</h2>
          <p class="section-desc">Simple natural remedies you can try alongside your routine.</p>
          <div class="remedies-card">
            <MarkdownRenderer :content="analysisData.home_remedies" />
          </div>
        </section>

        <!-- Wishing Message -->
        <section class="wishing-section" v-if="analysisData.wishing_message">
          <div class="wishing-card">
            <MarkdownRenderer :content="analysisData.wishing_message" />
          </div>
        </section>

        <!-- Actions -->
        <div class="results-actions">
          <button @click="analyzeAgain" class="btn btn-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            Analyze Again
          </button>
          <button @click="goHome" class="btn btn-secondary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            Home
          </button>
        </div>
      </template>

      <!-- Empty state -->
      <div class="empty-state" v-else>
        <p>No analysis data available.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.results-view {
  padding: 0.5rem 0 4rem;
  animation: fadeIn 0.3s ease;
}

/* Header */
.results-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-top: 1rem;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  padding: 0.4rem 0.85rem;
  border-radius: var(--r-md);
  border: 1px solid var(--border);
  background: var(--surface);
  transition: all var(--t-fast);
}

.btn-back:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.results-title {
  font-size: 1.5rem;
  font-weight: 700;
}

/* Disclaimer */
.disclaimer-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(245, 158, 11, 0.06);
  border-radius: var(--r-md);
  border-left: 3px solid var(--warning);
  margin-bottom: 1.5rem;
}

.disclaimer-banner svg { flex-shrink: 0; margin-top: 3px; color: var(--warning); }

.disclaimer-banner p {
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Score */
.score-section {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.score-card {
  display: flex;
  align-items: center;
  gap: 2rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: var(--sp-lg) var(--sp-xl);
}

.score-ring {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.score-ring svg { width: 100%; height: 100%; }

.score-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1;
  color: var(--text-primary);
}

.score-max {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.score-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.score-label {
  font-size: 1.35rem;
  font-weight: 700;
}

.skin-type-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  background: var(--background);
  padding: 0.4rem 0.85rem;
  border-radius: var(--r-full);
  width: fit-content;
}

.skin-type-pill strong {
  color: var(--primary);
}

/* Image */
.image-section {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.image-frame {
  max-width: 400px;
  border-radius: var(--r-lg);
  overflow: hidden;
  border: 1px solid var(--border);
}

.image-frame img {
  width: 100%;
  height: 300px;
  object-fit: cover;
  display: block;
}

/* Section headings */
.section-heading {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.section-desc {
  font-size: 0.925rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

/* Analysis Grid */
.analysis-section {
  margin-bottom: 2rem;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 1rem 1.1rem;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}

.metric-header svg { width: 15px; height: 15px; }

.metric-value {
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.metric-value .count {
  font-size: 0.85rem;
  font-weight: 400;
  color: var(--text-muted);
}

.metric-bar {
  height: 4px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 99px;
  transition: width 0.6s ease;
}

.bar-fill.fill-hydration {
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}

/* Summary */
.summary-section {
  margin-bottom: 2rem;
}

.summary-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(139, 92, 246, 0.04));
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: var(--sp-lg);
}

.summary-card p {
  font-size: 0.95rem;
  line-height: 1.75;
  color: var(--text-primary);
}

/* Recommendations */
.recs-section {
  margin-bottom: 2rem;
}

.recs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.rec-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: var(--sp-lg);
  transition: all var(--t-base);
}

.rec-card:hover {
  box-shadow: var(--shadow-md);
}

.rec-card.priority-high { border-left: 4px solid var(--success); }
.rec-card.priority-medium { border-left: 4px solid var(--warning); }
.rec-card.priority-low { border-left: 4px solid var(--text-muted); }

.rec-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
}

.rec-top h4 {
  font-size: 1.05rem;
  font-weight: 600;
}

.rec-badge {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.2rem 0.6rem;
  border-radius: var(--r-full);
}

.rec-card.priority-high .rec-badge { background: var(--success-light); color: var(--success); }
.rec-card.priority-medium .rec-badge { background: var(--warning-light); color: var(--warning); }
.rec-card.priority-low .rec-badge { background: var(--background); color: var(--text-muted); }

.rec-reason {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.rec-meta {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding-bottom: 0.65rem;
  margin-bottom: 0.65rem;
  border-bottom: 1px solid var(--border);
}

.rec-meta p { font-size: 0.82rem; color: var(--text-secondary); }
.rec-meta strong { font-weight: 600; color: var(--text-primary); }

.rec-caution {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  padding: 0.4rem 0.6rem;
  background: rgba(239, 68, 68, 0.04);
  border-radius: var(--r-sm);
}

.rec-caution svg {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--error);
  width: 14px;
  height: 14px;
}

/* Interactions */
.interactions-section {
  margin-bottom: 2rem;
}

.interactions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.interaction-card {
  background: var(--surface);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--r-lg);
  padding: var(--sp-lg);
  background: rgba(245, 158, 11, 0.03);
}

.interaction-pair {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.interaction-pair svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.interaction-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  background: var(--surface);
  padding: 0.25rem 0.65rem;
  border-radius: var(--r-full);
  border: 1px solid var(--border);
}

.interaction-reason {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 0.65rem;
}

.interaction-suggestion {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-size: 0.82rem;
  color: var(--text-primary);
  padding: 0.5rem 0.65rem;
  background: rgba(245, 158, 11, 0.06);
  border-radius: var(--r-sm);
  line-height: 1.5;
}

.interaction-suggestion svg {
  flex-shrink: 0;
  margin-top: 3px;
  color: var(--success);
  width: 14px;
  height: 14px;
}

/* Home Remedies */
.remedies-section {
  margin-bottom: 2rem;
}

.remedies-card {
  background: rgba(16, 185, 129, 0.04);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--r-lg);
  padding: var(--sp-lg);
}

.remedies-card p {
  font-size: 0.92rem;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-line;
}

/* Wishing Message */
.wishing-section {
  margin-bottom: 2rem;
}

.wishing-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(139, 92, 246, 0.06));
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: var(--sp-xl);
  text-align: center;
}

.wishing-card p {
  font-size: 1.1rem;
  line-height: 1.7;
  color: var(--text-primary);
  font-weight: 500;
}

/* Actions */
.results-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.5rem 0 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--r-md);
  font-size: 0.925rem;
  font-weight: 600;
  transition: all var(--t-base);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  border-color: var(--primary);
  color: var(--primary);
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 1024px) {
  .analysis-grid { grid-template-columns: repeat(3, 1fr); }
  .recs-grid { grid-template-columns: 1fr; }
  .interactions-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .score-card { flex-direction: column; text-align: center; }
  .score-meta { align-items: center; }
  .analysis-grid { grid-template-columns: repeat(2, 1fr); }
  .results-title { font-size: 1.25rem; }
}

@media (max-width: 480px) {
  .analysis-grid { grid-template-columns: 1fr; }
  .results-actions { flex-direction: column; }
  .results-actions .btn { width: 100%; justify-content: center; }
}
</style>
