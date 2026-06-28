<template>
  <div ref="glowRef" class="mouse-glow" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const glowRef = ref<HTMLDivElement>()

onMounted(() => {
  const el = glowRef.value
  if (!el) return

  const handleMouse = (e: MouseEvent) => {
    el.style.transform = `translate(${e.clientX - 200}px, ${e.clientY - 200}px)`
  }

  window.addEventListener('mousemove', handleMouse)
  onUnmounted(() => window.removeEventListener('mousemove', handleMouse))
})
</script>

<style scoped>
.mouse-glow {
  position: fixed;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(10, 132, 255, 0.03) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
  transition: transform 0.3s ease-out;
  will-change: transform;
}
</style>
