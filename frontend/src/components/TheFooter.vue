<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="footer-brand">
            <svg class="footer-logo" viewBox="0 0 32 32" fill="none" width="28" height="28">
              <defs>
                <linearGradient id="fg" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#6366f1" />
                  <stop offset="100%" stop-color="#8b5cf6" />
                </linearGradient>
              </defs>
              <rect width="32" height="32" rx="8" fill="url(#fg)" />
              <text x="16" y="22" text-anchor="middle" fill="white" font-size="18" font-weight="800" font-family="Arial, sans-serif">C</text>
            </svg>
            <span class="footer-brand-text">CutiS</span>
          </div>
          <p class="footer-desc">
            AI-powered skin analysis providing educational insights about your skin.
          </p>
        </div>
        <div class="footer-col">
          <h4 class="footer-heading">Important</h4>
          <p class="footer-text">This is NOT a medical diagnostic tool.</p>
          <p class="footer-text">Results are for educational purposes only.</p>
          <p class="footer-text">Consult a licensed dermatologist for medical advice.</p>
        </div>
        <div class="footer-col">
          <h4 class="footer-heading">Privacy</h4>
          <p class="footer-text">Images are processed in memory only.</p>
          <p class="footer-text">Your data is never stored or shared.</p>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; {{ new Date().getFullYear() }} CutiS</span>
        <span>Made By Rahul Dudi</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--surface);
  border-top: 1px solid var(--border);
  padding: 2.5rem 0 1.5rem;
  margin-top: auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.footer-brand-text {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
}

.footer-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 280px;
}

.footer-heading {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.footer-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.footer-version {
  font-family: monospace;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  background: var(--background);
  border-radius: var(--r-sm);
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  .footer-desc { max-width: none; }
  .footer-bottom { flex-direction: column; gap: 0.5rem; text-align: center; }
}
</style>
