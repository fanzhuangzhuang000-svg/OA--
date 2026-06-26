<template>
  <div class="page-container health-page">
    <div class="page-header">
      <span class="page-title">客户健康度看板</span>
      <div class="header-actions">
        <el-button :icon="Refresh" plain @click="loadAll">刷新</el-button>
      </div>
    </div>

    <HealthKpiRow
      :summary="summary"
      :level-count="levelCount"
      @scroll-to-table="scrollToTable"
    />

    <HealthDistribution :level-count="levelCount" />

    <HealthTable
      ref="tableComp"
      :list="list"
      :loading="loading"
      @view="goDetail"
      @mounted="(el) => (tableEl = el)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { get } from '@/utils/request'

import HealthKpiRow from './components/health/HealthKpiRow.vue'
import HealthDistribution from './components/health/HealthDistribution.vue'
import HealthTable from './components/health/HealthTable.vue'

import type { HealthRow, HealthSummary, LevelCount } from './components/health/types'
import { avatarColor, emptySummary, emptyLevelCount } from './components/health/types'

// v0.3.25 拆 Health.vue 506→115 (-77%)
// 子组件: KpiRow / Distribution / Table

const router = useRouter()
const loading = ref(false)
const tableComp = ref<InstanceType<typeof HealthTable> | null>(null)
const tableEl = ref<HTMLElement | null>(null)

const list = ref<HealthRow[]>([])
const summary = reactive<HealthSummary>(emptySummary())
const levelCount = reactive<LevelCount>(emptyLevelCount())

const goDetail = (row: HealthRow) => router.push(`/customer/${row.id}`)

const scrollToTable = () => {
  tableEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function loadAll() {
  loading.value = true
  try {
    const data: any = await get('/customers/health')
    const arr: HealthRow[] = ((data?.data || data || [])).map((c: any) => ({
      ...c,
      avatarColor: avatarColor(c.id),
    }))
    list.value = arr
    // summary
    const total = arr.length
    const avg = total ? arr.reduce((s, r) => s + Number(r.health_score || 0), 0) / total : null
    Object.assign(summary, {
      total,
      avg_score: avg != null ? Math.round(avg * 10) / 10 : null,
      new_this_month: data?.summary?.new_this_month ?? 0,
      growth_pct: data?.summary?.growth_pct ?? null,
    })
    // levelCount
    let h = 0, g = 0, n = 0, d = 0
    arr.forEach((r) => {
      const s = Number(r.health_score || 0)
      if (s >= 80) h++
      else if (s >= 60) g++
      else if (s >= 40) n++
      else d++
    })
    levelCount.healthy = h
    levelCount.good = g
    levelCount.normal = n
    levelCount.danger = d
  } catch { /* toast */ }
  loading.value = false
}

onMounted(loadAll)
</script>

<style lang="scss" scoped>
.health-page {
  padding: 16px;
  background: linear-gradient(180deg, #f5f7fa 0%, #eef2f7 100%);
  min-height: calc(100vh - 60px);
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 14px 20px;
  border-radius: 10px;
  margin-bottom: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #0C447C;
  border-left: 4px solid #0C447C;
  padding-left: 10px;
}
.header-actions { display: flex; gap: 8px; align-items: center; }
</style>
