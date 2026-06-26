<template>
  <div class="page-container">
    <!-- 页头：标题 + 待我审批徽标 -->
    <div class="page-header">
      <div class="header-left">
        <h2>财务审批</h2>
        <el-tag v-if="pendingCount > 0" type="danger" effect="dark" round class="ml-12">
          待我审批 {{ pendingCount }}
        </el-tag>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="loadList">刷新</el-button>
        <el-button type="primary" :icon="Search" @click="showSearch = !showSearch">筛选</el-button>
      </div>
    </div>

    <!-- 筛选区 -->
    <transition name="el-fade-in">
      <div v-if="showSearch" class="filter-bar">
        <el-input v-model="filter.keyword" placeholder="单号/标题" clearable style="width: 200px" @keyup.enter="handleSearch" />
        <el-select v-model="filter.subType" placeholder="审批子类" clearable style="width: 160px">
          <el-option v-for="t in subTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-select v-model="filter.priority" placeholder="优先级" clearable style="width: 120px">
          <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-date-picker v-model="filter.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width: 260px" />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>
    </transition>

    <!-- 4 张统计卡片 -->
    <div class="stats-row">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div>
            <div class="stat-label">待我审批</div>
            <div class="stat-value primary">{{ pendingCount }}</div>
          </div>
          <el-icon :size="32" class="stat-icon primary"><Bell /></el-icon>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div>
            <div class="stat-label">我已审批</div>
            <div class="stat-value success">{{ approvedCount }}</div>
          </div>
          <el-icon :size="32" class="stat-icon success"><Check /></el-icon>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div>
            <div class="stat-label">本月涉及金额</div>
            <div class="stat-value warning">¥ {{ formatMoney(totalAmount) }}</div>
          </div>
          <el-icon :size="32" class="stat-icon warning"><Money /></el-icon>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div>
            <div class="stat-label">本月已支付</div>
            <div class="stat-value info">¥ {{ formatMoney(paidAmount) }}</div>
          </div>
          <el-icon :size="32" class="stat-icon info"><CreditCard /></el-icon>
        </div>
      </el-card>
    </div>

    <div class="content-card">
      <el-tabs v-model="activeTab" class="approval-tabs">
        <el-tab-pane name="pending">
          <template #label>
            <el-badge :value="pendingCount" :hidden="pendingCount === 0" type="danger">
              待我审批
            </el-badge>
          </template>
        </el-tab-pane>
        <el-tab-pane name="approved">
          <template #label><span>我已审批</span></template>
        </el-tab-pane>
        <el-tab-pane name="rejected">
          <template #label><span>我已驳回</span></template>
        </el-tab-pane>
        <el-tab-pane name="initiated">
          <template #label><span>我发起的</span></template>
        </el-tab-pane>
        <el-tab-pane name="cc">
          <template #label><span>抄送我的</span></template>
        </el-tab-pane>
      </el-tabs>

      <el-table :data="filteredList" stripe border style="width: 100%" v-loading="loading" @row-dblclick="handleDetail">
        <el-table-column type="index" width="50" align="center" />
        <el-table-column prop="code" label="单号" width="160" fixed>
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="handleDetail(row)">{{ row.code }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="审批子类" width="120">
          <template #default="{ row }">
            <el-tag :type="subTypeTagType(row.subType)" effect="plain">
              <el-icon class="mr-4"><component :is="subTypeIcon(row.subType)" /></el-icon>
              {{ subTypeLabel(row.subType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="发起人" width="100">
          <template #default="{ row }">{{ row.initiator?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="140" align="right">
          <template #default="{ row }">
            <span class="amount">¥ {{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="账户" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.bankAccount" class="bank-info">
              <el-icon><CreditCard /></el-icon>
              {{ row.bankAccount }}
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="发起时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityTagType(row.priority)" effect="dark" size="small">
              {{ priorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="dark">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleDetail(row)">详情</el-button>
            <template v-if="row.status === 'pending' && canApprove(row)">
              <el-button link type="success" size="small" @click="handleApprove(row)">通过</el-button>
              <el-button link type="danger" size="small" @click="handleReject(row)">驳回</el-button>
            </template>
            <el-button v-if="row.status === 'pending' && canApprove(row)" link type="warning" size="small" @click="handleTransfer(row)">转交</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && filteredList.length === 0" description="暂无数据" :image-size="100" />
    </div>

    <!-- 详情 Dialog -->
    <el-dialog v-model="showDetailDialog" :title="`财务审批详情 — ${currentItem?.code || ''}`" width="1500px" destroy-on-close>
      <div v-if="currentItem">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="单号">{{ currentItem.code }}</el-descriptions-item>
          <el-descriptions-item label="子类">
            <el-tag :type="subTypeTagType(currentItem.subType)" effect="plain">
              {{ subTypeLabel(currentItem.subType) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="priorityTagType(currentItem.priority)" effect="dark">
              {{ priorityLabel(currentItem.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题" :span="3">{{ currentItem.title }}</el-descriptions-item>
          <el-descriptions-item label="发起人">{{ currentItem.initiator?.name }}</el-descriptions-item>
          <el-descriptions-item label="金额"><span class="amount">¥ {{ formatMoney(currentItem.amount) }}</span></el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTagType(currentItem.status)" effect="dark">
              {{ statusLabel(currentItem.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h4 class="section-title">💰 财务详情</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item v-for="(v, k) in currentItem.detail" :key="k" :label="k">{{ v }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="section-title">🔁 审批流程</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(n, i) in currentItem.flow"
            :key="i"
            :timestamp="formatDateTime(n.time)"
            :type="flowNodeType(n.action)"
            :hollow="i !== currentItem.flow.length - 1"
            size="large"
          >
            <strong>{{ n.operator }}</strong>
            <el-tag :type="flowNodeType(n.action)" effect="plain" size="small" class="ml-8">{{ flowActionLabel(n.action) }}</el-tag>
            <div v-if="n.comment" class="flow-comment">💬 {{ n.comment }}</div>
          </el-timeline-item>
        </el-timeline>

        <div v-if="currentItem.status === 'pending' && canApprove(currentItem)" class="approval-input">
          <h4 class="section-title">✍️ 我的审批</h4>
          <el-input v-model="approvalComment" type="textarea" :rows="3" placeholder="请输入审批意见（驳回必填）" maxlength="500" show-word-limit />
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <template v-if="currentItem?.status === 'pending' && canApprove(currentItem)">
          <el-button type="danger" @click="handleReject(currentItem)">驳回</el-button>
          <el-button type="warning" @click="handleTransfer(currentItem)">转交</el-button>
          <el-button type="success" @click="handleApprove(currentItem)">通过</el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, Bell, Check, Money, CreditCard } from '@element-plus/icons-vue'
import { get, post } from '@/utils/request'

const loading = ref(false)
const showSearch = ref(false)
const showDetailDialog = ref(false)
const activeTab = ref('pending')
const list = ref<any[]>([])
const currentItem = ref<any>(null)
const approvalComment = ref('')

const filter = reactive({ keyword: '', subType: '', priority: '', dateRange: [] as any[] })

// 财务审批子类
const subTypeOptions = [
  { value: 'expense', label: '报销' },
  { value: 'payment', label: '付款单' },
  { value: 'receivable', label: '应收确认' },
  { value: 'payable', label: '应付确认' },
  { value: 'purchase', label: '采购付款' },
  { value: 'commission', label: '居间费' },
  { value: 'salary', label: '薪资调整' },
  { value: 'reimburse', label: '差旅报销' },
  { value: 'loan', label: '借款' },
  { value: 'other', label: '其他' }
]
const priorityOptions = [
  { value: 'urgent', label: '紧急' }, { value: 'high', label: '高' },
  { value: 'normal', label: '普通' }, { value: 'low', label: '低' }
]
const subTypeLabel = (t: string) => subTypeOptions.find(x => x.value === t)?.label || t
const priorityLabel = (p: string) => priorityOptions.find(x => x.value === p)?.label || p
const subTypeTagType = (t: string): any => ({
  expense: 'danger', payment: 'danger', receivable: 'warning', payable: 'warning',
  purchase: 'success', commission: 'success', salary: 'info',
  reimburse: 'danger', loan: 'warning', other: 'info'
}[t] || 'info')
const subTypeIcon = (t: string) => ({
  expense: 'Money', payment: 'CreditCard', receivable: 'Wallet', payable: 'Wallet',
  purchase: 'ShoppingCart', commission: 'Coin', salary: 'UserFilled',
  reimburse: 'Ticket', loan: 'CreditCard', other: 'MoreFilled'
}[t] || 'MoreFilled')
const priorityTagType = (p: string): any => ({ urgent: 'danger', high: 'warning', normal: 'primary', low: 'info' }[p] || 'info')
const statusLabel = (s: string) => ({ pending: '待审批', approved: '已通过', rejected: '已驳回', transferred: '已转交', cancelled: '已撤销' }[s] || s)
const statusTagType = (s: string): any => ({ pending: 'warning', approved: 'success', rejected: 'danger', transferred: 'info', cancelled: 'info' }[s] || 'info')
const flowNodeType = (a: string): any => ({ submit: 'primary', approve: 'success', reject: 'danger', transfer: 'warning', comment: 'info' }[a] || 'info')
const flowActionLabel = (a: string) => ({ submit: '发起', approve: '通过', reject: '驳回', transfer: '转交', comment: '补充' }[a] || a)

const pendingCount = computed(() => list.value.filter(i => i.status === 'pending' && i.current_approver === 'me').length)
const approvedCount = computed(() => list.value.filter(i => i.status === 'approved' && i.approver === 'me').length)
const totalAmount = computed(() => list.value.filter(i => i.status === 'pending' || i.status === 'approved').reduce((s, i) => s + (parseFloat(i.amount) || 0), 0))
const paidAmount = computed(() => list.value.filter(i => i.status === 'approved').reduce((s, i) => s + (parseFloat(i.amount) || 0), 0))

const loadList = async () => {
  loading.value = true
  try {
    const res: any = await get('/approvals/finance', { per_page: 200 })
    const data = Array.isArray(res) ? res : (res.data?.data || res.data || [])
    list.value = Array.isArray(res) ? res : (res.data?.data || res.data || [])
  } catch { list.value = [] }
  finally { loading.value = false }
}

const filteredList = computed(() => list.value.filter(item => {
  if (activeTab.value === 'pending' && (item.status !== 'pending' || item.current_approver !== 'me')) return false
  if (activeTab.value === 'approved' && (item.status !== 'approved' || item.approver !== 'me')) return false
  if (activeTab.value === 'rejected' && (item.status !== 'rejected' || item.approver !== 'me')) return false
  if (activeTab.value === 'initiated' && item.initiator?.id !== 'me') return false
  if (activeTab.value === 'cc' && !item.cc?.includes('me')) return false
  if (filter.keyword && !item.code.includes(filter.keyword) && !item.title.includes(filter.keyword)) return false
  if (filter.subType && item.subType !== filter.subType) return false
  if (filter.priority && item.priority !== filter.priority) return false
  return true
}))

const canApprove = (row: any) => row.current_approver === 'me'
const handleDetail = (row: any) => { currentItem.value = row; approvalComment.value = ''; showDetailDialog.value = true }
const handleApprove = async (row: any) => {
  try { await ElMessageBox.confirm('确定审批通过吗？', '审批确认', { type: 'success' }); await post(`/approvals/finance/${row.id}/approve`, { comment: approvalComment.value || '同意' }); ElMessage.success('已通过'); showDetailDialog.value = false; loadList() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e?.message || '操作失败') }
}
const handleReject = async (row: any) => {
  if (!approvalComment.value.trim()) { ElMessage.warning('请填写驳回意见'); return }
  try { await ElMessageBox.confirm('确定驳回吗？', '驳回确认', { type: 'warning' }); await post(`/approvals/finance/${row.id}/reject`, { comment: approvalComment.value }); ElMessage.success('已驳回'); showDetailDialog.value = false; loadList() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e?.message || '操作失败') }
}
const handleTransfer = async (row: any) => {
  try { const { value: target } = await ElMessageBox.prompt('请输入转交给谁', '转交审批', { inputPlaceholder: '用户名' }); if (!target) return; await post(`/approvals/finance/${row.id}/forward`, { target }); ElMessage.success(`已转交 ${target}`); showDetailDialog.value = false; loadList() } catch (e: any) { if (e !== 'cancel') ElMessage.error(e?.message || '操作失败') }
}
const handleSearch = () => {}
const resetFilter = () => { filter.keyword = ''; filter.subType = ''; filter.priority = ''; filter.dateRange = [] }
const formatDateTime = (d: string) => d ? new Date(d).toLocaleString('zh-CN', { hour12: false }).slice(0, 16) : '-'
const formatMoney = (v: any) => { const n = parseFloat(v); return isNaN(n) ? '0.00' : n.toFixed(2) }

onMounted(loadList)
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; .header-left { display: flex; align-items: center; gap: 12px; h2 { font-size: 20px; color: #0C447C; margin: 0; } } }
.filter-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding: 16px; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-card { border-radius: 8px; .stat-content { display: flex; align-items: center; justify-content: space-between; } .stat-label { font-size: 14px; color: #606266; margin-bottom: 8px; } .stat-value { font-size: 28px; font-weight: 600; line-height: 1.2; &.primary { color: #BA7517; } &.success { color: #1D9E75; } &.warning { color: #A32D2D; } &.info { color: #534AB7; } } .stat-icon { opacity: 0.2; } }
.content-card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.section-title { margin: 20px 0 12px; font-size: 15px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 8px; }
.flow-comment { margin-top: 4px; color: #606266; font-size: 13px; }
.amount { color: #A32D2D; font-weight: 600; }
.bank-info { display: inline-flex; align-items: center; gap: 4px; color: #534AB7; font-family: monospace; font-size: 12px; }
.text-muted { color: #c0c4cc; }
.ml-8 { margin-left: 8px; }
.ml-12 { margin-left: 12px; }
.mr-4 { margin-right: 4px; }
</style>
