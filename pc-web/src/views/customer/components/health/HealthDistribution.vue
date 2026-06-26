<template>
  <div class="dist-row glass">
    <div class="dist-title">健康度分布</div>
    <div class="dist-bars">
      <div v-for="bar in bars" :key="bar.key" class="dist-bar-col">
        <div class="dist-bar-header">
          <el-tag :type="bar.tagType" effect="dark" size="small" round>{{ bar.label }} ({{ bar.count }})</el-tag>
        </div>
        <el-progress
          :percentage="bar.pct"
          :stroke-width="14"
          :color="bar.color"
          :show-text="false"
          :duration="6"
          class="dist-bar"
        />
        <div class="dist-bar-foot">
          <span class="dist-bar-pct">{{ bar.pct }}%</span>
          <span class="dist-bar-score">{{ bar.range }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LevelCount } from './types'

// v0.3.25 抽自 customer/Health.vue:69-91
const props = defineProps<{
  levelCount: LevelCount
}>()

const bars = computed(() => {
  const total = (props.levelCount.healthy + props.levelCount.good + props.levelCount.normal + props.levelCount.danger) || 1
  return [
    { key: 'healthy', label: '健康', color: '#1D9E75', tagType: 'success' as const, count: props.levelCount.healthy, pct: Math.round((props.levelCount.healthy / total) * 100), range: '≥80 分' },
    { key: 'good', label: '良好', color: '#0C447C', tagType: 'primary' as const, count: props.levelCount.good, pct: Math.round((props.levelCount.good / total) * 100), range: '60-79' },
    { key: 'normal', label: '一般', color: '#BA7517', tagType: 'warning' as const, count: props.levelCount.normal, pct: Math.round((props.levelCount.normal / total) * 100), range: '40-59' },
    { key: 'danger', label: '预警', color: '#A32D2D', tagType: 'danger' as const, count: props.levelCount.danger, pct: Math.round((props.levelCount.danger / total) * 100), range: '<40' },
  ]
})
</script>

<style lang="scss" scoped>
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 16px rgba(12, 68, 124, 0.06);
  border-radius: 12px;
}
.dist-row { padding: 16px 20px; margin-bottom: 16px; }
.dist-title {
  font-size: 14px;
  font-weight: 600;
  color: #0C447C;
  border-left: 3px solid #0C447C;
  padding-left: 8px;
  margin-bottom: 12px;
}
.dist-bars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.dist-bar-col { padding: 8px 0; }
.dist-bar-header { margin-bottom: 6px; }
.dist-bar { margin: 6px 0; }
.dist-bar-foot {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #94A3B8;
}
.dist-bar-pct { font-weight: 700; color: #0C447C; }
</style>
