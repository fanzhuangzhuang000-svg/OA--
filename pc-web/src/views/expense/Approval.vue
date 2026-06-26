<template>
  <div class="page-container">
    <div class="page-header">
      <h2>审批管理</h2>
    </div>
    <div class="content-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待我审批" name="pending">
          <el-table v-loading="loading.pending" :data="pendingData" stripe border style="width: 100%">
            <el-table-column prop="claim_no" label="报销单号" width="160" />
            <el-table-column label="申请人" width="110">
              <template #default="{ row }">{{ row.user?.name || '-' }}</template>
            </el-table-column>
            <el-table-column label="费用类别" width="110" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category_label || row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="金额(元)" width="120" align="right">
              <template #default="{ row }">
                <span style="font-weight: 600; color: #0C447C">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="关联项目" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.project">{{ row.project.name }}</span>
                <span v-else class="muted">无</span>
              </template>
            </el-table-column>
            <el-table-column label="提交日期" width="160">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="220" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
                <el-button link type="success" size="small" @click="handleApprove(row)">通过</el-button>
                <el-button link type="danger" size="small" @click="handleReject(row)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination
              background
              layout="total, prev, pager, next"
              :total="pendingTotal"
              :current-page="pendingPage"
              :page-size="pendingPerPage"
              @current-change="(p) => { pendingPage = p; loadPending() }"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="已审批" name="done">
          <el-table v-loading="loading.done" :data="doneData" stripe border style="width: 100%">
            <el-table-column prop="claim_no" label="报销单号" width="160" />
            <el-table-column label="申请人" width="110">
              <template #default="{ row }">{{ row.user?.name || '-' }}</template>
            </el-table-column>
            <el-table-column label="费用类别" width="110" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category_label || row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="金额(元)" width="120" align="right">
              <template #default="{ row }">
                <span style="font-weight: 600; color: #0C447C">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="审批结果" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'approved' ? 'success' : 'danger'" size="small">
                  {{ row.status_label || row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="审批人" width="100">
              <template #default="{ row }">{{ row.approver?.name || '-' }}</template>
            </el-table-column>
            <el-table-column label="审批日期" width="160">
              <template #default="{ row }">{{ formatDate(row.approved_at) }}</template>
            </el-table-column>
            <el-table-column label="驳回原因" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.reject_reason" style="color:#f56c6c;">{{ row.reject_reason }}</span>
                <span v-else class="muted">-</span>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination
              background
              layout="total, prev, pager, next"
              :total="doneTotal"
              :current-page="donePage"
              :page-size="donePerPage"
              @current-change="(p) => { donePage = p; loadDone() }"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="我发起的" name="mine">
          <el-table v-loading="loading.mine" :data="mineData" stripe border style="width: 100%">
            <el-table-column prop="claim_no" label="报销单号" width="160" />
            <el-table-column label="费用类别" width="110" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category_label || row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="金额(元)" width="120" align="right">
              <template #default="{ row }">
                <span style="font-weight: 600; color: #0C447C">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
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
            <el-table-column label="提交日期" width="160">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination
              background
              layout="total, prev, pager, next"
              :total="mineTotal"
              :current-page="minePage"
              :page-size="minePerPage"
              @current-change="(p) => { minePage = p; loadMine() }"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 详情对话框 -->
    <ApprovalDetailDialog
      v-model:visible="showDetailDialog"
      :row="detailRow"
      :loading="detailLoading"
      :status-type="expenseStatusType"
      :format-date="formatDate"
      @action="handleDetailAction"
    />

    <!-- 驳回原因对话框 -->
    <RejectDialog
      v-model:visible="showRejectDialog"
      :form="rejectForm"
      :target="rejectTarget"
      :loading="rejectLoading"
      @confirm="confirmReject"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post } from '@/utils/request'
import ApprovalDetailDialog from './components/approval/ApprovalDetailDialog.vue'
import RejectDialog from './components/approval/RejectDialog.vue'

const router = useRouter()
const activeTab = ref('pending')

type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

const expenseStatusType = (s: string): TagType => {
  const map: Record<string, TagType> = {
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

// ===== 待审批 =====
const pendingData = ref<any[]>([])
const pendingTotal = ref(0)
const pendingPage = ref(1)
const pendingPerPage = ref(15)

async function loadPending() {
  const key = 'pending' as const
  loading[key] = true
  try {
    const res: any = await get('/expenses', { status: 'submitted', page: pendingPage.value, per_page: pendingPerPage.value })
    pendingData.value = res.data || res.items || res || []
    pendingTotal.value = res.total || pendingData.value.length
  } catch (e) {
    console.error('[loadPending]', e)
    pendingData.value = []
    pendingTotal.value = 0
  } finally {
    loading[key] = false
  }
}

// ===== 已审批 =====
const doneData = ref<any[]>([])
const doneTotal = ref(0)
const donePage = ref(1)
const donePerPage = ref(15)

async function loadDone() {
  const key = 'done' as const
  loading[key] = true
  try {
    // 一次拉取 approved + rejected
    const [a, r]: any[] = await Promise.all([
      get('/expenses', { status: 'approved',  page: donePage.value, per_page: donePerPage.value }),
      get('/expenses', { status: 'rejected',  page: donePage.value, per_page: donePerPage.value }),
    ])
    const listA = a.data || a.items || a || []
    const listR = r.data || r.items || r || []
    doneData.value = [...listA, ...listR].sort((x, y) =>
      new Date(y.approved_at || y.created_at).getTime() - new Date(x.approved_at || x.created_at).getTime()
    )
    doneTotal.value = (a.total || listA.length) + (r.total || listR.length)
  } catch (e) {
    console.error('[loadDone]', e)
    doneData.value = []
    doneTotal.value = 0
  } finally {
    loading[key] = false
  }
}

// ===== 我发起的 =====
const mineData = ref<any[]>([])
const mineTotal = ref(0)
const minePage = ref(1)
const minePerPage = ref(15)

async function loadMine() {
  const key = 'mine' as const
  loading[key] = true
  try {
    const res: any = await get('/expenses/my', { page: minePage.value, per_page: minePerPage.value })
    mineData.value = res.data || res.items || res || []
    mineTotal.value = res.total || mineData.value.length
  } catch (e) {
    console.error('[loadMine]', e)
    mineData.value = []
    mineTotal.value = 0
  } finally {
    loading[key] = false
  }
}

const loading = reactive({ pending: false, done: false, mine: false })

function handleTabChange(name: string | number) {
  const tab = String(name)
  if (tab === 'pending') loadPending()
  else if (tab === 'done') loadDone()
  else if (tab === 'mine') loadMine()
}

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

// ===== 审批通过 =====
function handleDetailAction(a: 'approve' | 'reject') {
  if (!detailRow.value) return
  if (a === 'approve') handleApprove(detailRow.value)
  else handleReject(detailRow.value)
}

async function handleApprove(row: any) {
  await ElMessageBox.confirm(
    `确认通过 ${row.user?.name || ''} 的报销单 ${row.claim_no}（¥${Number(row.total_amount || 0).toFixed(2)}）？`,
    '审批通过',
    { type: 'success', confirmButtonText: '通过' }
  )
  try {
    await post(`/expenses/${row.id}/approve`, { action: 'approved' })
    ElMessage.success(`${row.claim_no} 已审批通过`)
    loadPending()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '审批失败')
  }
}

// ===== 驳回 =====
const showRejectDialog = ref(false)
const rejectTarget = ref<any>(null)
const rejectForm = reactive({ comment: '' })
const rejectLoading = ref(false)

function handleReject(row: any) {
  rejectTarget.value = row
  rejectForm.comment = ''
  showRejectDialog.value = true
}

async function confirmReject() {
  if (!rejectForm.comment.trim()) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  rejectLoading.value = true
  try {
    await post(`/expenses/${rejectTarget.value.id}/approve`, {
      action:  'rejected',
      comment: rejectForm.comment.trim(),
    })
    ElMessage.success(`${rejectTarget.value.claim_no} 已驳回`)
    showRejectDialog.value = false
    loadPending()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '驳回失败')
  } finally {
    rejectLoading.value = false
  }
}

onMounted(() => { loadPending() })
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header {
  margin-bottom: 16px;
  h2 { font-size: 20px; color: #0C447C; margin: 0; }
}
.content-card {
  background: #fff; border-radius: 8px; padding: 16px 24px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.pagination-wrap {
  display: flex; justify-content: flex-end; margin-top: 16px;
}
.muted { color: #c0c4cc; }
</style>
