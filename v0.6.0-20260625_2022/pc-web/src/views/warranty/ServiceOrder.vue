<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">质保服务工单</span>
      <div class="header-actions">
        <ScopeToggle @change="loadList" />
        <el-button :icon="Refresh" plain @click="handleReset">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建工单</el-button>
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
        <el-form-item label="服务类型">
          <el-select v-model="searchForm.service_type" placeholder="全部类型" clearable style="width: 140px">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="技工">
          <el-input v-model="searchForm.technician_id" placeholder="技工ID" clearable style="width: 100px" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="工单号/描述" clearable style="width: 220px" />
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
        <el-table-column prop="order_no" label="工单号" min-width="160" fixed>
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="goDetail(row)">{{ row.order_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="质保期" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.warranty?.warranty_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="服务类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ typeLabel(row.service_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityTagType(row.priority)" effect="plain" size="small">
              {{ priorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标题" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.title || row.fault_description || '-' }}</template>
        </el-table-column>
        <el-table-column label="预约日期" width="120" align="center">
          <template #default="{ row }">{{ row.scheduled_date || row.scheduled_at || '-' }}</template>
        </el-table-column>
        <el-table-column label="技工" width="100" align="center">
          <template #default="{ row }">{{ row.technician?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="plain" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="goDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" link type="success" :icon="User" @click="assignRow(row)">派单</el-button>
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

    <!-- 派单 dialog -->
    <el-dialog v-model="assignDialog.visible" title="派单" width="400px">
      <el-form :model="assignDialog.form" label-width="80px">
        <el-form-item label="技工ID" required>
          <el-input-number v-model="assignDialog.form.technician_id" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, User } from '@element-plus/icons-vue'
import { warrantyOrderApi } from '@/api/warranty'
import ScopeToggle from '@/components/ScopeToggle.vue'

const router = useRouter()

const statusOptions = [
  { value: 'pending',     label: '待派工' },
  { value: 'assigned',    label: '已派工' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed',   label: '已完成' },
  { value: 'cancelled',   label: '已取消' },
]

const typeOptions = [
  { value: 'inspect',   label: '巡检' },
  { value: 'repair',    label: '维修' },
  { value: 'clean',     label: '清洁' },
  { value: 'calibrate', label: '校准' },
  { value: 'replace',   label: '更换' },
]

const priorityOptions = [
  { value: 'low',    label: '低' },
  { value: 'normal', label: '中' },
  { value: 'high',   label: '高' },
  { value: 'urgent', label: '紧急' },
]

const statusLabel    = (s: string) => statusOptions.find(x => x.value === s)?.label || s || '-'
const typeLabel      = (t: string) => typeOptions.find(x => x.value === t)?.label || t || '-'
const priorityLabel  = (p: string) => priorityOptions.find(x => x.value === p)?.label || p || '-'
const statusTagType  = (s: string) => ({ pending: 'info', assigned: 'warning', in_progress: 'primary', completed: 'success', cancelled: 'danger' } as any)[s] || 'info'
const priorityTagType = (p: string) => ({ low: 'info', normal: '', high: 'warning', urgent: 'danger' } as any)[p] || ''

const loading = ref(false)
const list = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)

const searchForm = reactive({
  status: '',
  service_type: '',
  priority: '',
  technician_id: '',
  keyword: '',
})

const kpis = computed(() => {
  const total = list.value.length
  const pending = list.value.filter(x => x.status === 'pending').length
  const in_progress = list.value.filter(x => x.status === 'in_progress').length
  const completed = list.value.filter(x => x.status === 'completed').length
  return [
    { label: '工单总数', value: total,        color: '#409EFF' },
    { label: '待派工',   value: pending,      color: '#909399' },
    { label: '进行中',   value: in_progress,  color: '#E6A23C' },
    { label: '已完成',   value: completed,    color: '#67C23A' },
  ]
})

const filteredList = computed(() => {
  return list.value.filter(x => {
    if (searchForm.status && x.status !== searchForm.status) return false
    if (searchForm.service_type && x.service_type !== searchForm.service_type) return false
    if (searchForm.priority && x.priority !== searchForm.priority) return false
    if (searchForm.technician_id && String(x.technician_id) !== String(searchForm.technician_id)) return false
    if (searchForm.keyword) {
      const kw = searchForm.keyword.toLowerCase()
      if (!String(x.order_no || '').toLowerCase().includes(kw) &&
          !String(x.fault_description || '').toLowerCase().includes(kw)) return false
    }
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
    const res: any = await warrantyOrderApi.list({ per_page: 200 })
    const d = res.data || res
    const items = d.data || d.items || d
    list.value = Array.isArray(items) ? items : []
  } catch (e: any) {
    ElMessage.error('加载工单失败: ' + (e.message || 'unknown'))
    list.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() { page.value = 1 }
function handleReset() {
  Object.assign(searchForm, { status: '', service_type: '', priority: '', technician_id: '', keyword: '' })
  page.value = 1
  loadList()
}

function handleAdd() {
  router.push('/project/warranty/service-order')
}

function goDetail(row: any) {
  router.push(`/project/warranty/service-order/detail/${row.id}`)
}

const assignDialog = reactive({ visible: false, form: { technician_id: 1 }, target: null as any })

function assignRow(row: any) {
  assignDialog.target = row
  assignDialog.form.technician_id = 1
  assignDialog.visible = true
}

async function submitAssign() {
  try {
    await warrantyOrderApi.assign(assignDialog.target.id, { technician_id: assignDialog.form.technician_id })
    ElMessage.success('已派单')
    assignDialog.visible = false
    loadList()
  } catch (e: any) {
    ElMessage.error('派单失败: ' + (e.message || 'unknown'))
  }
}

onMounted(loadList)
</script>
