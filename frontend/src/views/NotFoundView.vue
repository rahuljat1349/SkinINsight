<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="not-found-view">
    <div class="container">
      <div class="not-found-content">
        <div class="not-found-code">404</div>
        <h1 class="not-found-title">Page Not Found</h1>
        <p class="not-found-message">
          Oops! The page you're looking for doesn't exist or has been moved.
        </p>
        <div class="not-found-actions">
          <button @click="goHome" class="btn btn-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            <span>Go Home</span>
          </button>
          <a href="/analyze" class="btn btn-secondary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
            <span>Start Analysis</span>
          </a>
        </div>
      </div>
      
      <div class="not-found-visual">
        <svg width="200" height="200" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z" />
          <path d="M12 6v6l4 2" />
          <circle cx="16" cy="8" r="1" fill="currentColor" />
          <circle cx="8" cy="16" r="1" fill="currentColor" />
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-view {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.container {
  max-width: 800px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  text-align: center;
}

.not-found-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.not-found-code {
  font-size: 8rem;
  font-weight: 800;
  color: var(--primary);
  line-height: 1;
  opacity: 0.8;
}

.not-found-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.not-found-message {
  color: var(--text-secondary);
  font-size: 1.125rem;
  max-width: 400px;
}

.not-found-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--background);
  border-color: var(--primary);
  color: var(--primary);
}

.btn svg {
  width: 18px;
  height: 18px;
}

.not-found-visual {
  display: flex;
  justify-content: center;
  opacity: 0.6;
}

.not-found-visual svg {
  color: var(--primary);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@media (max-width: 768px) {
  .not-found-code {
    font-size: 5rem;
  }
  
  .not-found-title {
    font-size: 1.5rem;
  }
  
  .not-found-message {
    font-size: 1rem;
  }
  
  .not-found-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
