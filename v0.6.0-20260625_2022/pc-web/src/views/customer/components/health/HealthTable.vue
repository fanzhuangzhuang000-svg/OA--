<template>
  <div ref="tableRef" class="content-card glass">
    <div class="table-head">
      <span class="table-title">客户健康度明细</span>
      <span class="table-tip">按分数升序, 预警客户置顶</span>
    </div>
    <el-table
      :data="sortedList"
      stripe
      v-loading="loading"
      style="width: 100%"
      :header-cell-style="{ background: 'rgba(245, 247, 250, 0.6)', color: '#303133', fontWeight: 600 }"
      :row-class-name="rowClassName"
    >
      <el-table-column type="index" label="#" width="55" align="center" />
      <el-table-column prop="name" label="客户名称" min-width="180">
        <template #default="{ row }">
          <div class="customer-name">
            <el-avatar :size="30" :style="{ background: row.avatarColor }">
              {{ row.name?.charAt(0) }}
            </el-avatar>
            <span class="name-text">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="health_level" label="等级" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="healthTagType(row.health_level, row.health_score)" effect="dark" size="small" round>
            {{ healthChipText(row.health_level, row.health_score) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="health_score" label="分数" width="100" align="center">
        <template #default="{ row }">
          <span class="score-num" :style="{ color: healthColor(row.health_score) }">
            {{ Math.round(Number(row.health_score || 0)) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="5 维度评分" min-width="320">
        <template #default="{ row }">
          <div class="dim-bars">
            <div v-for="(v, k) in (row.score_breakdown || {})" :key="k" class="dim-row">
              <span class="dim-label">{{ healthDimensionLabel(String(k)) }}</span>
              <el-progress
                :percentage="Math.round(Number(v) || 0)"
                :stroke-width="6"
                :color="healthColor(Number(v) || 0)"
                :show-text="false"
                style="flex:1;margin:0 8px;"
              />
              <span class="dim-val">{{ Math.round(Number(v) || 0) }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="last_follow_at" label="最后跟进" width="160">
        <template #default="{ row }">
          {{ row.last_follow_at || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="emit('view', row)">
            <el-icon><View /></el-icon>查看详情
          </el-button>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty description="暂无健康度数据" />
      </template>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { View } from '@element-plus/icons-vue'
import type { HealthRow } from './types'
import { healthColor, healthTagType, healthChipText, healthDimensionLabel } from './types'

// v0.3.25 抽自 customer/Health.vue:93-165
const props = defineProps<{
  list: HealthRow[]
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'view', row: HealthRow): void
  (e: 'mounted', el: HTMLElement): void
}>()

const tableRef = ref<HTMLElement | null>(null)
defineExpose({ tableRef })

const sortedList = computed(() => {
  return [...props.list].sort((a, b) => Number(a.health_score || 0) - Number(b.health_score || 0))
})

function rowClassName({ row }: { row: HealthRow }): string {
  return Number(row.health_score || 0) < 40 ? 'row-warn' : ''
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
.content-card { padding: 16px 20px; }
.table-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.table-title {
  font-size: 14px;
  font-weight: 600;
  color: #0C447C;
  border-left: 3px solid #0C447C;
  padding-left: 8px;
}
.table-tip {
  font-size: 12px;
  color: #94A3B8;
}
.customer-name { display: flex; align-items: center; gap: 8px; }
.name-text { font-weight: 500; color: #0F172A; }
.score-num { font-size: 18px; font-weight: 700; }
.dim-bars { display: flex; flex-direction: column; gap: 4px; padding: 4px 0; }
.dim-row { display: flex; align-items: center; gap: 4px; }
.dim-label { font-size: 12px; color: #64748B; min-width: 60px; }
.dim-val { font-size: 12px; color: #0F172A; font-weight: 600; min-width: 30px; text-align: right; }

:deep(.row-warn) {
  background: rgba(163, 45, 45, 0.05) !important;
}
</style>
