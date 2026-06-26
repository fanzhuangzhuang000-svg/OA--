<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">采购审批</span>
      <div class="header-actions">
        <el-tag :type="activeTab === 'pending' ? 'warning' : 'default'" effect="light" size="large">
          <el-icon><Bell /></el-icon>
          <span style="margin-left: 4px">待审批 {{ pendingData.length }} 条</span>
        </el-tag>
        <el-button :icon="Refresh" plain @click="loadAll">刷新</el-button>
      </div>
    </div>

    <ApprovalFilterBar
      v-model:keyword="searchForm.keyword"
      v-model:status="searchForm.status"
      v-model:approver="searchForm.approver"
      :status-options="statusOptions"
      :approver-options="approverOptions"
      @search="handleSearch"
      @reset="handleReset"
    />

    <div class="content-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 待审批 -->
        <el-tab-pane :name="'pending'">
          <template #label>
            <span><el-icon><Bell /></el-icon> 待审批 ({{ pendingData.length }})</span>
          </template>

          <div class="batch-bar" v-if="pendingSelection.length > 0">
            <el-alert type="info" :closable="false" show-icon>
              <template #title>已选择 <b>{{ pendingSelection.length }}</b> 条采购计划</template>
            </el-alert>
            <div class="batch-actions">
              <el-button type="success" :icon="Check" @click="handleBatchApprove">批量批准</el-button>
              <el-button type="danger" :icon="Close" @click="handleBatchReject">批量驳回</el-button>
              <el-button text @click="clearSelection('pending')">取消选择</el-button>
            </div>
          </div>

          <el-table
            ref="pendingTableRef"
            :data="filteredPending"
            stripe
            border
            v-loading="loading"
            :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
            @selection-change="(rows: any[]) => pendingSelection = rows"
          >
            <el-table-column type="selection" width="50" align="center" />
            <el-table-column prop="code" label="计划编号" width="160" fixed>
              <template #default="{ row }">
                <span class="link-text" @click="handleView(row)">{{ row.code }}</span>
              </template>
            </el-table-column>
            <el-table-column label="标题" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">{{ row.title }}</template>
            </el-table-column>
            <el-table-column label="关联需求" width="160" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="link-text" @click="handleView(row)">{{ getReqById(row.requirement_id)?.code || row.requirement_id || '-' }}</span>
                <div class="sub-text">{{ getReqById(row.requirement_id)?.material || '' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="{ row }">
                <span style="color: #0C447C; font-weight: 600">¥ {{ formatMoney(row.total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="90" align="center">
              <template #default="{ row }">{{ row.priority }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交时间" width="160" align="center" />
            <el-table-column label="状态" width="100" align="center">
              <template #default>
                <el-tag type="warning" effect="plain" size="small">待审批</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
                <el-button link type="success" size="small" @click="openApproveDialog(row, 'approve')">批准</el-button>
                <el-button link type="danger" size="small" @click="openApproveDialog(row, 'reject')">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 已通过 -->
        <el-tab-pane :name="'approved'">
          <template #label>
            <span><el-icon><Check /></el-icon> 已通过 ({{ approvedData.length }})</span>
          </template>
          <el-table
            :data="filteredApproved"
            stripe
            border
            v-loading="loading"
            :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
          >
            <el-table-column prop="code" label="计划编号" width="160" fixed>
              <template #default="{ row }">
                <span class="link-text" @click="handleView(row)">{{ row.code }}</span>
              </template>
            </el-table-column>
            <el-table-column label="标题" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">{{ row.title }}</template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="{ row }">
                <span style="color: #0C447C; font-weight: 600">¥ {{ formatMoney(row.total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="approver_id" label="审批人 ID" width="100" align="center" />
            <el-table-column prop="approved_at" label="审批时间" width="160" align="center" />
            <el-table-column label="状态" width="100" align="center">
              <template #default>
                <el-tag type="success" effect="plain" size="small">已通过</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 已驳回 -->
        <el-tab-pane :name="'rejected'">
          <template #label>
            <span><el-icon><Close /></el-icon> 已驳回 ({{ rejectedData.length }})</span>
          </template>
          <el-table
            :data="filteredRejected"
            stripe
            border
            v-loading="loading"
            :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
          >
            <el-table-column prop="code" label="计划编号" width="160" fixed>
              <template #default="{ row }">
                <span class="link-text" @click="handleView(row)">{{ row.code }}</span>
              </template>
            </el-table-column>
            <el-table-column label="标题" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">{{ row.title }}</template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="{ row }">
                <span style="color: #0C447C; font-weight: 600">¥ {{ formatMoney(row.total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="approver_id" label="审批人 ID" width="100" align="center" />
            <el-table-column prop="approved_at" label="审批时间" width="160" align="center" />
            <el-table-column label="驳回原因" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span style="color: #f56c6c">{{ row.approve_remark || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default>
                <el-tag type="danger" effect="plain" size="small">已驳回</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 审批 Dialog -->
    <el-dialog
      v-model="showApproveDialog"
      :title="approveAction === 'approve' ? '批准采购计划' : '驳回采购计划'"
      width="640px"
      :close-on-click-modal="false"
    >
      <div v-if="approveTarget">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="计划编号">{{ approveTarget.code }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ approveTarget.title }}</el-descriptions-item>
          <el-descriptions-item label="关联需求">
            {{ getReqById(approveTarget.requirement_id)?.code || approveTarget.requirement_id || '-' }}
            <div class="sub-text">{{ getReqById(approveTarget.requirement_id)?.material || '' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="金额">
            <span style="color: #0C447C; font-weight: 600">¥ {{ formatMoney(approveTarget.total_amount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">{{ approveTarget.priority }}</el-descriptions-item>
          <el-descriptions-item label="计划日期">{{ approveTarget.plan_date ? String(approveTarget.plan_date).slice(0, 10) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            <div style="white-space: pre-wrap">{{ approveTarget.remark || '（无）' }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <el-form :model="approveForm" label-width="100px" style="margin-top: 16px">
          <el-form-item :label="approveAction === 'approve' ? '批准意见' : '驳回原因'" required>
            <el-input
              v-model="approveForm.comment"
              type="textarea"
              :rows="3"
              :placeholder="approveAction === 'approve' ? '请输入批准意见（可选）' : '请说明驳回原因（必填）'"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showApproveDialog = false">取消</el-button>
        <el-button
          v-if="approveAction === 'approve'"
          type="success"
          :icon="Check"
          :loading="approving"
          @click="confirmApprove"
        >确认批准</el-button>
        <el-button
          v-if="approveAction === 'reject'"
          type="danger"
          :icon="Close"
          :loading="approving"
          @click="confirmApprove"
        >确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 查看 Dialog（只读） -->
    <el-dialog v-model="showViewDialog" title="采购计划详情" width="1500px" :close-on-click-modal="false">
      <div v-if="viewTarget">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="计划编号">{{ viewTarget.code }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ viewTarget.title }}</el-descriptions-item>
          <el-descriptions-item label="关联需求">
            {{ getReqById(viewTarget.requirement_id)?.code || viewTarget.requirement_id || '-' }}
            <div class="sub-text">{{ getReqById(viewTarget.requirement_id)?.material || '' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="金额">
            <span style="color: #0C447C; font-weight: 600">¥ {{ formatMoney(viewTarget.total_amount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">{{ viewTarget.priority }}</el-descriptions-item>
          <el-descriptions-item label="计划日期">{{ viewTarget.plan_date ? String(viewTarget.plan_date).slice(0, 10) : '-' }}</el-descriptions-item>
          <el-descriptions-item v-if="viewTarget.approver_id" label="审批人 ID">{{ viewTarget.approver_id }}</el-descriptions-item>
          <el-descriptions-item v-if="viewTarget.approved_at" label="审批时间">{{ viewTarget.approved_at }}</el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="statusTagType(viewTarget.status)" size="small">{{ statusLabel(viewTarget.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            <div style="white-space: pre-wrap">{{ viewTarget.remark || '（无）' }}</div>
          </el-descriptions-item>
          <el-descriptions-item v-if="viewTarget.approve_remark" label="审批备注" :span="2">
            <div style="white-space: pre-wrap">{{ viewTarget.approve_remark }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
        <el-button
          v-if="viewTarget && viewTarget.status === 'submitted'"
          type="success"
          :icon="Check"
          @click="showViewDialog = false; openApproveDialog(viewTarget, 'approve')"
        >批准</el-button>
        <el-button
          v-if="viewTarget && viewTarget.status === 'submitted'"
          type="danger"
          :icon="Close"
          @click="showViewDialog = false; openApproveDialog(viewTarget, 'reject')"
        >驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Bell, Check, Close } from '@element-plus/icons-vue'
import { purchase } from '@/api/modules'
import ApprovalFilterBar from './components/approval/ApprovalFilterBar.vue'

// ===== 状态选项（与后端 Plan status 一致） =====
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'submitted', label: '待审批' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已驳回' },
  { value: 'cancelled', label: '已取消' }
]

// ===== 数据（统一从 plans 拉，按 status 分类）=====
const loading = ref(false)
const planList = ref<any[]>([])
const requirementMap = ref<Record<number, any>>({})

const loadAll = async () => {
  loading.value = true
  try {
    const [plansRes, reqsRes] = await Promise.all([
      purchase.getPlans({ per_page: 200 }),
      purchase.getRequirements({ per_page: 200 }).catch(() => null)
    ])
    const arr = (plansRes && Array.isArray(plansRes.data)) ? plansRes.data : []
    planList.value = arr
    if (reqsRes && Array.isArray(reqsRes.data)) {
      const m: Record<number, any> = {}
      reqsRes.data.forEach((r: any) => { m[r.id] = r })
      requirementMap.value = m
    }
    ElMessage.success('已刷新')
  } catch {
    planList.value = []
  } finally {
    loading.value = false
  }
}

const getReqById = (id: number) => requirementMap.value[id] || null

// ===== 三态数据 =====
const pendingData = computed(() => planList.value.filter(p => p.status === 'submitted'))
const approvedData = computed(() => planList.value.filter(p => p.status === 'approved'))
const rejectedData = computed(() => planList.value.filter(p => p.status === 'rejected'))

// ===== 过滤 =====
const activeTab = ref('pending')
const searchForm = reactive({ keyword: '', status: '' })

const filterBySearch = (rows: any[]) => {
  return rows.filter(r => {
    if (searchForm.keyword) {
      const kw = searchForm.keyword.toLowerCase()
      if (!(r.code || '').toLowerCase().includes(kw) && !(r.title || '').toLowerCase().includes(kw)) return false
    }
    if (searchForm.status && r.status !== searchForm.status) return false
    return true
  })
}
const filteredPending = computed(() => filterBySearch(pendingData.value))
const filteredApproved = computed(() => filterBySearch(approvedData.value))
const filteredRejected = computed(() => filterBySearch(rejectedData.value))

const approverOptions = computed(() => {
  const set = new Set<string>()
  approvedData.value.forEach((d: any) => d.approver_id && set.add(`#${d.approver_id}`))
  rejectedData.value.forEach((d: any) => d.approver_id && set.add(`#${d.approver_id}`))
  return Array.from(set)
})

const handleSearch = () => { /* reactive computed will refresh */ }
const handleReset = () => { searchForm.keyword = ''; searchForm.status = ''; searchForm.approver = '' }
const handleTabChange = (_name: string | number) => { clearSelection('pending') }

// ===== 多选（只对 pending）=====
const pendingTableRef = ref()
const pendingSelection = ref<any[]>([])
const clearSelection = (_tab: string) => {
  pendingTableRef.value?.clearSelection()
  pendingSelection.value = []
}

// ===== 工具函数 =====
const formatMoney = (n: number) => Number(n || 0).toLocaleString('zh-CN', { maximumFractionDigits: 0 })
const statusTagType = (s: string): any => ({ draft: 'info', submitted: 'warning', approved: 'success', rejected: 'danger', cancelled: 'info' } as any)[s] || 'info'
const statusLabel = (s: string) => statusOptions.find(o => o.value === s)?.label || s || '-'

// ===== 审批 Dialog =====
const showApproveDialog = ref(false)
const approveAction = ref<'approve' | 'reject'>('approve')
const approveTarget = ref<any>(null)
const approveForm = reactive({ comment: '' })
const approving = ref(false)

const openApproveDialog = (row: any, action: 'approve' | 'reject') => {
  approveTarget.value = row
  approveAction.value = action
  approveForm.comment = ''
  showApproveDialog.value = true
}

const confirmApprove = async () => {
  if (!approveTarget.value) return
  if (approveAction.value === 'reject' && !approveForm.comment.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  approving.value = true
  try {
    await purchase.approvePlan(approveTarget.value.id, {
      decision: approveAction.value,
      remark: approveForm.comment || (approveAction.value === 'approve' ? '同意采购' : '')
    })
    ElMessage.success(approveAction.value === 'approve' ? `已批准：${approveTarget.value.code}` : `已驳回：${approveTarget.value.code}`)
    showApproveDialog.value = false
    await loadAll()
    clearSelection('pending')
  } catch { /* 拦截器已提示 */ }
  finally { approving.value = false }
}

// ===== 批量审批 =====
const handleBatchApprove = async () => {
  if (pendingSelection.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确认批量批准 ${pendingSelection.value.length} 条采购计划？`,
      '批量批准',
      { type: 'success', confirmButtonText: '全部批准' }
    )
  } catch { return }
  let ok = 0
  for (const row of [...pendingSelection.value]) {
    try {
      await purchase.approvePlan(row.id, { decision: 'approve', remark: '批量审批通过' })
      ok++
    } catch { /* 单条失败不阻塞 */ }
  }
  ElMessage.success(`已批量批准 ${ok}/${pendingSelection.value.length} 条`)
  await loadAll()
  clearSelection('pending')
}

const handleBatchReject = async () => {
  if (pendingSelection.value.length === 0) return
  let value = ''
  try {
    const res = await ElMessageBox.prompt('请输入批量驳回原因（将应用于所有选中项）', '批量驳回', {
      inputType: 'textarea',
      confirmButtonText: '全部驳回',
      cancelButtonText: '取消',
      inputPlaceholder: '请填写驳回原因',
      inputValidator: (v: string) => (v && v.trim() ? true : '请填写驳回原因')
    })
    value = res.value
  } catch { return }
  if (!value) return
  let ok = 0
  for (const row of [...pendingSelection.value]) {
    try {
      await purchase.approvePlan(row.id, { decision: 'reject', remark: value })
      ok++
    } catch { /* 单条失败不阻塞 */ }
  }
  ElMessage.success(`已批量驳回 ${ok}/${pendingSelection.value.length} 条`)
  await loadAll()
  clearSelection('pending')
}

// ===== 查看 Dialog（只读）=====
const showViewDialog = ref(false)
const viewTarget = ref<any>(null)
const handleView = (row: any) => {
  viewTarget.value = row
  showViewDialog.value = true
}

onMounted(() => { loadAll() })
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
  .header-actions { display: flex; gap: 8px; align-items: center; }
}
.filter-bar { background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); }
.content-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); }
.sub-text { font-size: 11px; color: #909399; margin-top: 2px; }
.link-text { color: #0C447C; cursor: pointer; font-weight: 500; &:hover { text-decoration: underline; } }

.batch-bar {
  display: flex; justify-content: space-between; align-items: center;
  background: #f5f9ff; border: 1px solid #d6e4ff; border-radius: 6px;
  padding: 8px 12px; margin-bottom: 12px;
  .batch-actions { display: flex; gap: 8px; }
}
</style>
