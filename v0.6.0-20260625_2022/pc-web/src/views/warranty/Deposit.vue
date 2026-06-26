<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">质保金管理</span>
      <div class="header-actions">
        <ScopeToggle @change="loadList" />
        <el-button :icon="Refresh" plain @click="handleReset">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建质保金</el-button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-row">
      <el-card v-for="kpi in kpis" :key="kpi.label" shadow="hover" :body-style="{ padding: '14px 18px' }" class="kpi-card">
        <div class="kpi-label">{{ kpi.label }}</div>
        <div class="kpi-value" :style="{ color: kpi.color }">{{ kpi.value }}</div>
      </el-card>
    </div>

    <!-- 筛选区 -->
    <div class="filter-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目">
          <el-input v-model="searchForm.project_id" placeholder="项目ID" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="质保期">
          <el-input v-model="searchForm.warranty_id" placeholder="质保期ID" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="content-card">
      <el-table
        :data="pagedList"
        v-loading="loading"
        stripe
        border
        :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
      >
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column label="项目" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.project?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="客户" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ row.customer?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="合同金额" width="120" align="right">
          <template #default="{ row }">¥ {{ formatAmount(row.contract_amount) }}</template>
        </el-table-column>
        <el-table-column label="质保金" width="120" align="right">
          <template #default="{ row }"><strong>¥ {{ formatAmount(row.deposit_amount) }}</strong></template>
        </el-table-column>
        <el-table-column label="已释放" width="110" align="right">
          <template #default="{ row }">¥ {{ formatAmount(row.released_amount) }}</template>
        </el-table-column>
        <el-table-column label="已没收" width="110" align="right">
          <template #default="{ row }">¥ {{ formatAmount(row.forfeited_amount) }}</template>
        </el-table-column>
        <el-table-column label="余额" width="120" align="right">
          <template #default="{ row }">
            <strong :style="{ color: balanceColor(row) }">¥ {{ formatAmount(balance(row)) }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="plain" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="留置日" width="110" align="center">
          <template #default="{ row }">{{ row.hold_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="goDetail(row)">详情</el-button>
            <el-button v-if="['held', 'partial_released'].includes(row.status)" link type="success" :icon="Refresh" @click="showReleaseDialog(row, 'partial')">部分释放</el-button>
            <el-button v-if="['held', 'partial_released'].includes(row.status)" link type="warning" :icon="Check" @click="showReleaseDialog(row, 'full')">全部释放</el-button>
            <el-button v-if="['held', 'partial_released'].includes(row.status)" link type="danger" :icon="CircleClose" @click="showForfeitDialog(row)">没收</el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 释放 dialog -->
    <el-dialog v-model="releaseDialog.visible" :title="releaseDialog.title" width="500px">
      <el-form :model="releaseDialog.form" label-width="100px">
        <el-form-item v-if="releaseDialog.type === 'partial'" label="释放金额" required>
          <el-input-number v-model="releaseDialog.form.release_amount" :min="0.01" :max="releaseDialog.balance" :precision="2" />
          <span style="margin-left: 8px; color: #909399">余额: ¥ {{ formatAmount(releaseDialog.balance) }}</span>
        </el-form-item>
        <el-form-item label="释放日期" required>
          <el-date-picker v-model="releaseDialog.form.release_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="原因" required>
          <el-input v-model="releaseDialog.form.release_reason" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="收款人">
          <el-input v-model="releaseDialog.form.beneficiary_name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="releaseDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitRelease">确认</el-button>
      </template>
    </el-dialog>

    <!-- 没收 dialog -->
    <el-dialog v-model="forfeitDialog.visible" title="没收质保金" width="500px">
      <el-form :model="forfeitDialog.form" label-width="100px">
        <el-form-item label="没收金额" required>
          <el-input-number v-model="forfeitDialog.form.forfeit_amount" :min="0.01" :max="forfeitDialog.balance" :precision="2" />
          <span style="margin-left: 8px; color: #909399">余额: ¥ {{ formatAmount(forfeitDialog.balance) }}</span>
        </el-form-item>
        <el-form-item label="没收日期" required>
          <el-date-picker v-model="forfeitDialog.form.forfeit_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="没收原因" required>
          <el-input v-model="forfeitDialog.form.forfeit_reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forfeitDialog.visible = false">取消</el-button>
        <el-button type="danger" @click="submitForfeit">确认没收</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Check, CircleClose } from '@element-plus/icons-vue'
import { warrantyDepositApi } from '@/api/warranty'
import ScopeToggle from '@/components/ScopeToggle.vue'

const router = useRouter()

const statusOptions = [
  { value: 'held',             label: '留置中' },
  { value: 'partial_released', label: '部分释放' },
  { value: 'fully_released',   label: '全部释放' },
  { value: 'forfeited',        label: '已没收' },
]

const statusLabel = (s: string) => statusOptions.find(x => x.value === s)?.label || s || '-'
const statusTagType = (s: string) => ({ held: 'info', partial_released: 'warning', fully_released: 'success', forfeited: 'danger' } as any)[s] || 'info'

const formatAmount = (v: any) => {
  const n = parseFloat(v) || 0
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const balance = (row: any) => {
  return (parseFloat(row.deposit_amount) || 0) - (parseFloat(row.released_amount) || 0) - (parseFloat(row.forfeited_amount) || 0)
}
const balanceColor = (row: any) => {
  const b = balance(row)
  if (b <= 0) return '#909399'
  return '#67C23A'
}

const loading = ref(false)
const list = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)

const searchForm = reactive({ status: '', project_id: '', warranty_id: '' })

const kpis = computed(() => {
  const total = list.value.length
  const held = list.value.filter(x => x.status === 'held').length
  const totalAmount = list.value.reduce((s, x) => s + (parseFloat(x.deposit_amount) || 0), 0)
  const released = list.value.reduce((s, x) => s + (parseFloat(x.released_amount) || 0), 0)
  return [
    { label: '质保金笔数', value: total, color: '#409EFF' },
    { label: '留置中',     value: held,  color: '#909399' },
    { label: '总额 (¥)',   value: totalAmount.toLocaleString('zh-CN', { maximumFractionDigits: 0 }), color: '#67C23A' },
    { label: '已释放 (¥)', value: released.toLocaleString('zh-CN', { maximumFractionDigits: 0 }), color: '#E6A23C' },
  ]
})

const filteredList = computed(() => {
  return list.value.filter(x => {
    if (searchForm.status && x.status !== searchForm.status) return false
    if (searchForm.project_id && String(x.project_id) !== String(searchForm.project_id)) return false
    if (searchForm.warranty_id && String(x.warranty_id) !== String(searchForm.warranty_id)) return false
    return true
  })
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

async function loadList() {
  loading.value = true
  try {
    const res: any = await warrantyDepositApi.list({ per_page: 200 })
    const d = res.data || res
    const items = d.data || d.items || d
    list.value = Array.isArray(items) ? items : []
  } catch (e: any) {
    ElMessage.error('加载质保金失败: ' + (e.message || 'unknown'))
    list.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() { page.value = 1 }
function handleReset() {
  Object.assign(searchForm, { status: '', project_id: '', warranty_id: '' })
  page.value = 1
  loadList()
}

function handleAdd() {
  router.push({ path: '/project/warranty/deposit' })
}

function goDetail(row: any) {
  router.push(`/project/warranty/deposit/detail/${row.id}`)
}

const releaseDialog = reactive({
  visible: false, title: '', type: 'partial' as 'partial' | 'full',
  target: null as any, balance: 0,
  form: { release_amount: 0, release_date: new Date().toISOString().slice(0, 10), release_reason: '', beneficiary_name: '' },
})

function showReleaseDialog(row: any, type: 'partial' | 'full') {
  releaseDialog.type = type
  releaseDialog.title = type === 'partial' ? '部分释放' : '全部释放'
  releaseDialog.target = row
  releaseDialog.balance = balance(row)
  releaseDialog.form = {
    release_amount: type === 'full' ? releaseDialog.balance : 0,
    release_date: new Date().toISOString().slice(0, 10),
    release_reason: '',
    beneficiary_name: '',
  }
  releaseDialog.visible = true
}

async function submitRelease() {
  if (!releaseDialog.form.release_reason) {
    ElMessage.warning('请填写原因')
    return
  }
  try {
    if (releaseDialog.type === 'partial') {
      await warrantyDepositApi.partialRelease(releaseDialog.target.id, releaseDialog.form)
    } else {
      await warrantyDepositApi.fullRelease(releaseDialog.target.id, releaseDialog.form)
    }
    ElMessage.success(releaseDialog.type === 'partial' ? '部分释放成功' : '全部释放成功')
    releaseDialog.visible = false
    loadList()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.message || 'unknown'))
  }
}

const forfeitDialog = reactive({
  visible: false, target: null as any, balance: 0,
  form: { forfeit_amount: 0, forfeit_date: new Date().toISOString().slice(0, 10), forfeit_reason: '' },
})

function showForfeitDialog(row: any) {
  forfeitDialog.target = row
  forfeitDialog.balance = balance(row)
  forfeitDialog.form = {
    forfeit_amount: forfeitDialog.balance,
    forfeit_date: new Date().toISOString().slice(0, 10),
    forfeit_reason: '',
  }
  forfeitDialog.visible = true
}

async function submitForfeit() {
  if (!forfeitDialog.form.forfeit_reason) {
    ElMessage.warning('请填写没收原因')
    return
  }
  try {
    await warrantyDepositApi.forfeit(forfeitDialog.target.id, forfeitDialog.form)
    ElMessage.success('已没收')
    forfeitDialog.visible = false
    loadList()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.message || 'unknown'))
  }
}

onMounted(loadList)
</script>
