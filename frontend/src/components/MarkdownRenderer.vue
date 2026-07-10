<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{ content: string }>()

const md = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: false,
  typographer: true
})

const rendered = computed(() => md.render(props.content || ''))
</script>

<template>
  <div class="md-content" v-html="rendered" />
</template>

<style scoped>
.md-content {
  font-size: inherit;
  line-height: inherit;
  color: inherit;
}

.md-content :deep(p) {
  margin: 0 0 0.5em;
}

.md-content :deep(p:last-child) {
  margin-bottom: 0;
}

.md-content :deep(strong) {
  font-weight: 600;
}

.md-content :deep(ul),
.md-content :deep(ol) {
  padding-left: 1.25rem;
  margin: 0.4em 0;
}

.md-content :deep(li) {
  margin-bottom: 0.2em;
}

.md-content :deep(h3),
.md-content :deep(h4) {
  margin: 0.75em 0 0.35em;
  font-weight: 600;
}

.md-content :deep(code) {
  background: var(--background);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.88em;
}

.md-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0.75em 0;
}
</style>
