<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">施工团队</span>
      <div class="header-actions">
        <el-button :icon="Refresh" plain @click="handleReset">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建团队</el-button>
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
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="全部类型" clearable style="width: 140px">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="团队名称 / 负责人" clearable style="width: 220px" />
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
        <el-table-column prop="name" label="团队名称" min-width="160" fixed show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="goDetail(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="100" align="center">
          <template #default="{ row }">
            {{ row.leader?.name || row.leader_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="130" align="center" />
        <el-table-column label="成员数" width="80" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.member_count ?? (row.members?.length ?? 0) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="工种" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-for="s in (row.specialty || [])" :key="s" size="small" effect="plain" style="margin-right: 4px">
              {{ s }}
            </el-tag>
            <span v-if="!row.specialty || row.specialty.length === 0" class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" effect="plain" size="small">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" align="center" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="goDetail(row)">详情</el-button>
            <el-button link type="warning" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
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

    <!-- 新建 / 编辑 dialog -->
    <TeamFormDialog
      v-model:visible="showFormDialog"
      :user-options="userOptions"
      :editing="editingTeam"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import { teamApi } from '@/api/construction'
import { getUserList } from '@/api/modules'
import TeamFormDialog from './components/TeamFormDialog.vue'

const router = useRouter()

const typeOptions = [
  { value: 'internal', label: '自有团队' },
  { value: 'external', label: '外包团队' },
  { value: 'mixed',    label: '混合团队' },
]
const typeLabel = (k: string) => typeOptions.find(t => t.value === k)?.label || k || '-'

const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const list = ref<any[]>([])
const userOptions = ref<any[]>([])

const searchForm = reactive<{ type: string; status: string; keyword: string }>({
  type: '', status: '', keyword: '',
})

const filteredList = computed(() => {
  let arr = [...list.value]
  if (searchForm.type) arr = arr.filter(r => r.type === searchForm.type)
  if (searchForm.status) arr = arr.filter(r => r.status === searchForm.status)
  if (searchForm.keyword) {
    const kw = searchForm.keyword.toLowerCase()
    arr = arr.filter(r =>
      (r.name || '').toLowerCase().includes(kw) ||
      (r.leader?.name || '').toLowerCase().includes(kw)
    )
  }
  return arr
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

const kpis = computed(() => {
  const total = list.value.length
  const active = list.value.filter(r => r.status === 'active').length
  const members = list.value.reduce((s, r) => s + (r.member_count ?? (r.members?.length ?? 0)), 0)
  return [
    { label: '团队总数', value: total,  color: '#0C447C' },
    { label: '启用中',  value: active, color: '#67c23a' },
    { label: '总成员数', value: members, color: '#1D9E75' },
  ]
})

const loadList = async () => {
  loading.value = true
  try {
    const params: any = { per_page: 500, page: 1 }
    if (searchForm.type)   params.type = searchForm.type
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const res: any = await teamApi.list(params)
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    list.value = arr
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const res: any = await getUserList({ per_page: 500 })
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    userOptions.value = arr
  } catch {
    userOptions.value = []
  }
}

const handleSearch = () => { page.value = 1 }
const handleReset = () => {
  searchForm.type = ''
  searchForm.status = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}

const goDetail = (row: any) => router.push(`/construction/team/${row.id}`)

// === 新建 / 编辑 ===
const showFormDialog = ref(false)
const editingTeam = ref<any>(null)

const handleAdd = () => {
  editingTeam.value = null
  showFormDialog.value = true
}

const handleEdit = (row: any) => {
  editingTeam.value = row
  showFormDialog.value = true
}

const handleSave = async (payload: any) => {
  try {
    if (editingTeam.value?.id) {
      await teamApi.update(editingTeam.value.id, payload)
      ElMessage.success('已更新')
    } else {
      await teamApi.create(payload)
      ElMessage.success('已创建')
    }
    showFormDialog.value = false
    editingTeam.value = null
    await loadList()
  } catch { /* 拦截器已提示 */ }
}

// === 删除 ===
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认删除团队「${row.name}」？已关联的成员关系将一并解除。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    await teamApi.remove(row.id)
    ElMessage.success('已删除')
    await loadList()
    if (pagedList.value.length === 0 && page.value > 1) page.value -= 1
  } catch { /* 拦截器已提示 */ }
}

onMounted(() => {
  loadUsers()
  loadList()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .page-title {
    font-size: 18px; font-weight: 600; color: #0C447C;
    border-left: 4px solid #0C447C; padding-left: 10px;
  }
  .header-actions { display: flex; gap: 8px; }
}
.kpi-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;
}
.kpi-card {
  .kpi-label { color: #909399; font-size: 13px; }
  .kpi-value { font-size: 22px; font-weight: 700; margin-top: 4px; }
}
.filter-bar {
  background: #fff; padding: 16px 20px; border-radius: 8px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.content-card {
  background: #fff; padding: 20px; border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
.muted { color: #c0c4cc; }
</style>
