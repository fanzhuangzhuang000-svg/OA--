<template>
  <div class="page-container">
    <InspectionStatCards :stats="stats" :stats-loading="statsLoading" />

    <InspectionFilterBar
      ref="filterBarRef"
      :form="searchForm"
      :project-options="projectOptions"
      :process-instance-options="processInstanceOptions"
      @search="handleSearch"
      @reset="handleReset"
    />

    <InspectionTable
      :list="list"
      :loading="loading"
      :total="pagination.total"
      :page="pagination.page"
      :per-page="pagination.per_page"
      @view="goInstance"
      @page-change="(p) => loadList(p)"
      @size-change="(s) => { pagination.per_page = s; loadList(1) }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { processApi } from '@/api/modules'
import { getProjectList } from '@/api/modules'

import InspectionStatCards from './components/inspection-list/InspectionStatCards.vue'
import InspectionFilterBar from './components/inspection-list/InspectionFilterBar.vue'
import InspectionTable from './components/inspection-list/InspectionTable.vue'

import type {
  Inspection, InspectionStats, InspectionFilters,
  ProjectOption, ProcessInstanceOption,
} from './components/inspection-list/types'
import { emptyStats } from './components/inspection-list/types'

// v0.3.25 拆 InspectionList.vue 539→115 (-79%)
// 子组件: StatCards / FilterBar / Table

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const statsLoading = ref(false)

const stats = reactive<InspectionStats>(emptyStats())
const list = ref<Inspection[]>([])
const projectOptions = ref<ProjectOption[]>([])
const processInstanceOptions = ref<ProcessInstanceOption[]>([])

const searchForm = reactive<InspectionFilters>({
  project_id: null,
  process_instance_id: null,
  result: '',
})

const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const filterBarRef = ref<InstanceType<typeof InspectionFilterBar> | null>(null)

async function loadStats() {
  statsLoading.value = true
  try {
    const r: any = await processApi.inspectionStats()
    Object.assign(stats, r || {})
  } catch { /* 静默 */ }
  statsLoading.value = false
}

async function loadList(page = 1) {
  loading.value = true
  pagination.page = page
  try {
    const params: any = {
      page: pagination.page,
      per_page: pagination.per_page,
    }
    if (searchForm.project_id) params.project_id = searchForm.project_id
    if (searchForm.process_instance_id) params.process_instance_id = searchForm.process_instance_id
    if (searchForm.result) params.result = searchForm.result
    const range = filterBarRef.value?.dateRange
    if (range && range.length === 2) {
      params.start_date = range[0]
      params.end_date = range[1]
    }
    const r: any = await processApi.inspectionList(params)
    const data = r?.data ?? r
    list.value = (data?.data || data || []) as Inspection[]
    pagination.total = data?.total ?? list.value.length
  } catch { /* toast */ }
  loading.value = false
}

async function loadProjectOptions() {
  try {
    const r: any = await getProjectList({ per_page: 500 })
    const arr = r?.data ?? r ?? []
    projectOptions.value = (Array.isArray(arr) ? arr : arr.data || []).map((p: any) => ({ id: p.id, name: p.name || p.code }))
  } catch { /* 静默 */ }
}

async function loadProcessInstanceOptions() {
  try {
    const r: any = await processApi.instanceList({ per_page: 500 })
    const arr = r?.data?.data ?? r?.data ?? r ?? []
    processInstanceOptions.value = (Array.isArray(arr) ? arr : []).map((i: any) => ({
      id: i.id,
      label: `[#${i.id}] ${i.template_name || i.name || ''}`,
    }))
  } catch { /* 静默 */ }
}

function handleSearch() {
  pagination.page = 1
  loadList(1)
}

function handleReset() {
  searchForm.project_id = null
  searchForm.process_instance_id = null
  searchForm.result = ''
  if (filterBarRef.value?.dateRange) filterBarRef.value.dateRange = null
  pagination.page = 1
  loadList(1)
}

const goInstance = (row: Inspection) => {
  if (!row.process_instance_id) return
  router.push(`/construction/process/instances/detail/${row.process_instance_id}`)
}

onMounted(() => {
  // 从 query 自动填项目过滤 (项目详情 → 施工进度 tab 跳转)
  const qProjectId = Number(route.query.project_id)
  if (qProjectId) {
    searchForm.project_id = qProjectId
  }
  loadStats()
  loadProjectOptions()
  loadProcessInstanceOptions()
  loadList(1)
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 16px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
