import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Smoothly hide initial loading indicator
const initialLoading = document.getElementById('initial-loading')
if (initialLoading) {
  initialLoading.classList.add('hidden')
  setTimeout(() => {
    initialLoading.style.display = 'none'
  }, 400)
}

app.mount('#app')
