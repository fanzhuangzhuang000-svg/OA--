<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">付款单管理</span>
      <el-button type="primary" @click="handleCreate"><el-icon><Plus /></el-icon>新增付款单</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="searchForm.keyword" placeholder="搜索单号/收款方/项目" clearable style="width: 220px" @keyup.enter="loadList" />
      <el-select v-model="searchForm.status" placeholder="状态" clearable style="width: 140px" @change="loadList">
        <el-option label="待审批" value="pending" />
        <el-option label="已付款" value="paid" />
        <el-option label="已驳回" value="rejected" />
        <el-option label="已作废" value="voided" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>

    <el-row :gutter="16" class="mb-16">
      <el-col :span="6">
        <div class="mini-stat">
          <div class="mini-stat-value primary">¥{{ stats.totalAmount }}</div>
          <div class="mini-stat-label">付款总额(万元)</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="mini-stat">
          <div class="mini-stat-value success">{{ stats.paidCount }}</div>
          <div class="mini-stat-label">已付款单数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="mini-stat">
          <div class="mini-stat-value warning">{{ stats.pendingCount }}</div>
          <div class="mini-stat-label">待审批单数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="mini-stat">
          <div class="mini-stat-value danger">¥{{ stats.monthAmount }}</div>
          <div class="mini-stat-label">本月付款(万元)</div>
        </div>
      </el-col>
    </el-row>

    <div class="content-card">
      <el-table :data="list" stripe border style="width: 100%" v-loading="loading">
        <el-table-column prop="payment_no" label="付款单号" width="160" />
        <el-table-column label="收款方" min-width="160">
          <template #default="{ row }">{{ row.payee || row.supplier?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="关联项目" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.project?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="付款金额" width="120">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="method" label="付款方式" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="付款日期" width="120" />
        <el-table-column prop="handler" label="经办人" width="100">
          <template #default="{ row }">{{ row.handler || row.applicant?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'pending'" link type="success" size="small" @click="handleApprove(row)">审批</el-button>
            <el-button v-if="row.status === 'pending'" link type="danger" size="small" @click="handleVoid(row)">作废</el-button>
            <el-button link type="primary" size="small" @click="handlePrint(row)">打印</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showFormDialog" :title="editingId ? '编辑付款单' : '新增付款单'" width="1500px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="付款单号" prop="payment_no">
          <el-input v-model="formData.payment_no" placeholder="如 FK-2026-001" />
        </el-form-item>
        <el-form-item label="收款方" prop="payee">
          <el-input v-model="formData.payee" placeholder="请输入收款方" />
        </el-form-item>
        <el-form-item label="关联项目">
          <el-select v-model="formData.project_id" filterable clearable placeholder="选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款金额" prop="amount">
          <el-input-number v-model="formData.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="formData.method" style="width: 100%">
            <el-option label="银行转账" value="银行转账" />
            <el-option label="现金" value="现金" />
            <el-option label="支票" value="支票" />
            <el-option label="承兑汇票" value="承兑汇票" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款日期">
          <el-date-picker v-model="formData.payment_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="经办人">
          <el-input v-model="formData.handler" placeholder="经办人" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="付款单详情" width="1500px">
      <el-descriptions :column="2" border v-if="detailRow">
        <el-descriptions-item label="付款单号">{{ detailRow.payment_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(detailRow.status)">{{ statusLabel(detailRow.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="收款方">{{ detailRow.payee }}</el-descriptions-item>
        <el-descriptions-item label="关联项目">{{ detailRow.project?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="付款金额">
          <span class="text-danger fw-bold">¥{{ detailRow.amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="付款方式">{{ detailRow.method }}</el-descriptions-item>
        <el-descriptions-item label="付款日期">{{ detailRow.payment_date }}</el-descriptions-item>
        <el-descriptions-item label="经办人">{{ detailRow.handler }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailRow.notes || '无' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { get, post, put, del } from '@/utils/request'
import { printTable } from '@/utils/exporter'

// 付款单后端暂无独立表，使用 localStorage 做最小可用实现
const LIST_KEY = 'oa:finance:payments'

const searchForm = ref({ keyword: '', status: '' })
const list = ref<any[]>([])
const loading = ref(false)
const projects = ref<any[]>([])

const statusMap: Record<string, { label: string; type: 'success' | 'warning' | 'info' | 'danger' | 'primary' }> = {
  pending: { label: '待审批', type: 'warning' },
  paid: { label: '已付款', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' },
  voided: { label: '已作废', type: 'info' },
}
const statusLabel = (s: string) => statusMap[s]?.label || s
const statusType = (s: string): 'success' | 'warning' | 'info' | 'danger' | 'primary' => statusMap[s]?.type || 'info'

const loadList = () => {
  loading.value = true
  try {
    const raw = localStorage.getItem(LIST_KEY)
    const all = raw ? JSON.parse(raw) : []
    list.value = all.filter((it: any) => {
      const k = searchForm.value.keyword
      const matchKeyword = !k || (it.payment_no || '').includes(k) || (it.payee || '').includes(k) || (it.project?.name || '').includes(k)
      const matchStatus = !searchForm.value.status || it.status === searchForm.value.status
      return matchKeyword && matchStatus
    })
  } catch { list.value = [] } finally { loading.value = false }
}

const loadProjects = async () => {
  try { const r: any = await get('/projects', { pageSize: 500 }); projects.value = (r.data?.items || r.data?.data || r.data || r) || [] } catch (e) {}
}

onMounted(() => { loadList(); loadProjects() })

const resetSearch = () => { searchForm.value = { keyword: '', status: '' }; loadList() }

const stats = computed(() => {
  const total = list.value.filter((r: any) => r.status === 'paid').reduce((s: number, r: any) => s + Number(r.amount || 0), 0)
  const paidCount = list.value.filter((r: any) => r.status === 'paid').length
  const pendingCount = list.value.filter((r: any) => r.status === 'pending').length
  const monthStart = '2026-06-01'
  const monthAmount = list.value.filter((r: any) => r.status === 'paid' && (r.payment_date || '') >= monthStart).reduce((s: number, r: any) => s + Number(r.amount || 0), 0)
  return { totalAmount: total.toFixed(1), paidCount, pendingCount, monthAmount: monthAmount.toFixed(1) }
})

const showFormDialog = ref(false)
const editingId = ref<string | null>(null)
const formRef = ref()
const submitting = ref(false)
const formData = reactive({
  payment_no: '', payee: '', project_id: null as number | null, amount: 0,
  method: '银行转账', payment_date: '', handler: '', notes: '',
})
const formRules = {
  payment_no: [{ required: true, message: '请输入单号', trigger: 'blur' }],
  payee: [{ required: true, message: '请输入收款方', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
}

const handleCreate = () => {
  editingId.value = null
  Object.assign(formData, { payment_no: `FK-${new Date().getFullYear()}-${String(Math.floor(Math.random()*999)+1).padStart(3,'0')}`, payee: '', project_id: null, amount: 0, method: '银行转账', payment_date: new Date().toISOString().slice(0,10), handler: '', notes: '' })
  showFormDialog.value = true
}
const handleSubmit = async () => {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    const project = projects.value.find((p: any) => p.id === formData.project_id)
    const all = JSON.parse(localStorage.getItem(LIST_KEY) || '[]')
    const payload = { ...formData, id: editingId.value || `PMT-${Date.now()}`, project, status: editingId.value ? (all.find((x:any) => x.id === editingId.value)?.status || 'pending') : 'pending' }
    if (editingId.value) {
      const idx = all.findIndex((x: any) => x.id === editingId.value)
      if (idx >= 0) all[idx] = payload
    } else {
      all.unshift(payload)
    }
    localStorage.setItem(LIST_KEY, JSON.stringify(all))
    ElMessage.success(editingId.value ? '已更新' : '付款单已创建')
    showFormDialog.value = false
    loadList()
  } catch (e: any) { ElMessage.error(e?.message || '保存失败') } finally { submitting.value = false }
}

const showDetailDialog = ref(false)
const detailRow = ref<any>(null)
const handleView = (row: any) => { detailRow.value = row; showDetailDialog.value = true }

const handleApprove = async (row: any) => {
  try { await ElMessageBox.confirm(`确认向 ${row.payee} 支付 ¥${row.amount}？`, '付款审批', { type: 'success', confirmButtonText: '确认付款' }) } catch { return }
  const all = JSON.parse(localStorage.getItem(LIST_KEY) || '[]')
  const idx = all.findIndex((x: any) => x.id === row.id)
  if (idx >= 0) { all[idx].status = 'paid'; localStorage.setItem(LIST_KEY, JSON.stringify(all)); loadList(); ElMessage.success('付款已确认') }
}
const handleVoid = async (row: any) => {
  try { await ElMessageBox.confirm(`确认作废付款单 ${row.payment_no}？`, '作废确认', { type: 'warning' }) } catch { return }
  const all = JSON.parse(localStorage.getItem(LIST_KEY) || '[]')
  const idx = all.findIndex((x: any) => x.id === row.id)
  if (idx >= 0) { all[idx].status = 'voided'; localStorage.setItem(LIST_KEY, JSON.stringify(all)); loadList(); ElMessage.success('已作废') }
}
const handlePrint = (row: any) => {
  const headers = ['字段', '内容']
  const rows = [
    ['付款单号', row.payment_no || '-'],
    ['付款类型', ({ supplier: '供应商付款', refund: '退款', other: '其他' }[row.type as string] || row.type || '-')],
    ['关联项目', row.project?.name || row.project_name || '-'],
    ['收款方', row.supplier?.name || row.supplier_name || row.payee || '-'],
    ['付款金额', '¥' + Number(row.amount || 0).toFixed(2)],
    ['付款方式', ({ bank: '银行转账', cash: '现金', alipay: '支付宝', wechat: '微信', check: '支票' }[row.method as string] || row.method || '-')],
    ['付款日期', row.payment_date?.slice(0, 10) || '-'],
    ['凭证号', row.voucher_no || '-'],
    ['付款状态', ({ pending: '待付', paid: '已付', voided: '已作废' }[row.status as string] || row.status || '-')],
    ['经手人', row.operator || '-'],
    ['备注', row.remark || row.notes || '-'],
  ]
  printTable(`付款单 - ${row.payment_no || ''}`, headers, rows, { orientation: 'portrait' })
}
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; .page-title { font-size: 20px; color: #0C447C; font-weight: 600; } }
.filter-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding: 16px; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); flex-wrap: wrap; }
.content-card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.mb-16 { margin-bottom: 16px; }
.mini-stat { background: #fff; border-radius: 8px; padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.mini-stat-value { font-size: 22px; font-weight: 700; &.primary { color: #0C447C; } &.success { color: #1D9E75; } &.warning { color: #BA7517; } &.danger { color: #A32D2D; } }
.mini-stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.text-danger { color: #A32D2D; }
.fw-bold { font-weight: 700; }
</style>
