<template>
  <div class="page-container">
    <div class="page-header">
      <div class="title-area">
        <span class="page-title">工序模板管理</span>
        <el-tag effect="light" type="info">{{ total }} 个模板</el-tag>
      </div>
      <div class="header-actions">
        <el-button :icon="RefreshRight" plain @click="loadAll">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleCreate">新建模板</el-button>
      </div>
    </div>

    <TemplateStatCards :stats="stats" />

    <TemplateFilterBar
      :form="searchForm"
      @search="handleSearch"
      @reset="handleReset"
    />

    <div class="content-card">
      <TemplateTable
        :list="list"
        :loading="loading"
        @edit="handleEdit"
        @delete="handleDelete"
        @status-change="handleStatusChange"
      />

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </div>

    <TemplateFormDialog
      v-model="dialogVisible"
      :mode="dialogMode"
      :form="form"
      :loading="dialogLoading"
      @submit="handleDialogSubmit"
      @closed="handleDialogClosed"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, RefreshRight } from '@element-plus/icons-vue'
import { processApi } from '@/api/modules'

import TemplateStatCards from './components/template-list/TemplateStatCards.vue'
import TemplateFilterBar from './components/template-list/TemplateFilterBar.vue'
import TemplateTable from './components/template-list/TemplateTable.vue'
import TemplateFormDialog from './components/template-list/TemplateFormDialog.vue'

import type { ProcessTemplate, SearchForm, TemplateStats } from './components/template-list/types'
import { emptyStats, defaultTemplateForm } from './components/template-list/types'

// v0.3.25 拆 TemplateList.vue 568→170 (-70%)
// 子组件: StatCards / FilterBar / Table / FormDialog

const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const list = ref<ProcessTemplate[]>([])

const stats = reactive<TemplateStats>(emptyStats())
const searchForm = reactive<SearchForm>({ industry: '', keyword: '' })

const todayLabel = (): string => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (searchForm.industry) params.industry = searchForm.industry
    if (searchForm.keyword) params.keyword = searchForm.keyword

    const r: any = await processApi.templateList(params)
    const data = r?.data ?? r
    const rows = data?.data ?? data?.list ?? []
    list.value = Array.isArray(rows) ? rows.map((it: any) => ({ ...it, _statusLoading: false })) : []
    total.value = data?.total ?? list.value.length

    computeStatsFromList()
  } catch (e: any) {
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function computeStatsFromList() {
  stats.total = total.value
  const activeInPage = list.value.filter((t) => Number(t.status) === 1).length
  if (list.value.length > 0) {
    stats.active = Math.round((activeInPage / list.value.length) * total.value)
  } else {
    stats.active = 0
  }
  const industrySet = new Set(list.value.map((t) => t.industry).filter(Boolean))
  stats.industryCount = industrySet.size
  const today = todayLabel()
  stats.todayNew = list.value.filter((t) => t.created_at && String(t.created_at).slice(0, 10) === today).length
}

function loadAll() {
  loadList()
}

const handleSearch = () => { page.value = 1; loadList() }
const handleReset = () => {
  searchForm.industry = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}

async function handleStatusChange(row: ProcessTemplate, val: number | string | boolean) {
  const newStatus = Number(val) === 1 ? 1 : 0
  row._statusLoading = true
  try {
    await processApi.templateUpdate(row.id, {
      industry: row.industry,
      code: row.code,
      name: row.name,
      sort_order: row.sort_order,
      duration_days: row.duration_days,
      acceptance_points: row.acceptance_points,
      status: newStatus,
    })
    ElMessage.success(newStatus === 1 ? '已启用' : '已停用')
    computeStatsFromList()
  } catch (e: any) {
    row.status = newStatus === 1 ? 0 : 1
    ElMessage.error(e?.message || '状态更新失败')
  } finally {
    row._statusLoading = false
  }
}

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const form = reactive(defaultTemplateForm())

function handleCreate() {
  dialogMode.value = 'create'
  Object.assign(form, defaultTemplateForm())
  dialogVisible.value = true
}

function handleEdit(row: ProcessTemplate) {
  dialogMode.value = 'edit'
  Object.assign(form, {
    id: row.id,
    industry: row.industry,
    code: row.code,
    name: row.name,
    sort_order: row.sort_order ?? 0,
    duration_days: row.duration_days ?? 0,
    acceptance_points: row.acceptance_points ?? '',
    status: Number(row.status) === 1 ? 1 : 0,
  })
  dialogVisible.value = true
}

async function handleDialogSubmit() {
  const formRef = (document.querySelector('.el-dialog__wrapper .el-form') as any)
  if (!formRef) return
  try {
    await formRef.validate()
  } catch {
    return
  }
  dialogLoading.value = true
  try {
    const payload = {
      industry: form.industry,
      code: form.code,
      name: form.name,
      sort_order: form.sort_order,
      duration_days: form.duration_days,
      acceptance_points: form.acceptance_points,
      status: form.status,
    }
    if (dialogMode.value === 'create') {
      await processApi.templateCreate(payload)
      ElMessage.success('创建成功')
    } else {
      await processApi.templateUpdate(form.id, payload)
      ElMessage.success('保存成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.message || (dialogMode.value === 'create' ? '创建失败' : '保存失败'))
  } finally {
    dialogLoading.value = false
  }
}

function handleDialogClosed() {
  Object.assign(form, defaultTemplateForm())
}

async function handleDelete(row: ProcessTemplate) {
  try {
    await processApi.templateDelete(row.id)
    ElMessage.success('删除成功')
    if (list.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

onMounted(() => {
  loadAll()
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 16px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .title-area { display: flex; align-items: center; gap: 10px; }
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
  .header-actions { display: flex; gap: 8px; }
}
.content-card {
  background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
