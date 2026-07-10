<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <header class="header" :class="{ 'header-transparent': route.name === 'home' }">
    <div class="container">
      <RouterLink to="/" class="logo">
        <svg class="logo-icon" viewBox="0 0 32 32" fill="none">
          <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6366f1" />
              <stop offset="100%" stop-color="#8b5cf6" />
            </linearGradient>
          </defs>
          <rect width="32" height="32" rx="8" fill="url(#logoGrad)" />
          <circle cx="16" cy="16" r="9" fill="none" stroke="white" stroke-width="1.8" />
          <path d="M11 16.5c0-2.8 2.2-5 5-5s5 2.2 5 5" stroke="white" stroke-width="1.5" stroke-linecap="round" />
          <path d="M13 17c0-1.7 1.3-3 3-3s3 1.3 3 3" stroke="white" stroke-width="1.3" stroke-linecap="round" />
          <circle cx="16" cy="18.5" r="1.5" fill="white" opacity="0.9" />
          <path d="M10 13l2 1M22 13l-2 1" stroke="white" stroke-width="1.2" stroke-linecap="round" />
        </svg>
        <span class="logo-text">Skin<span class="logo-accent">Insight</span></span>
      </RouterLink>

      <nav class="nav">
        <RouterLink to="/" class="nav-link">Home</RouterLink>
        <RouterLink to="/analyze" class="nav-link">Analyze</RouterLink>
        <RouterLink to="/about" class="nav-link">About</RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background 0.3s ease;
}

.header-transparent {
  background: rgba(255, 255, 255, 0.8);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1.25rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 1.3rem;
  letter-spacing: -0.02em;
}

.logo-accent {
  color: var(--primary);
}

.nav {
  display: flex;
  gap: 0.25rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.925rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.nav-link:hover {
  color: var(--primary);
  background: rgba(99, 102, 241, 0.06);
}

.router-link-exact-active {
  color: var(--primary);
  background: rgba(99, 102, 241, 0.08);
  font-weight: 600;
}

@media (max-width: 768px) {
  .container {
    height: 60px;
    padding: 0 1rem;
  }

  .logo-text {
    font-size: 1.1rem;
  }

  .nav-link {
    padding: 0.4rem 0.75rem;
    font-size: 0.85rem;
  }
}
</style>
