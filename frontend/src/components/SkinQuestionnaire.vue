<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'

const store = useAnalysisStore()

const emit = defineEmits<{ analyze: [] }>()

const questions = [
  {
    label: 'What\u2019s your age group?',
    key: 'age_group' as const,
    options: ['18\u201324', '25\u201330', '31\u201340', '41\u201350', '50+']
  },
  {
    label: 'How would you describe your skin?',
    key: 'skin_type_self' as const,
    options: ['Oily', 'Dry', 'Combination']
  },
  {
    label: 'What Is your gender?',
    key: 'gender' as const,
    options: ['Male', 'Female', 'Non-binary / Other']
  },
  {
    label: 'Is your skin sensitive?',
    key: 'sensitive_skin' as const,
    options: ['Yes', 'No', 'Sometimes']
  }
]

const current = ref(0)
const total = questions.length
const isLast = computed(() => current.value === total - 1)
const progress = computed(() => ((current.value + 1) / total) * 100)

const currentQuestion = computed(() => questions[current.value])
const currentValue = computed(() => store.userInfo[currentQuestion.value.key])

const select = (value: string) => {
  store.setUserInfo({ ...store.userInfo, [currentQuestion.value.key]: value })
}

const next = () => {
  if (!currentValue.value) return
  if (isLast.value) {
    emit('analyze')
  } else {
    current.value++
  }
}
</script>

<template>
  <div class="q-card">
    <!-- Progress bar -->
    <div class="q-progress-track">
      <div class="q-progress-fill" :style="{ width: `${progress}%` }"></div>
    </div>

    <!-- Step label -->
    <p class="q-step-label">{{ current + 1 }} of {{ total }}</p>

    <!-- Question -->
    <h3 class="q-label">{{ currentQuestion.label }}</h3>

    <!-- Options -->
    <div class="q-options">
      <button
        v-for="opt in currentQuestion.options"
        :key="opt"
        class="q-pill"
        :class="{ active: currentValue === opt }"
        @click="select(opt)"
      >
        {{ opt }}
      </button>
    </div>

    <!-- Next / Analyze button -->
    <button
      class="q-btn"
      :disabled="!currentValue"
      @click="next"
    >
      <template v-if="isLast">
        <span>Analyze My Skin</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
      </template>
      <template v-else>
        <span>Next</span>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </template>
    </button>
  </div>
</template>

<style scoped>
.q-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: var(--sp-xl);
  box-shadow: var(--shadow-md);
  animation: fadeSlideIn 0.25s ease;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Progress bar */
.q-progress-track {
  width: 100%;
  height: 4px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.q-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 99px;
  transition: width 0.3s ease;
}

/* Step label */
.q-step-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

/* Question */
.q-label {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  line-height: 1.4;
}

/* Options */
.q-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-bottom: 1.5rem;
}

.q-pill {
  padding: 0.6rem 1.25rem;
  border-radius: 999px;
  border: 1.5px solid var(--border);
  background: var(--background);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--t-fast);
}

.q-pill:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

.q-pill.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

/* Action button */
.q-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  width: 100%;
  max-width: 360px;
  padding: 0.8rem 1.5rem;
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

.q-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
}

.q-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}
</style>
