<template>
  <div class="page-container">
    <div class="page-header">
      <h2>报销管理</h2>
      <div class="header-stats" v-if="stats">
        <span class="stat-chip">合计 {{ stats.total }} 单</span>
        <span class="stat-chip stat-pending">待审批 {{ stats.pending }}</span>
        <span class="stat-chip stat-approved">已审批 {{ stats.approved }}</span>
        <span class="stat-chip stat-paid">已付款 {{ stats.paid }}</span>
        <span class="stat-chip stat-money">总额 ¥{{ Number(stats.totalAmount || 0).toFixed(2) }}</span>
      </div>
    </div>

    <div class="filter-bar">
      <el-input v-model="searchForm.keyword" placeholder="搜索报销单号/事由/申请人" clearable style="width: 240px" @keyup.enter="loadList(1)" />
      <el-select v-model="searchForm.status" placeholder="审批状态" clearable style="width: 140px">
        <el-option v-for="o in statusOptions" :key="o.value" :label="o.label" :value="o.value" />
      </el-select>
      <el-select v-model="searchForm.category" placeholder="费用类别" clearable style="width: 140px">
        <el-option v-for="o in categoryOptions" :key="o.value" :label="o.label" :value="o.value" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="loadList(1)">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
      <el-button type="primary" plain :icon="Plus" @click="handleApply">申请报销</el-button>
    </div>

    <div class="content-card">
      <el-table v-loading="loading" :data="list" stripe border style="width: 100%">
        <el-table-column prop="claim_no" label="报销单号" width="160" />
        <el-table-column label="申请人" width="110">
          <template #default="{ row }">
            {{ row.user?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="费用类别" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category_label || row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额(元)" width="120" align="right">
          <template #default="{ row }">
            <span style="font-weight: 600; color: #0C447C">{{ Number(row.total_amount || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联项目" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.project">{{ row.project.name }}</span>
            <span v-else class="muted">无</span>
          </template>
        </el-table-column>
        <el-table-column label="审批状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="expenseStatusType(row.status)" size="small">{{ row.status_label || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交日期" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button v-if="canCancel(row)" link type="warning" size="small" @click="handleCancel(row)">撤销</el-button>
            <el-button v-if="canDelete(row)" link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            <el-button v-if="canPay(row)" link type="success" size="small" @click="handlePay(row)">付款</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          :current-page="pagination.page"
          :page-size="pagination.per_page"
          :page-sizes="[10, 20, 50]"
          @current-change="(p) => loadList(p)"
          @size-change="(s) => { pagination.per_page = s; loadList(1) }"
        />
      </div>
    </div>

    <!-- 详情对话框 -->
    <ExpenseDetailDialog
      v-model:visible="showDetailDialog"
      :row="detailRow"
      :loading="detailLoading"
      :status-type="expenseStatusType"
      :format-date="formatDate"
      :can-cancel="canCancel"
      :can-delete="canDelete"
      :can-pay="canPay"
      @action="handleDetailAction"
    />

    <!-- 付款对话框 -->
    <ExpensePayDialog
      v-model:visible="showPayDialog"
      :form="payForm"
      :target="payTarget"
      :loading="payLoading"
      @confirm="confirmPay"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { get, post, del } from '@/utils/request'
import { useUserStore } from '@/stores/user'
import ExpenseDetailDialog from './components/index/ExpenseDetailDialog.vue'
import ExpensePayDialog from './components/index/ExpensePayDialog.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// ===== 状态选项 =====
const statusOptions = [
  { value: 'submitted', label: '待审批' },
  { value: 'approved',  label: '已审批' },
  { value: 'rejected',  label: '已驳回' },
  { value: 'paid',      label: '已付款' },
  { value: 'cancelled', label: '已撤销' },
  { value: 'draft',     label: '草稿' },
]

const categoryOptions = [
  { value: 'travel',       label: '差旅费' },
  { value: 'hospitality',  label: '招待费' },
  { value: 'office',       label: '办公费' },
  { value: 'transport',    label: '交通费' },
  { value: 'project_cost', label: '项目成本' },
  { value: 'other',        label: '其他' },
]

const expenseStatusType = (s: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    submitted: 'warning',
    approved:  'success',
    rejected:  'danger',
    paid:      'success',
    cancelled: 'info',
    draft:     'info',
  }
  return map[s] || 'info'
}

const formatDate = (s?: string) => {
  if (!s) return '-'
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const searchForm = ref({ keyword: '', status: '', category: '' })
const list = ref<any[]>([])
const loading = ref(false)
const pagination = reactive({ page: 1, per_page: 15, total: 0 })
const stats = ref<any>(null)

async function loadList(page = 1) {
  pagination.page = page
  loading.value = true
  try {
    const params: any = { page, per_page: pagination.per_page }
    if (searchForm.value.keyword)  params.keyword  = searchForm.value.keyword
    if (searchForm.value.status)   params.status   = searchForm.value.status
    if (searchForm.value.category) params.category = searchForm.value.category
    const res: any = await get('/expenses', params)
    list.value = res.data || res.items || res || []
    pagination.total = res.total || (Array.isArray(list.value) ? list.value.length : 0)
    if (res.current_page) pagination.page = res.current_page
  } catch (e) {
    console.error('[loadList]', e)
    list.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const res: any = await get('/expenses/stats')
    stats.value = res.data || res || null
  } catch (e) {
    console.warn('[loadStats]', e)
  }
}

function resetSearch() {
  searchForm.value = { keyword: '', status: '', category: '' }
  loadList(1)
}

function handleApply() { router.push('/expense/apply') }

// ===== 详情 =====
const showDetailDialog = ref(false)
const detailRow = ref<any>(null)
const detailLoading = ref(false)

async function handleView(row: any) {
  detailRow.value = row
  showDetailDialog.value = true
  detailLoading.value = true
  try {
    const res: any = await get(`/expenses/${row.id}`)
    detailRow.value = res.data || res
  } catch (e) {
    console.error('[handleView]', e)
  } finally {
    detailLoading.value = false
  }
}

const currentUserId = computed(() => userStore.userInfo?.id)

function canCancel(row: any) {
  if (!row) return false
  if (row.user_id && currentUserId.value && row.user_id !== currentUserId.value) return false
  return ['submitted', 'draft'].includes(row.status)
}

function canDelete(row: any) {
  if (!row) return false
  if (['approved', 'paid'].includes(row.status)) return false
  // 删除权限：自己 OR 管理员
  if (row.user_id && currentUserId.value && row.user_id === currentUserId.value) return true
  return userStore.hasPermission('expense.delete')
}

function canPay(row: any) {
  return row?.status === 'approved'
}

function handleDetailAction(action: 'cancel' | 'delete' | 'pay') {
  if (!detailRow.value) return
  if (action === 'cancel') handleCancel(detailRow.value)
  else if (action === 'delete') handleDelete(detailRow.value)
  else if (action === 'pay') handlePay(detailRow.value)
}

async function handleCancel(row: any) {
  await ElMessageBox.confirm(
    `确认撤销报销单 ${row.claim_no}？撤销后可重新提交。`,
    '撤销确认',
    { type: 'warning', confirmButtonText: '确认撤销' }
  )
  try {
    await post(`/expenses/${row.id}/cancel`)
    ElMessage.success(`${row.claim_no} 已撤销`)
    loadList(pagination.page)
    loadStats()
    if (showDetailDialog.value) handleView(row)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '撤销失败')
  }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(
    `确认删除报销单 ${row.claim_no}？删除后不可恢复。`,
    '删除确认',
    { type: 'error', confirmButtonText: '确认删除' }
  )
  try {
    await del(`/expenses/${row.id}`)
    ElMessage.success(`${row.claim_no} 已删除`)
    loadList(pagination.page)
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '删除失败')
  }
}

// ===== 付款 =====
const showPayDialog = ref(false)
const payTarget = ref<any>(null)
const payLoading = ref(false)
const payForm = reactive({ paid_amount: 0 })

function handlePay(row: any) {
  payTarget.value = row
  payForm.paid_amount = Number(row.total_amount || 0)
  showPayDialog.value = true
}

async function confirmPay() {
  if (payForm.paid_amount <= 0) {
    ElMessage.warning('请输入付款金额')
    return
  }
  payLoading.value = true
  try {
    await post(`/expenses/${payTarget.value.id}/pay`, { paid_amount: payForm.paid_amount })
    ElMessage.success(`${payTarget.value.claim_no} 已标记付款`)
    showPayDialog.value = false
    loadList(pagination.page)
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '付款失败')
  } finally {
    payLoading.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadList(1), loadStats()])
  // 处理 ?view=ID 自动打开详情
  const viewId = route.query.view as string
  if (viewId) {
    const row = list.value.find((r: any) => String(r.id) === String(viewId) || r.claim_no === viewId)
    if (row) handleView(row)
  }
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
  h2 { font-size: 20px; color: #0C447C; margin: 0; }
}
.header-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.stat-chip {
  background: #fff;
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 13px;
  color: #606266;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  &.stat-pending  { color: #e6a23c; }
  &.stat-approved { color: #67c23a; }
  &.stat-paid     { color: #0C447C; font-weight: 600; }
  &.stat-money    { color: #f56c6c; font-weight: 600; }
}
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  flex-wrap: wrap;
}
.content-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.muted { color: #c0c4cc; }
</style>
