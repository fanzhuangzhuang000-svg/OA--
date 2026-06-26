<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">招标中心</span>
      <div class="header-actions">
        <el-button :icon="Refresh" plain @click="loadList">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="onCreate">新建招标项目</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input v-model="filter.keyword" placeholder="编号/名称" clearable style="width:240px" @keyup.enter="loadList" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filter.status" placeholder="全部" clearable style="width:160px">
            <el-option v-for="o in STATUS_OPTIONS" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadList">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="filteredList" v-loading="loading" stripe border>
      <el-table-column prop="code" label="编号" width="170" />
      <el-table-column prop="name" label="项目名称" min-width="220" show-overflow-tooltip />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="row.type === 'tender' ? 'danger' : row.type === 'rfq' ? 'warning' : 'info'" effect="light">
            {{ typeLabel(row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="关联项目" width="160" show-overflow-tooltip>
        <template #default="{ row }">{{ row.project?.name || '-' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag size="small" :type="statusTag(row.status)" effect="light">
            {{ row.status_label || row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="投标数" width="80" align="center">
        <template #default="{ row }">{{ row.bids_count ?? (row.bids_summary?.length ?? 0) }}</template>
      </el-table-column>
      <el-table-column label="截标" width="170">
        <template #default="{ row }">{{ fmt(row.deadline) }}</template>
      </el-table-column>
      <el-table-column label="中标供应商" width="160" show-overflow-tooltip>
        <template #default="{ row }">{{ row.awardedSupplier?.name || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="goDetail(row)">详情</el-button>
          <el-button link v-if="row.status === 'draft'" type="primary" @click="onEdit(row)">编辑</el-button>
          <el-button link v-if="row.status === 'draft'" type="success" @click="onPublish(row)">发布</el-button>
          <el-button link v-if="['bidding','evaluating'].includes(row.status)" type="danger" @click="onCancel(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <EditTenderDialog
      v-model:visible="showEditDialog"
      :tender="currentEdit"
      @saved="loadList"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { tender } from '@/api/tender'
import type { TenderProject } from '@/api/tender'
import EditTenderDialog from './components/EditTenderDialog.vue'

const router = useRouter()
const list = ref<TenderProject[]>([])
const loading = ref(false)
const filter = reactive({ keyword: '', status: '' })

const showEditDialog = ref(false)
const currentEdit = ref<TenderProject | null>(null)

const STATUS_OPTIONS = [
  { value: 'draft', label: '草稿' },
  { value: 'bidding', label: '招标中' },
  { value: 'evaluating', label: '评标中' },
  { value: 'awarded', label: '已中标' },
  { value: 'closed', label: '已关闭' },
  { value: 'cancelled', label: '已取消' },
]

const typeLabel = (t?: string) =>
  t === 'tender' ? '招标' : t === 'rfq' ? '询价' : t === 'negotiation' ? '议价' : '-'

const statusTag = (s: string) => {
  return ({
    draft: 'info',
    bidding: 'warning',
    evaluating: 'primary',
    awarded: 'success',
    closed: '',
    cancelled: 'danger',
  } as Record<string, '' | 'success' | 'warning' | 'info' | 'primary' | 'danger'>)[s] || ''
}

const fmt = (s?: string) => (s ? s.replace('T', ' ').slice(0, 16) : '-')

const filteredList = computed(() => list.value)

const loadList = async () => {
  loading.value = true
  try {
    const res: any = await tender.list({
      keyword: filter.keyword || undefined,
      status: filter.status || undefined,
      per_page: 200,
    })
    list.value = res?.items ?? res?.data?.items ?? []
  } finally {
    loading.value = false
  }
}

const onCreate = () => { currentEdit.value = null; showEditDialog.value = true }
const onEdit = (row: TenderProject) => { currentEdit.value = row; showEditDialog.value = true }

const goDetail = (row: TenderProject) => {
  router.push({ name: 'TenderDetail', params: { id: String(row.id) } })
}

const onPublish = async (row: TenderProject) => {
  try {
    await ElMessageBox.confirm(`确认发布「${row.name}」? 发布后将生成对外邀请链接,不可回退到草稿。`, '发布确认', { type: 'success' })
  } catch { return }
  await tender.publish(row.id)
  ElMessage.success('已发布')
  loadList()
}

const onCancel = async (row: TenderProject) => {
  try {
    await ElMessageBox.confirm(`确认取消「${row.name}」?`, '取消确认', { type: 'warning' })
  } catch { return }
  await tender.cancel(row.id)
  ElMessage.success('已取消')
  loadList()
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.page-container { padding: 16px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.page-title { font-size: 18px; font-weight: 600; }
.header-actions { display: flex; gap: 8px; }
.filter-bar { margin-bottom: 12px; }
</style>
