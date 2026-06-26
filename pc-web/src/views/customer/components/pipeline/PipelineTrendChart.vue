<template>
  <div class="trend-card glass">
    <div class="trend-header">
      <span class="trend-title">最近 4 周趋势</span>
      <div class="trend-legend">
        <span class="lg-item"><span class="lg-dot" style="background:#534AB7"></span>新增</span>
        <span class="lg-item"><span class="lg-dot" style="background:#1D9E75"></span>成交</span>
        <span class="lg-item"><span class="lg-dot" style="background:#A32D2D"></span>流失</span>
      </div>
    </div>
    <svg class="trend-svg" viewBox="0 0 680 200" preserveAspectRatio="none">
      <g class="grid">
        <line v-for="i in 4" :key="i" x1="0" :y1="40 * i" x2="680" :y2="40 * i" stroke="#E5EAF1" stroke-dasharray="3 3" />
      </g>
      <g v-for="(w, wi) in trend" :key="w.week" :transform="`translate(${wi * 170 + 30}, 0)`">
        <g v-for="(bar, bi) in trendBars(w)" :key="bar.label">
          <rect
            :x="bi * 36 + 12"
            :y="160 - bar.h"
            width="28"
            :height="bar.h"
            :fill="bar.color"
            rx="4"
          >
            <title>{{ bar.label }}: {{ bar.value }}</title>
          </rect>
          <text
            :x="bi * 36 + 26"
            :y="155 - bar.h"
            text-anchor="middle"
            fill="#475569"
            font-size="11"
          >{{ bar.value || '' }}</text>
        </g>
        <text
          x="80"
          y="190"
          text-anchor="middle"
          fill="#0C447C"
          font-size="12"
          font-weight="600"
        >{{ w.week }}</text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import type { WeeklyTrend } from './types'

// v0.3.25 抽自 customer/Pipeline.vue:164-209
const props = defineProps<{
  trend: WeeklyTrend[]
}>()

function trendBars(w: WeeklyTrend) {
  const max = Math.max(
    1,
    ...props.trend.flatMap((x) => [x.new_count, x.won_count, x.lost_count])
  )
  const mk = (label: string, value: number, color: string) => {
    const h = Math.round((value / max) * 130)
    return { label, value, h: Math.max(2, h), color }
  }
  return [
    mk('新增', w.new_count, '#534AB7'),
    mk('成交', w.won_count, '#1D9E75'),
    mk('流失', w.lost_count, '#A32D2D'),
  ]
}
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
.trend-card { padding: 16px 20px; }
.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.trend-title {
  font-size: 14px;
  font-weight: 600;
  color: #0C447C;
  border-left: 3px solid #0C447C;
  padding-left: 8px;
}
.trend-legend {
  display: flex;
  gap: 14px;
  font-size: 12px;
  color: #475569;
}
.lg-item { display: inline-flex; align-items: center; gap: 4px; }
.lg-dot { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
.trend-svg {
  width: 100%;
  height: 200px;
  display: block;
}
</style>
