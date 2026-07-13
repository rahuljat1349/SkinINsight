<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import TheHeader from './components/TheHeader.vue'
import TheFooter from './components/TheFooter.vue'
import '@/assets/main.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const BACKEND_URL = API_BASE_URL.replace('/api', '')

let pingInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  pingInterval = setInterval(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/health`, { signal: AbortSignal.timeout(5000) })
      if (res.ok) {
        const data = await res.json()
        console.log('[keepalive] backend healthy:', data.status)
      }
    } catch {
      // ignore – backend might be starting
    }
  }, 300_000)
})

onUnmounted(() => {
  if (pingInterval) clearInterval(pingInterval)
})
</script>

<template>
  <div class="app-container">
    <TheHeader />
    <main class="main-content">
      <RouterView v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
    <TheFooter />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
