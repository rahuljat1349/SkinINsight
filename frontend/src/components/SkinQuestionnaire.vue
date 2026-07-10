<script setup lang="ts">
import { useAnalysisStore } from '@/stores/analysisStore'
import { AGE_GROUPS, SKIN_TYPES, GENDERS, SENSITIVITY_OPTIONS } from '@/types'

const store = useAnalysisStore()

const set = (field: keyof typeof store.userInfo, value: string) => {
  store.setUserInfo({ ...store.userInfo, [field]: value })
}
</script>

<template>
  <div class="questionnaire-card">
    <h3 class="q-title">Tell Us About Yourself</h3>
    <p class="q-subtitle">Help us tailor your skin analysis with these details.</p>

    <div class="q-grid">
      <!-- Age Group -->
      <div class="q-field">
        <label class="q-label">Age Group</label>
        <div class="pill-group">
          <button
            v-for="opt in AGE_GROUPS"
            :key="opt"
            class="pill"
            :class="{ active: store.userInfo.age_group === opt }"
            @click="set('age_group', opt)"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- Skin Type (self-reported) -->
      <div class="q-field">
        <label class="q-label">How Would You Describe Your Skin?</label>
        <div class="pill-group">
          <button
            v-for="opt in SKIN_TYPES"
            :key="opt"
            class="pill"
            :class="{ active: store.userInfo.skin_type_self === opt }"
            @click="set('skin_type_self', opt)"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- Gender -->
      <div class="q-field">
        <label class="q-label">Gender</label>
        <div class="pill-group">
          <button
            v-for="opt in GENDERS"
            :key="opt"
            class="pill"
            :class="{ active: store.userInfo.gender === opt }"
            @click="set('gender', opt)"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- Sensitive Skin -->
      <div class="q-field">
        <label class="q-label">Is Your Skin Sensitive?</label>
        <div class="pill-group">
          <button
            v-for="opt in SENSITIVITY_OPTIONS"
            :key="opt"
            class="pill"
            :class="{ active: store.userInfo.sensitive_skin === opt }"
            @click="set('sensitive_skin', opt)"
          >
            {{ opt }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.questionnaire-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-xl);
  padding: var(--sp-xl);
  box-shadow: var(--shadow-md);
  margin-bottom: 1.5rem;
}

.q-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.q-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: var(--sp-lg);
}

.q-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.q-field {}

.q-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pill {
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  border: 1.5px solid var(--border);
  background: var(--background);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--t-fast);
}

.pill:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

.pill.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
</style>
