<template>
  <div class="kpi-row">
    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">客户总数 / 平均健康分</div>
          <div class="kpi-value gradient-blue">
            {{ summary.total || 0 }}
            <span class="kpi-sub-inline">·  {{ summary.avg_score ?? '—' }} 分</span>
          </div>
        </div>
        <div class="kpi-icon" style="background: rgba(12, 68, 124, 0.12);">
          <el-icon :size="24" color="#0C447C"><OfficeBuilding /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">本月新增 {{ summary.new_this_month || 0 }} 家</div>
    </div>

    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">健康客户 (≥80)</div>
          <div class="kpi-value gradient-green">{{ levelCount.healthy || 0 }}</div>
        </div>
        <div class="kpi-icon" style="background: rgba(29, 158, 117, 0.12);">
          <el-icon :size="24" color="#1D9E75"><CircleCheckFilled /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">占比 {{ pct('healthy') }}%</div>
    </div>

    <div class="kpi-card glass" :class="{ 'is-warn': (levelCount.danger || 0) > 0 }">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">预警客户 (&lt;40)</div>
          <div class="kpi-value gradient-red">{{ levelCount.danger || 0 }}</div>
        </div>
        <div class="kpi-icon" style="background: rgba(163, 45, 45, 0.12);">
          <el-icon :size="24" color="#A32D2D"><WarningFilled /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">
        <el-link type="danger" :underline="false" @click="emit('scrollToTable')">查看 ↓</el-link>
      </div>
    </div>

    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">本月新增</div>
          <div class="kpi-value gradient-purple">{{ summary.new_this_month || 0 }}</div>
        </div>
        <div class="kpi-icon" style="background: rgba(83, 74, 183, 0.12);">
          <el-icon :size="24" color="#534AB7"><TrendCharts /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">vs 上月 {{ summary.growth_pct != null ? (summary.growth_pct + '%') : '—' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { OfficeBuilding, CircleCheckFilled, WarningFilled, TrendCharts } from '@element-plus/icons-vue'
import type { HealthSummary, LevelCount } from './types'

// v0.3.25 抽自 customer/Health.vue:11-67
const props = defineProps<{
  summary: HealthSummary
  levelCount: LevelCount
}>()

const emit = defineEmits<{
  (e: 'scrollToTable'): void
}>()

function pct(key: 'healthy' | 'good' | 'normal' | 'danger'): number {
  const total = (props.levelCount.healthy + props.levelCount.good + props.levelCount.normal + props.levelCount.danger) || 1
  return Math.round(((props.levelCount[key] || 0) / total) * 100)
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
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.kpi-card {
  padding: 18px 20px;
  transition: all 0.3s;
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(12, 68, 124, 0.12);
  }
  &.is-warn { animation: warn-pulse 1.5s ease-in-out infinite; }
}
.kpi-top { display: flex; justify-content: space-between; align-items: flex-start; }
.kpi-label { font-size: 13px; color: #64748B; }
.kpi-value {
  font-size: 26px;
  font-weight: 700;
  margin-top: 4px;
  letter-spacing: 0.3px;
}
.kpi-sub-inline {
  font-size: 14px;
  color: #94A3B8;
  font-weight: 500;
  margin-left: 6px;
}
.kpi-foot { margin-top: 8px; font-size: 12px; color: #94A3B8; }
.kpi-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gradient-blue    { background: linear-gradient(90deg, #0C447C, #1976D2); -webkit-background-clip: text; color: transparent; }
.gradient-green   { background: linear-gradient(90deg, #1D9E75, #34D399); -webkit-background-clip: text; color: transparent; }
.gradient-red     { background: linear-gradient(90deg, #A32D2D, #F87171); -webkit-background-clip: text; color: transparent; }
.gradient-purple  { background: linear-gradient(90deg, #534AB7, #818CF8); -webkit-background-clip: text; color: transparent; }

@keyframes warn-pulse {
  0%, 100% { box-shadow: 0 4px 16px rgba(12, 68, 124, 0.06); }
  50% { box-shadow: 0 4px 16px rgba(163, 45, 45, 0.3); }
}
</style>
