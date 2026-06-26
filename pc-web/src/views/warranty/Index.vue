<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">质保期管理</span>
      <div class="header-actions">
        <ScopeToggle @change="loadList" />
        <el-button :icon="Refresh" plain @click="handleReset">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建质保期</el-button>
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
        <el-form-item label="类型">
          <el-select v-model="searchForm.warranty_type" placeholder="全部类型" clearable style="width: 140px">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目">
          <el-input v-model="searchForm.project_id" placeholder="项目ID" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="质保编号/名称" clearable style="width: 220px" />
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
        <el-table-column prop="warranty_no" label="质保编号" min-width="160" fixed show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="goDetail(row)">{{ row.warranty_no }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="质保名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.warranty_name || row.terms || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="项目" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="客户" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.customer?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ typeLabel(row.warranty_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="起止日期" width="200" align="center">
          <template #default="{ row }">
            <div style="font-size: 12px">{{ row.start_date }} ~ {{ row.end_date }}</div>
          </template>
        </el-table-column>
        <el-table-column label="剩余天数" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="daysLeftTag(row).type" effect="plain" size="small">
              {{ daysLeftText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="plain" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="goDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'active'" link type="success" :icon="Refresh" @click="handleRenew(row)">续期</el-button>
            <el-button v-if="['active', 'expiring'].includes(row.status)" link type="danger" :icon="CircleClose" @click="handleTerminate(row)">终止</el-button>
            <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
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

    <!-- 续期 / 终止弹窗 -->
    <el-dialog v-model="actionDialog.visible" :title="actionDialog.title" width="500px" :close-on-click-modal="false">
      <el-form :model="actionDialog.form" label-width="100px">
        <el-form-item v-if="actionDialog.type === 'renew'" label="续期月数">
          <el-input-number v-model="actionDialog.form.renew_months" :min="1" :max="600" />
        </el-form-item>
        <el-form-item label="原因/备注" required>
          <el-input v-model="actionDialog.form.reason" type="textarea" :rows="3" placeholder="请输入原因/备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitAction">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Delete, CircleClose } from '@element-plus/icons-vue'
import { warrantyApi } from '@/api/warranty'
import ScopeToggle from '@/components/ScopeToggle.vue'

const router = useRouter()

const statusOptions = [
  { value: 'active',     label: '在保' },
  { value: 'expiring',   label: '即将到期' },
  { value: 'expired',    label: '已过期' },
  { value: 'renewed',    label: '已续约' },
  { value: 'terminated', label: '已终止' },
]

const typeOptions = [
  { value: 'construction', label: '施工质保' },
  { value: 'equipment',    label: '设备质保' },
  { value: 'product',      label: '产品质保' },
  { value: 'service',      label: '服务质保' },
]

const statusLabel = (s: string) => statusOptions.find(x => x.value === s)?.label || s || '-'
const typeLabel   = (t: string) => typeOptions.find(x => x.value === t)?.label || t || '-'
const statusTagType = (s: string) => {
  if (s === 'active')     return 'success'
  if (s === 'expiring')   return 'warning'
  if (s === 'expired')    return 'danger'
  if (s === 'terminated') return 'info'
  return 'info'
}

const daysLeftText = (row: any) => {
  if (row.status === 'expired' || row.status === 'terminated' || row.status === 'renewed') return '-'
  if (!row.end_date) return '-'
  const end = new Date(row.end_date).getTime()
  const now = Date.now()
  const days = Math.ceil((end - now) / (1000 * 60 * 60 * 24))
  if (days < 0) return `已过期 ${Math.abs(days)} 天`
  if (days === 0) return '今日到期'
  return `${days} 天`
}

const daysLeftTag = (row: any) => {
  const text = daysLeftText(row)
  if (text.includes('已过期')) return { type: 'danger' as const }
  if (text === '今日到期') return { type: 'warning' as const }
  if (text.includes('天') && text.includes('天')) {
    const n = parseInt(text)
    if (n <= 30) return { type: 'warning' as const }
    if (n <= 90) return { type: 'info' as const }
  }
  return { type: 'success' as const }
}

const loading = ref(false)
const list = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)

const searchForm = reactive({
  status: '',
  warranty_type: '',
  project_id: '',
  keyword: '',
})

const kpis = computed(() => {
  const total    = list.value.length
  const active   = list.value.filter(x => x.status === 'active').length
  const expiring = list.value.filter(x => x.status === 'expiring').length
  const expired  = list.value.filter(x => x.status === 'expired').length
  return [
    { label: '质保总数', value: total,    color: '#409EFF' },
    { label: '在保',     value: active,   color: '#67C23A' },
    { label: '即将到期', value: expiring, color: '#E6A23C' },
    { label: '已过期',   value: expired,  color: '#F56C6C' },
  ]
})

const filteredList = computed(() => {
  return list.value.filter(x => {
    if (searchForm.status && x.status !== searchForm.status) return false
    if (searchForm.warranty_type && x.warranty_type !== searchForm.warranty_type) return false
    if (searchForm.project_id && String(x.project_id) !== String(searchForm.project_id)) return false
    if (searchForm.keyword) {
      const kw = searchForm.keyword.toLowerCase()
      if (!String(x.warranty_no || '').toLowerCase().includes(kw) &&
          !String(x.warranty_name || '').toLowerCase().includes(kw)) return false
    }
    return true
  })
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

const actionDialog = reactive({
  visible: false,
  title: '',
  type: '' as '' | 'renew' | 'terminate',
  target: null as any,
  form: { renew_months: 12, reason: '' },
})

async function loadList() {
  loading.value = true
  try {
    const res: any = await warrantyApi.list({ per_page: 200 })
    const d = res.data || res
    const items = d.data || d.items || d
    list.value = Array.isArray(items) ? items : []
  } catch (e: any) {
    ElMessage.error('加载质保期失败: ' + (e.message || 'unknown'))
    list.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
}

function handleReset() {
  searchForm.status = ''
  searchForm.warranty_type = ''
  searchForm.project_id = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}

function handleAdd() {
  router.push('/project/warranty/create')
}

function goDetail(row: any) {
  router.push(`/project/warranty/detail/${row.id}`)
}

function handleRenew(row: any) {
  actionDialog.type = 'renew'
  actionDialog.title = `续期 - ${row.warranty_no}`
  actionDialog.target = row
  actionDialog.form = { renew_months: 12, reason: '' }
  actionDialog.visible = true
}

function handleTerminate(row: any) {
  actionDialog.type = 'terminate'
  actionDialog.title = `终止质保期 - ${row.warranty_no}`
  actionDialog.target = row
  actionDialog.form = { renew_months: 12, reason: '' }
  actionDialog.visible = true
}

async function submitAction() {
  if (!actionDialog.form.reason) {
    ElMessage.warning('请填写原因/备注')
    return
  }
  try {
    if (actionDialog.type === 'renew') {
      await warrantyApi.renew(actionDialog.target.id, {
        renew_months: actionDialog.form.renew_months,
        remark: actionDialog.form.reason,
      })
      ElMessage.success('质保期已续期')
    } else {
      await warrantyApi.terminate(actionDialog.target.id, {
        terminate_reason: actionDialog.form.reason,
        remark: actionDialog.form.reason,
      })
      ElMessage.success('质保期已终止')
    }
    actionDialog.visible = false
    loadList()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + (e.message || 'unknown'))
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除质保期 ${row.warranty_no}?`, '删除确认', {
      type: 'warning',
    })
    await warrantyApi.remove(row.id)
    ElMessage.success('已删除')
    loadList()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + (e.message || 'unknown'))
    }
  }
}

onMounted(loadList)
</script>
