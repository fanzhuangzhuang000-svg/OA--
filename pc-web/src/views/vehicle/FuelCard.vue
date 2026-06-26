<template>
  <div class="page-container">
    <div class="page-header">
      <h2>油卡管理</h2>
      <div class="header-stats">
        <el-tag type="success" effect="plain">油卡 {{ stats.totalCards }} 张</el-tag>
        <el-tag type="warning" effect="plain">已绑定 {{ stats.boundCards }} 张</el-tag>
        <el-tag type="primary" effect="plain">总余额 ¥{{ formatMoney(stats.totalBalance) }}</el-tag>
        <el-tag type="info" effect="plain">本月充值 ¥{{ formatMoney(stats.monthRecharge) }} ({{ stats.monthCount }} 次)</el-tag>
      </div>
    </div>

    <div class="filter-bar">
      <el-select v-model="searchForm.vehicle_id" placeholder="选择车辆" clearable filterable style="width: 200px">
        <el-option v-for="v in vehicles" :key="v.id" :label="`${v.plate_no} (${v.brand})`" :value="v.id" />
      </el-select>
      <el-select v-model="searchForm.status" placeholder="卡片状态" clearable style="width: 130px">
        <el-option label="在用" value="active" />
        <el-option label="挂失" value="lost" />
        <el-option label="过期" value="expired" />
      </el-select>
      <el-input v-model="searchForm.keyword" placeholder="搜索卡号/发卡机构" clearable style="width: 240px" @keyup.enter="handleSearch" />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
      <el-button type="primary" plain @click="openCardDialog()">新增油卡</el-button>
      <el-button type="warning" plain @click="openRechargeDialog()">记录充值</el-button>
    </div>

    <div class="content-card">
      <el-table :data="cardList" stripe border v-loading="loading">
        <el-table-column prop="id" label="#" width="60" />
        <el-table-column prop="card_no" label="卡号" width="160" />
        <el-table-column prop="card_name" label="发卡机构" width="140" />
        <el-table-column label="绑定车辆" min-width="180">
          <template #default="{ row }">
            <span v-if="row.vehicle" class="plate">{{ row.vehicle.plate_no }}</span>
            <span v-else class="muted">未绑定</span>
            <span v-if="row.vehicle" class="vehicle-meta">{{ row.vehicle.brand }} {{ row.vehicle.model }}</span>
          </template>
        </el-table-column>
        <el-table-column label="当前余额" width="130" align="right">
          <template #default="{ row }">
            <span class="balance">¥ {{ formatMoney(row.balance) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="发卡日期" width="120">
          <template #default="{ row }">{{ formatDate(row.issue_date) }}</template>
        </el-table-column>
        <el-table-column label="到期日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'date-warn': isExpiringSoon(row.expire_date) }">{{ formatDate(row.expire_date) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="cardStatusType(row.status)" effect="dark">{{ cardStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openCardDialog(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDeleteCard(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="cardPagination.page"
        v-model:page-size="cardPagination.per_page"
        :total="cardPagination.total"
        :page-sizes="[10, 15, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadCardList"
        @current-change="loadCardList"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </div>

    <el-divider content-position="left">充值记录</el-divider>

    <div class="content-card">
      <div class="filter-bar">
        <el-select v-model="rechargeForm.card_id" placeholder="选择油卡" clearable filterable style="width: 200px" @change="loadRecharges">
          <el-option v-for="c in cardList" :key="c.id" :label="`${c.card_no} (${c.card_name || '-'})`" :value="c.id" />
        </el-select>
        <el-input v-model="rechargeForm.keyword" placeholder="搜索凭证号/经办人" clearable style="width: 220px" @keyup.enter="loadRecharges" />
        <el-button type="primary" @click="loadRecharges">搜索</el-button>
        <el-button @click="resetRecharge">重置</el-button>
      </div>

      <el-table :data="rechargeList" stripe border v-loading="rechargeLoading">
        <el-table-column prop="id" label="#" width="60" />
        <el-table-column label="充值日期" width="120">
          <template #default="{ row }">{{ formatDate(row.recharge_date) }}</template>
        </el-table-column>
        <el-table-column label="油卡" min-width="180">
          <template #default="{ row }">
            <span class="card-no">{{ row.card?.card_no }}</span>
            <span class="muted">{{ row.card?.card_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="充值金额" width="130" align="right">
          <template #default="{ row }">
            <span class="amount-add">+¥ {{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="120" />
        <el-table-column prop="operator" label="经办人" width="100" />
        <el-table-column prop="voucher_no" label="凭证号" width="160" />
        <el-table-column prop="notes" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="handleDeleteRecharge(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="rechargePagination.page"
        v-model:page-size="rechargePagination.per_page"
        :total="rechargePagination.total"
        :page-sizes="[10, 15, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadRecharges"
        @current-change="loadRecharges"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </div>

    <!-- 新增/编辑油卡 -->
    <CardFormDialog
      v-model:visible="cardDialogVisible"
      :editing-id="editingCardId"
      :form="cardForm"
      :rules="cardRules"
      :vehicles="vehicles"
      :submitting="submitting"
      @submit="handleCardSubmit"
    />

    <!-- 充值对话框 -->
    <RechargeDialog
      v-model:visible="rechargeDialogVisible"
      :form="rechargePayload"
      :rules="rechargeRules"
      :card-list="cardList"
      :pay-methods="payMethods"
      :submitting="submitting"
      :format-money="formatMoney"
      @submit="handleRechargeSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getFuelCardList, createFuelCard, updateFuelCard, deleteFuelCard,
  getFuelCardRecharges, createFuelCardRecharge, deleteFuelCardRecharge,
  getFuelCardStats, getVehicleList
} from '@/api/modules'
import CardFormDialog from './components/fuel-card/CardFormDialog.vue'
import RechargeDialog from './components/fuel-card/RechargeDialog.vue'

const payMethods = ['银行转账', '微信', '支付宝', '现金', '其他']

const loading = ref(false)
const rechargeLoading = ref(false)
const submitting = ref(false)
const cardList = ref<any[]>([])
const rechargeList = ref<any[]>([])
const vehicles = ref<any[]>([])
const stats = reactive({ totalCards: 0, activeCards: 0, boundCards: 0, totalBalance: '0', monthRecharge: '0', monthCount: 0 })
const cardPagination = reactive({ page: 1, per_page: 15, total: 0 })
const rechargePagination = reactive({ page: 1, per_page: 15, total: 0 })
const searchForm = reactive({ vehicle_id: null as number | null, status: '', keyword: '' })
const rechargeForm = reactive({ card_id: null as number | null, keyword: '' })

const cardDialogVisible = ref(false)
const editingCardId = ref<number | null>(null)
const cardFormRef = ref()
const cardForm = reactive({
  card_no: '', card_name: '', vehicle_id: null as number | null,
  balance: 0, issue_date: null as string | null, expire_date: null as string | null, notes: ''
})
const cardRules = {
  card_no: [{ required: true, message: '请输入卡号', trigger: 'blur' }],
}

const rechargeDialogVisible = ref(false)
const rechargeFormRef = ref()
const rechargePayload = reactive({
  card_id: null as number | null,
  amount: 1000,
  recharge_date: new Date().toISOString().slice(0, 10),
  payment_method: '银行转账',
  operator: '',
  voucher_no: '',
  notes: '',
})
const rechargeRules = {
  card_id: [{ required: true, message: '请选择油卡', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  recharge_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

function formatMoney(v: any) {
  const n = parseFloat(v)
  return isNaN(n) ? '0.00' : n.toFixed(2)
}
function formatDate(d: string) { return d ? String(d).slice(0, 10) : '-' }
function isExpiringSoon(endDate: string) {
  if (!endDate) return false
  const end = new Date(endDate).getTime()
  return end >= Date.now() && end - Date.now() < 30 * 24 * 60 * 60 * 1000
}
function cardStatusType(s: string) {
  if (s === 'active') return 'success'
  if (s === 'lost') return 'danger'
  return 'info'
}
function cardStatusLabel(s: string) {
  if (s === 'active') return '在用'
  if (s === 'lost') return '挂失'
  return '过期'
}

async function loadCardList() {
  loading.value = true
  try {
    const res: any = await getFuelCardList({
      page: cardPagination.page,
      per_page: cardPagination.per_page,
      vehicle_id: searchForm.vehicle_id || undefined,
      status: searchForm.status || undefined,
      keyword: searchForm.keyword || undefined,
    })
    cardList.value = res?.data || []
    cardPagination.total = res?.total || 0
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function loadRecharges() {
  rechargeLoading.value = true
  try {
    const res: any = await getFuelCardRecharges({
      page: rechargePagination.page,
      per_page: rechargePagination.per_page,
      card_id: rechargeForm.card_id || undefined,
      keyword: rechargeForm.keyword || undefined,
    })
    rechargeList.value = res?.data || []
    rechargePagination.total = res?.total || 0
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '加载失败')
  } finally {
    rechargeLoading.value = false
  }
}

async function loadStats() {
  try {
    const res: any = await getFuelCardStats()
    if (res) Object.assign(stats, res)
  } catch { /* 静默 */ }
}

async function loadVehicles() {
  try {
    const res: any = await getVehicleList()
    vehicles.value = Array.isArray(res) ? res : (res?.data || [])
  } catch { /* 静默 */ }
}

function handleSearch() { cardPagination.page = 1; loadCardList() }
function resetSearch() {
  searchForm.vehicle_id = null; searchForm.status = ''; searchForm.keyword = ''
  cardPagination.page = 1; loadCardList()
}
function resetRecharge() {
  rechargeForm.card_id = null; rechargeForm.keyword = ''
  rechargePagination.page = 1; loadRecharges()
}

function openCardDialog(row?: any) {
  editingCardId.value = null
  cardForm.card_no = ''; cardForm.card_name = ''; cardForm.vehicle_id = null
  cardForm.balance = 0; cardForm.issue_date = null; cardForm.expire_date = null; cardForm.notes = ''
  if (row) {
    editingCardId.value = row.id
    cardForm.card_no = row.card_no
    cardForm.card_name = row.card_name || ''
    cardForm.vehicle_id = row.vehicle_id || null
    cardForm.balance = parseFloat(row.balance) || 0
    cardForm.issue_date = row.issue_date ? formatDate(row.issue_date) : null
    cardForm.expire_date = row.expire_date ? formatDate(row.expire_date) : null
    cardForm.notes = row.notes || ''
  }
  cardDialogVisible.value = true
}

async function handleCardSubmit() {
  if (!cardFormRef.value) return
  try { await cardFormRef.value.validate() } catch { return }
  submitting.value = true
  const payload: any = {
    card_no: cardForm.card_no,
    card_name: cardForm.card_name || null,
    vehicle_id: cardForm.vehicle_id || null,
    balance: cardForm.balance,
    issue_date: cardForm.issue_date || null,
    expire_date: cardForm.expire_date || null,
    notes: cardForm.notes || null,
  }
  try {
    if (editingCardId.value) {
      await updateFuelCard(editingCardId.value, payload)
      ElMessage.success('已更新')
    } else {
      await createFuelCard(payload)
      ElMessage.success('油卡已添加')
    }
    cardDialogVisible.value = false
    loadCardList()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeleteCard(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除油卡 ${row.card_no} 及其所有充值记录?`, '删除确认', { type: 'warning' })
    await deleteFuelCard(row.id)
    ElMessage.success('已删除')
    loadCardList()
    loadRecharges()
    loadStats()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || e?.message || '删除失败')
  }
}

function openRechargeDialog() {
  rechargePayload.card_id = null
  rechargePayload.amount = 1000
  rechargePayload.recharge_date = new Date().toISOString().slice(0, 10)
  rechargePayload.payment_method = '银行转账'
  rechargePayload.operator = ''
  rechargePayload.voucher_no = ''
  rechargePayload.notes = ''
  rechargeDialogVisible.value = true
}

async function handleRechargeSubmit() {
  if (!rechargeFormRef.value) return
  try { await rechargeFormRef.value.validate() } catch { return }
  submitting.value = true
  try {
    await createFuelCardRecharge({ ...rechargePayload })
    ElMessage.success('充值已记录, 余额已更新')
    rechargeDialogVisible.value = false
    loadRecharges()
    loadCardList()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeleteRecharge(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除该条充值记录 (¥${formatMoney(row.amount)})? 余额会同步扣减`, '删除确认', { type: 'warning' })
    await deleteFuelCardRecharge(row.id)
    ElMessage.success('已删除')
    loadRecharges()
    loadCardList()
    loadStats()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || e?.message || '删除失败')
  }
}

onMounted(() => {
  loadVehicles()
  loadCardList()
  loadRecharges()
  loadStats()
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.header-stats { display: flex; gap: 8px; }
.plate { font-weight: 600; color: #0c447c; margin-right: 8px; }
.vehicle-meta { color: #909399; font-size: 12px; }
.card-no { font-weight: 600; color: #0c447c; margin-right: 8px; }
.muted { color: #c0c4cc; }
.balance { color: #e6a23c; font-weight: 600; font-size: 15px; }
.amount-add { color: #67c23a; font-weight: 600; }
.date-warn { color: #e6a23c; font-weight: 600; }
.filter-bar { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
</style>
