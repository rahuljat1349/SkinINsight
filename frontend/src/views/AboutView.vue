<template>
  <div class="about-view">
    <div class="container">
      <div class="about-header">
        <h1 class="about-title">About Skin Insight AI</h1>
        <p class="about-subtitle">
          AI-powered skin analysis providing educational insights about your skin.
        </p>
      </div>

      <section class="about-section">
        <h2 class="section-title">What is Skin Insight AI?</h2>
        <div class="content-grid">
          <div class="content-text">
            <p>
              Skin Insight AI is an innovative web application that uses artificial intelligence 
              to analyze your facial skin from a single photograph. It provides educational insights 
              about your skin condition, skin type, and recommends suitable skincare ingredients.
            </p>
            <p>
              Our advanced AI pipeline processes your image through multiple analysis stages,
              including face detection, alignment, and detailed skin characteristic evaluation.
            </p>
          </div>
          <div class="content-visual">
            <div class="visual-placeholder">
              <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <path d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2z"/>
                <path d="M12 6v6l4 2"/>
                <circle cx="12" cy="12" r="3" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      <section class="about-section">
        <h2 class="section-title">What We Analyze</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-number">01</div>
            <h3>Skin Type</h3>
            <p>Determine if your skin is Oily, Dry, Combination, or Normal</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">02</div>
            <h3>Oiliness</h3>
            <p>Measure oil production on a scale of 0-100</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">03</div>
            <h3>Hydration</h3>
            <p>Assess moisture levels on a scale of 0-100</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">04</div>
            <h3>Redness</h3>
            <p>Evaluate skin redness (Low, Moderate, High)</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">05</div>
            <h3>Pigmentation</h3>
            <p>Assess uneven skin tone (None, Mild, Moderate, Severe)</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">06</div>
            <h3>Acne</h3>
            <p>Detect acne with severity levels and lesion count</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">07</div>
            <h3>Wrinkles</h3>
            <p>Analyze fine lines (Minimal, Mild, Moderate, Severe)</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">08</div>
            <h3>Pores</h3>
            <p>Evaluate pore size (Small, Medium, Large)</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">09</div>
            <h3>Texture</h3>
            <p>Measure skin smoothness on a scale of 0-100</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-number">10</div>
            <h3>Skin Tone</h3>
            <p>Estimate your skin tone for educational purposes</p>
          </div>
        </div>
      </section>

      <section class="about-section">
        <h2 class="section-title">Personalized Recommendations</h2>
        <p class="section-intro">
          Based on your analysis, we provide personalized ingredient recommendations 
          that may benefit your skin:
        </p>
        
        <div class="ingredients-grid">
          <div class="ingredient-card">
            <h4>Niacinamide</h4>
            <p>Regulates oil, reduces pores, improves skin barrier</p>
          </div>
          <div class="ingredient-card">
            <h4>Salicylic Acid (BHA)</h4>
            <p>Exfoliates pores, reduces acne and blackheads</p>
          </div>
          <div class="ingredient-card">
            <h4>Glycolic Acid (AHA)</h4>
            <p>Exfoliates surface, brightens skin, improves texture</p>
          </div>
          <div class="ingredient-card">
            <h4>Hyaluronic Acid</h4>
            <p>Hydrates, plumps skin, improves elasticity</p>
          </div>
          <div class="ingredient-card">
            <h4>Vitamin C</h4>
            <p>Brightens skin, antioxidant protection, boosts collagen</p>
          </div>
          <div class="ingredient-card">
            <h4>Ceramides</h4>
            <p>Strengthens barrier, retains moisture, soothes skin</p>
          </div>
          <div class="ingredient-card">
            <h4>Retinol</h4>
            <p>Reduces wrinkles, improves texture, increases cell turnover</p>
          </div>
          <div class="ingredient-card">
            <h4>Azelaic Acid</h4>
            <p>Reduces acne and pigmentation, anti-inflammatory</p>
          </div>
          <div class="ingredient-card">
            <h4>Sunscreen</h4>
            <p>Essential protection from UV damage and premature aging</p>
          </div>
        </div>
      </section>

      <section class="about-section important">
        <h2 class="section-title">Important Information</h2>
        <div class="important-grid">
          <div class="important-card">
            <div class="important-icon warning">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <h3>Not a Medical Device</h3>
            <p>
              Skin Insight AI is <strong>NOT</strong> a medical diagnostic tool. 
              Our analysis is for educational purposes only and does not replace 
              professional dermatological advice, diagnosis, or treatment.
            </p>
          </div>
          
          <div class="important-card">
            <div class="important-icon privacy">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h3>Privacy First</h3>
            <p>
              We prioritize your privacy. Images are processed in memory and 
              not stored on our servers. Your data remains secure and private.
            </p>
          </div>
          
          <div class="important-card">
            <div class="important-icon accuracy">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </div>
            <h3>Accuracy Factors</h3>
            <p>
              Results may vary based on lighting conditions, image quality, 
              and camera angle. For best results, use a clear, well-lit frontal 
              photo with minimal shadows.
            </p>
          </div>
        </div>
      </section>

      <section class="about-section">
        <h2 class="section-title">Technology</h2>
        <div class="tech-grid">
          <div class="tech-card">
            <div class="tech-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <h4>Backend</h4>
            <p>FastAPI (Python) with ONNX Runtime and PyTorch</p>
          </div>
          
          <div class="tech-card">
            <div class="tech-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                <circle cx="12" cy="12" r="4" />
              </svg>
            </div>
            <h4>Frontend</h4>
            <p>Vue 3 + TypeScript + Vite</p>
          </div>
          
          <div class="tech-card">
            <div class="tech-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <line x1="3" y1="9" x2="21" y2="9" />
                <line x1="9" y1="21" x2="9" y2="9" />
              </svg>
            </div>
            <h4>Models</h4>
            <p>InsightFace for face detection and analysis</p>
          </div>
          
          <div class="tech-card">
            <div class="tech-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                <polyline points="9 22 9 12 15 12 15 22" />
              </svg>
            </div>
            <h4>Deployment</h4>
            <p>Docker with multi-stage builds</p>
          </div>
        </div>
      </section>

      <div class="about-footer">
        <p>Skin Insight AI - Version 1.0.0</p>
        <p>&copy; {{ new Date().getFullYear() }} All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-view {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.about-header {
  text-align: center;
  padding: 2rem 0;
}

.about-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.about-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  max-width: 700px;
  margin: 0 auto;
}

.about-section {
  padding: 1rem 0;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  text-align: center;
}

.section-intro {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
  padding: 2rem 0;
}

.content-text p {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.7;
  margin-bottom: 1rem;
}

.content-visual {
  display: flex;
  justify-content: center;
}

.visual-placeholder {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 3s ease-in-out infinite;
}

.visual-placeholder svg {
  color: white;
  opacity: 0.8;
  width: 100px;
  height: 100px;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.feature-card {
  background: var(--surface);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
  border-color: var(--primary);
}

.feature-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
  font-family: monospace;
}

.feature-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Ingredients Grid */
.ingredients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.ingredient-card {
  background: var(--surface);
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}

.ingredient-card:hover {
  border-color: var(--primary);
  transform: translateX(4px);
}

.ingredient-card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.ingredient-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Important Section */
.about-section.important {
  background: var(--background);
  padding: 2rem;
  border-radius: 16px;
}

.important-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.important-card {
  background: var(--surface);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.important-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.important-icon.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.important-icon.privacy {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary);
}

.important-icon.accuracy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.important-icon svg {
  width: 28px;
  height: 28px;
}

.important-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.important-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}

.important-card p strong {
  color: var(--text-primary);
}

/* Tech Grid */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.tech-card {
  background: var(--surface);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.tech-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
}

.tech-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tech-icon svg {
  color: white;
  width: 36px;
  height: 36px;
}

.tech-card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.tech-card p {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

/* Footer */
.about-footer {
  text-align: center;
  padding: 2rem 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.about-footer p {
  margin-bottom: 0.25rem;
}

@media (max-width: 768px) {
  .about-title {
    font-size: 2rem;
  }
  
  .about-subtitle {
    font-size: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .features-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .ingredients-grid {
    grid-template-columns: 1fr;
  }
  
  .important-grid {
    grid-template-columns: 1fr;
  }
  
  .tech-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
</style>
