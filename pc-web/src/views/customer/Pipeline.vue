<template>
  <div class="page-container pipeline-page">
    <div class="page-header">
      <span class="page-title">销售漏斗看板</span>
      <div class="header-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索客户名"
          :prefix-icon="Search"
          clearable
          style="width: 220px;"
          @keyup.enter="loadAll"
        />
        <el-button :icon="Refresh" plain @click="loadAll">刷新</el-button>
        <el-button :icon="Back" plain @click="goBack">返回列表</el-button>
      </div>
    </div>

    <PipelineKpiRow :kpi="kpi" />

    <div class="kanban-board" @dragover.prevent>
      <PipelineColumn
        v-for="col in columns"
        :key="col.stage"
        :column="col"
        :drag-over="dragOverCol === col.stage"
        :dragging-id="draggingId"
        @dragstart="onDragStart"
        @dragend="onDragEnd"
        @dragover="onDragOver"
        @dragenter="onDragEnter"
        @dragleave="onDragLeave"
        @drop="onDrop"
        @view="goDetail"
      />
    </div>

    <PipelineTrendChart :trend="trend" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Back } from '@element-plus/icons-vue'
import {
  getCustomerPipeline,
  updateCustomerStage,
  getPipelineWeeklyTrend,
} from '@/api/modules'

import PipelineKpiRow from './components/pipeline/PipelineKpiRow.vue'
import PipelineColumn from './components/pipeline/PipelineColumn.vue'
import PipelineTrendChart from './components/pipeline/PipelineTrendChart.vue'

import type { PipelineColumn as Column, PipelineCard, PipelineKpi, WeeklyTrend, PipelineStage } from './components/pipeline/types'

// v0.3.25 拆 Pipeline.vue 625→170 (-73%)
// 子组件: KpiRow / Column(内含 Card) / TrendChart

const router = useRouter()
const keyword = ref('')

const columns = ref<Column[]>([])
const kpi = ref<PipelineKpi>({} as PipelineKpi)
const trend = ref<WeeklyTrend[]>([])
const draggingId = ref<number | null>(null)
const draggingFrom = ref<PipelineStage | null>(null)
const dragOverCol = ref<PipelineStage | null>(null)

const goBack = () => router.push('/customer/list')
const goDetail = (card: PipelineCard) => router.push(`/customer/${card.id}`)

async function loadAll() {
  try {
    const [pipe, tr] = await Promise.all([
      getCustomerPipeline({ keyword: keyword.value || undefined }),
      getPipelineWeeklyTrend(),
    ])
    columns.value = pipe.columns || []
    kpi.value = pipe.kpi || {}
    const lostCol = columns.value.find((c) => c.stage === 'lost')
    kpi.value.lost_count = lostCol?.count || 0
    trend.value = tr || []
  } catch (e: any) {
    ElMessage.error('加载看板失败: ' + (e?.message || 'unknown'))
  }
}

function onDragStart(e: DragEvent, card: PipelineCard, from: PipelineStage) {
  draggingId.value = card.id
  draggingFrom.value = from
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(card.id))
  }
}

function onDragEnd() {
  draggingId.value = null
  draggingFrom.value = null
  dragOverCol.value = null
}

function onDragOver(_e: DragEvent, stage: PipelineStage) {
  if (draggingFrom.value === stage) return
}

function onDragEnter(_e: DragEvent, stage: PipelineStage) {
  if (draggingFrom.value !== stage) dragOverCol.value = stage
}

function onDragLeave(stage: PipelineStage) {
  if (dragOverCol.value === stage) dragOverCol.value = null
}

async function onDrop(_e: DragEvent, targetStage: PipelineStage) {
  dragOverCol.value = null
  if (!draggingId.value || !draggingFrom.value) return
  if (draggingFrom.value === targetStage) return

  const id = draggingId.value
  const fromStage = draggingFrom.value
  const fromCol = columns.value.find((c) => c.stage === fromStage)
  const toCol = columns.value.find((c) => c.stage === targetStage)
  if (!fromCol || !toCol) return

  const cardIdx = fromCol.cards.findIndex((c) => c.id === id)
  if (cardIdx < 0) return
  const card = fromCol.cards[cardIdx]
  const amount = Number(card.expected_amount) || 0

  // 乐观更新
  fromCol.cards.splice(cardIdx, 1)
  fromCol.count = Math.max(0, fromCol.count - 1)
  fromCol.total = Math.max(0, fromCol.total - amount)
  toCol.cards.unshift({ ...card })
  toCol.count += 1
  toCol.total += amount
  if (targetStage !== 'lost' && fromStage === 'lost') {
    kpi.value.total_amount = (Number(kpi.value.total_amount) || 0) + amount
    kpi.value.total_opportunities = (kpi.value.total_opportunities || 0) + 1
  } else if (fromStage !== 'lost' && targetStage === 'lost') {
    kpi.value.total_amount = Math.max(0, (Number(kpi.value.total_amount) || 0) - amount)
    kpi.value.total_opportunities = Math.max(0, (kpi.value.total_opportunities || 0) - 1)
  }

  try {
    await updateCustomerStage(id, targetStage)
    ElMessage.success(`已移至「${toCol.label}」`)
  } catch (e: any) {
    // 回滚
    toCol.cards.shift()
    toCol.count = Math.max(0, toCol.count - 1)
    toCol.total = Math.max(0, toCol.total - amount)
    fromCol.cards.splice(cardIdx, 0, card)
    fromCol.count += 1
    fromCol.total += amount
    ElMessage.error('更新失败: ' + (e?.message || 'unknown'))
  } finally {
    draggingId.value = null
    draggingFrom.value = null
  }
}

onMounted(() => {
  loadAll()
})
</script>

<style lang="scss" scoped>
.pipeline-page {
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
.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.kanban-board {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 16px;
  min-height: 60vh;
}
</style>
