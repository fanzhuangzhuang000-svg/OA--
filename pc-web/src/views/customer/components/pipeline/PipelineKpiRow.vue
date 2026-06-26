<template>
  <div class="kpi-row">
    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">总机会数（5 列）</div>
          <div class="kpi-value gradient-blue">{{ kpi.total_opportunities ?? 0 }}</div>
        </div>
        <div class="kpi-icon" style="background: rgba(12, 68, 124, 0.12);">
          <el-icon :size="24" color="#0C447C"><Connection /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">流失 {{ kpi.lost_count ?? 0 }} 家不计入</div>
    </div>

    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">总预计金额</div>
          <div class="kpi-value gradient-green">¥ {{ formatAmount(kpi.total_amount ?? 0) }}</div>
        </div>
        <div class="kpi-icon" style="background: rgba(29, 158, 117, 0.12);">
          <el-icon :size="24" color="#1D9E75"><Money /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">按 5 列阶段合计</div>
    </div>

    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">本月新增</div>
          <div class="kpi-value gradient-purple">{{ kpi.new_this_month ?? 0 }}</div>
        </div>
        <div class="kpi-icon" style="background: rgba(83, 74, 183, 0.12);">
          <el-icon :size="24" color="#534AB7"><Plus /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">created_at 本月</div>
    </div>

    <div class="kpi-card glass">
      <div class="kpi-top">
        <div>
          <div class="kpi-label">平均成交周期</div>
          <div class="kpi-value gradient-orange">
            {{ kpi.avg_won_days != null ? kpi.avg_won_days + ' 天' : '—' }}
          </div>
        </div>
        <div class="kpi-icon" style="background: rgba(186, 117, 23, 0.12);">
          <el-icon :size="24" color="#BA7517"><Timer /></el-icon>
        </div>
      </div>
      <div class="kpi-foot">成交客户中位天数</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Connection, Money, Plus, Timer } from '@element-plus/icons-vue'
import type { PipelineKpi } from './types'
import { formatAmount } from './types'

// v0.3.25 抽自 customer/Pipeline.vue:20-74
defineProps<{
  kpi: PipelineKpi
}>()
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
}
.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.kpi-label { font-size: 13px; color: #64748B; }
.kpi-value {
  font-size: 26px;
  font-weight: 700;
  margin-top: 4px;
  letter-spacing: 0.3px;
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
.gradient-purple  { background: linear-gradient(90deg, #534AB7, #818CF8); -webkit-background-clip: text; color: transparent; }
.gradient-orange  { background: linear-gradient(90deg, #BA7517, #FBBF24); -webkit-background-clip: text; color: transparent; }

@media (max-width: 1200px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
