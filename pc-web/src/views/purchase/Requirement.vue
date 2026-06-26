<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">采购需求管理</span>
      <div class="header-actions">
        <el-button :icon="Download" plain @click="handleExport">导出</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建需求</el-button>
      </div>
    </div>

    <RequirementFilterBar
      :filters="searchForm"
      :project-options="projectOptions"
      @search="handleSearch"
      @reset="handleReset"
    />

    <div class="content-card">
      <RequirementStatCards :stats="stats" :list="list" />

      <RequirementTable
        :list="pagedList"
        :loading="loading"
        @view="handleView"
        @view-project="handleViewProject"
        @edit="handleEdit"
        @delete="handleDelete"
      />

      <el-empty v-if="!loading && pagedList.length === 0" description="暂无采购需求" :image-size="80" />

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="filteredList.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <RequirementFormDialog
      v-model="showFormDialog"
      :mode="formMode"
      :form="formData"
      :loading="submitting"
      :project-options="projectOptions"
      @submit="handleSave"
      @add-material="addMaterial"
      @remove-material="removeMaterial"
    />

    <RequirementDetailDrawer
      v-model="showDetailDrawer"
      :item="currentItem"
      @view-project="handleViewProject"
      @edit="handleEditFromDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { purchase } from '@/api/modules'
import { getProjectList } from '@/api/modules'
import { exportExcelLike } from '@/utils/exporter'

import RequirementFilterBar from './components/requirement/RequirementFilterBar.vue'
import RequirementStatCards from './components/requirement/RequirementStatCards.vue'
import RequirementTable from './components/requirement/RequirementTable.vue'
import RequirementFormDialog from './components/requirement/RequirementFormDialog.vue'
import RequirementDetailDrawer from './components/requirement/RequirementDetailDrawer.vue'

import type {
  Requirement, RequirementFilters, RequirementForm, ProjectOption, FormMode,
} from './components/requirement/types'
import {
  statusLabel, priorityLabel, formatDate, emptyForm,
} from './components/requirement/types'

// v0.3.23 拆 Requirement.vue 727→260 (-64%)
// 子组件: FilterBar / StatCards / Table / FormDialog / DetailDrawer

const loading = ref(false)
const submitting = ref(false)
const list = ref<Requirement[]>([])
const stats = reactive({ pending: 0, approved: 0, rejected: 0, cancelled: 0, total: 0 })
const projectOptions = ref<ProjectOption[]>([])

const page = ref(1)
const pageSize = ref(10)

const searchForm = reactive<RequirementFilters>({
  project_id: null,
  status: '',
  priority: '',
  keyword: '',
})

const filteredList = computed(() => {
  let arr = [...list.value]
  if (searchForm.project_id) arr = arr.filter((r) => r.project_id === searchForm.project_id)
  if (searchForm.status) arr = arr.filter((r) => r.status === searchForm.status)
  if (searchForm.priority) arr = arr.filter((r) => r.priority === searchForm.priority)
  if (searchForm.keyword) {
    const kw = searchForm.keyword.toLowerCase()
    arr = arr.filter((r) =>
      (r.code || '').toLowerCase().includes(kw) ||
      (r.material || '').toLowerCase().includes(kw)
    )
  }
  return arr.sort((a, b) => {
    if (a.priority !== b.priority) return a.priority === 'urgent' ? -1 : 1
    return (a.need_date || '').localeCompare(b.need_date || '')
  })
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

// ====================== 数据加载 ======================
const loadList = async () => {
  loading.value = true
  try {
    const params: any = { page: 1, per_page: 200 }
    if (searchForm.project_id) params.project_id = searchForm.project_id
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.priority) params.priority = searchForm.priority
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const res: any = await purchase.getRequirements(params)
    const arr = (res && Array.isArray(res.data)) ? res.data : []
    list.value = arr
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res: any = await purchase.getRequirementStats()
    Object.assign(stats, res || {})
  } catch { /* 静默 */ }
}

const loadProjects = async () => {
  try {
    const res: any = await getProjectList({ per_page: 200 })
    const arr = (res && Array.isArray(res.data)) ? res.data : []
    projectOptions.value = arr.map((p: any) => ({ id: p.id, name: p.name || p.code }))
  } catch {
    projectOptions.value = []
  }
}

// ====================== 表单 Dialog ======================
const showFormDialog = ref(false)
const formMode = ref<FormMode>('create')
const formData = reactive<RequirementForm>(emptyForm())

const handleAdd = () => {
  formMode.value = 'create'
  Object.assign(formData, emptyForm())
  showFormDialog.value = true
}

const handleEdit = (row: Requirement) => {
  if (row.status === 'approved') {
    ElMessage.warning('已通过的需求不可编辑')
    return
  }
  if (row.status === 'rejected') {
    ElMessage.warning('已驳回的需求不可编辑')
    return
  }
  formMode.value = 'edit'
  Object.assign(formData, {
    id: row.id,
    project_id: row.project_id,
    need_date: row.need_date ? String(row.need_date).slice(0, 10) : '',
    priority: row.priority || 'medium',
    creator: row.creator || '',
    materials: [{
      name: row.material,
      spec: row.spec || '',
      quantity: Number(row.quantity || 1),
      unit: row.unit || '件',
    }],
    remark: row.remark || '',
  })
  showFormDialog.value = true
}

const handleEditFromDetail = () => {
  if (currentItem.value) {
    handleEdit(currentItem.value)
    showDetailDrawer.value = false
  }
}

const addMaterial = () => {
  formData.materials.push({ name: '', spec: '', quantity: 1, unit: '件' })
}

const removeMaterial = (idx: number) => {
  if (formData.materials.length === 1) {
    ElMessage.warning('至少保留一条物资')
    return
  }
  formData.materials.splice(idx, 1)
}

const handleSave = async () => {
  for (let i = 0; i < formData.materials.length; i++) {
    const m = formData.materials[i]
    if (!m.name || !m.quantity) {
      ElMessage.warning(`第 ${i + 1} 行物资不完整`)
      return
    }
  }
  submitting.value = true
  try {
    const main = formData.materials[0]
    const payload: any = {
      project_id: formData.project_id || null,
      material: main.name,
      spec: main.spec || null,
      quantity: Number(main.quantity) || 0,
      unit: main.unit || '件',
      need_date: formData.need_date || null,
      priority: formData.priority || 'medium',
      creator: formData.creator || null,
      remark: formData.remark || null,
    }
    if (formMode.value === 'create') {
      await purchase.createRequirement(payload)
      ElMessage.success('采购需求创建成功')
    } else {
      await purchase.updateRequirement(formData.id, payload)
      ElMessage.success('采购需求已更新')
    }
    showFormDialog.value = false
    page.value = 1
    await loadList()
    await loadStats()
  } catch (e) {
    /* request 拦截器已 ElMessage */
  } finally {
    submitting.value = false
  }
}

// ====================== 详情 Drawer ======================
const showDetailDrawer = ref(false)
const currentItem = ref<Requirement | null>(null)

const handleView = (row: Requirement) => {
  currentItem.value = row
  showDetailDrawer.value = true
}

const handleViewProject = (row: Requirement) => {
  ElMessage.info(`查看项目详情：${row.project_name || row.project_id}（占位）`)
}

// ====================== 删除 ======================
const handleDelete = async (row: Requirement) => {
  if (row.status === 'approved') {
    ElMessage.warning('已通过的需求不可删除')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除采购需求「${row.code}」吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await purchase.deleteRequirement(row.id)
    ElMessage.success('已删除')
    await loadList()
    await loadStats()
    if (pagedList.value.length === 0 && page.value > 1) page.value -= 1
  } catch (e) { /* request 拦截器已 ElMessage */ }
}

// ====================== 搜索 / 重置 / 导出 ======================
const handleSearch = () => { page.value = 1; loadList() }
const handleReset = () => {
  searchForm.project_id = null
  searchForm.status = ''
  searchForm.priority = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}
const handlePageChange = () => { /* computed 自动重算 */ }

const handleExport = () => {
  if (filteredList.value.length === 0) {
    ElMessage.warning('当前列表无数据可导出')
    return
  }
  const headers = ['需求编号', '关联项目', '需求物资', '规格', '数量', '单位', '需求日期', '优先级', '发起人', '状态', '发起时间']
  const rows = filteredList.value.map((r: any) => [
    r.code, r.project_name, r.material, r.spec || '',
    r.quantity, r.unit || '件', r.need_date,
    priorityLabel(r.priority), r.creator, statusLabel(r.status), r.created_at,
  ])
  exportExcelLike(headers, rows, '采购需求', { title: '采购需求清单' })
}

onMounted(() => {
  loadList()
  loadStats()
  loadProjects()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
  .header-actions { display: flex; gap: 8px; }
}
.content-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
