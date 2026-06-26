<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">项目预算管理</span>
      <div class="header-actions">
        <el-button :icon="Refresh" plain @click="handleReset">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增预算</el-button>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="项目">
          <el-select
            v-model="searchForm.project_id"
            placeholder="全部项目"
            clearable
            filterable
            style="width: 220px"
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="`${p.code ? p.code + ' - ' : ''}${p.name || ''}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="编号 / 备注" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="content-card">
      <BudgetTable
        :data="pagedList"
        :loading="loading"
        @view="handleView"
        @edit="handleEdit"
        @approve="handleApprove"
        @revise="handleReviseFromTable"
        @delete="handleDelete"
      />

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="filteredList.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </div>

    <!-- 新建 / 编辑 dialog -->
    <BudgetFormDialog
      v-model:visible="showFormDialog"
      :project-options="projectOptions"
      :editing="editingBudget"
      @save="handleSave"
    />

    <!-- 详情 dialog -->
    <BudgetDetailDialog
      v-model:visible="showDetailDialog"
      :budget-id="detailBudgetId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { construction } from '@/api/construction'
import { getProjectList } from '@/api/modules'
import BudgetTable from './components/BudgetTable.vue'
import BudgetFormDialog from './components/BudgetFormDialog.vue'
import BudgetDetailDialog from './components/BudgetDetailDialog.vue'

const route = useRoute()
const userStore = useUserStore()

// 状态：draft/approved/revised/voided
const statusOptions = [
  { value: 'draft',    label: '草稿' },
  { value: 'approved', label: '已审批' },
  { value: 'revised',  label: '已修订' },
  { value: 'voided',   label: '已作废' },
]

const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const list = ref<any[]>([])

const searchForm = reactive<{ project_id: number | null; status: string; keyword: string }>({
  project_id: null,
  status: '',
  keyword: '',
})

const projectOptions = ref<any[]>([])

// === 过滤 / 分页（前端） ===
const filteredList = computed(() => {
  let arr = [...list.value]
  if (searchForm.project_id) arr = arr.filter(r => Number(r.project_id) === Number(searchForm.project_id))
  if (searchForm.status) arr = arr.filter(r => r.status === searchForm.status)
  if (searchForm.keyword) {
    const kw = searchForm.keyword.toLowerCase()
    arr = arr.filter(r =>
      (r.code || '').toLowerCase().includes(kw) ||
      (r.remark || '').toLowerCase().includes(kw) ||
      (r.project?.name || '').toLowerCase().includes(kw) ||
      (r.project?.code || '').toLowerCase().includes(kw)
    )
  }
  return arr
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

// === 数据加载 ===
const loadList = async () => {
  loading.value = true
  try {
    const params: any = { per_page: 500, page: 1 }
    if (searchForm.project_id) params.project_id = searchForm.project_id
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const res: any = await construction.listBudgets(params)
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    list.value = arr
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const res: any = await getProjectList({ per_page: 500 })
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    projectOptions.value = arr.map((p: any) => ({ id: p.id, code: p.code, name: p.name }))
  } catch {
    projectOptions.value = []
  }
}

const handleSearch = () => { page.value = 1 }
const handleReset = () => {
  searchForm.project_id = null
  searchForm.status = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}

// === 新建 / 编辑 ===
const showFormDialog = ref(false)
const editingBudget = ref<any>(null)

const handleAdd = () => {
  editingBudget.value = null
  showFormDialog.value = true
}

const handleEdit = (row: any) => {
  if (row.status !== 'draft') {
    ElMessage.warning('仅「草稿」状态可编辑')
    return
  }
  editingBudget.value = row
  showFormDialog.value = true
}

const handleSave = async (payload: { project_id: number; items: any[]; remark: string }) => {
  try {
    if (editingBudget.value?.id) {
      await construction.updateBudget(editingBudget.value.id, payload)
      ElMessage.success('预算已更新')
    } else {
      await construction.createBudget(payload)
      ElMessage.success('预算已创建')
    }
    showFormDialog.value = false
    editingBudget.value = null
    page.value = 1
    await loadList()
  } catch {
    /* 拦截器已提示 */
  }
}

// === 详情 ===
const showDetailDialog = ref(false)
const detailBudgetId = ref<number | undefined>(undefined)

const handleView = (row: any) => {
  detailBudgetId.value = row.id
  showDetailDialog.value = true
}

// === 审批 ===
const handleApprove = async (row: any) => {
  if (row.status !== 'draft') {
    ElMessage.warning('仅「草稿」状态可审批')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认审批预算「${row.code}」？审批后不能再编辑。`,
      '批准确认',
      { type: 'success', confirmButtonText: '确认审批', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    await construction.approveBudget(row.id)
    ElMessage.success('已审批')
    await loadList()
  } catch { /* 拦截器已提示 */ }
}

// === 修订（表格 / 详情） ===
const handleReviseFromTable = async (row: any) => {
  if (row.status !== 'approved') {
    ElMessage.warning('仅「已审批」状态可修订')
    return
  }
  let remark = ''
  try {
    const { value } = await ElMessageBox.prompt('请输入修订原因（可选）', '修订预算', {
      inputType: 'textarea',
      inputPlaceholder: '修订原因',
    })
    remark = value
  } catch { return }
  try {
    await construction.reviseBudget(row.id, { remark, reason: remark })
    ElMessage.success('已提交修订')
    await loadList()
  } catch { /* 拦截器已提示 */ }
}

// === 删除 ===
const handleDelete = async (row: any) => {
  if (row.status !== 'draft') {
    ElMessage.warning('仅「草稿」状态可删除')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认删除预算「${row.code}」？该操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    await construction.deleteBudget(row.id)
    ElMessage.success('已删除')
    await loadList()
    if (pagedList.value.length === 0 && page.value > 1) page.value -= 1
  } catch { /* 拦截器已提示 */ }
}

// === 路由参数 ?project_id= 自动筛选 ===
const applyRouteFilter = () => {
  const q = (route.query.project_id || route.query.projectId) as string | undefined
  if (q && !Number.isNaN(Number(q))) {
    searchForm.project_id = Number(q)
  }
}
watch(() => route.query.project_id, () => { applyRouteFilter(); page.value = 1; loadList() })

onMounted(() => {
  // 触发 userStore（演示项目结构使用）
  if (!userStore.userInfo) { /* 占位 — 主页面主要使用路由参数 + 列表数据 */ }
  applyRouteFilter()
  loadProjects()
  loadList()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .page-title {
    font-size: 18px; font-weight: 600; color: #0C447C;
    border-left: 4px solid #0C447C; padding-left: 10px;
  }
  .header-actions { display: flex; gap: 8px; }
}
.filter-bar {
  background: #fff; padding: 16px 20px; border-radius: 8px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.content-card {
  background: #fff; padding: 20px; border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.pagination-wrapper {
  margin-top: 16px;
  display: flex; justify-content: flex-end;
}
</style>
