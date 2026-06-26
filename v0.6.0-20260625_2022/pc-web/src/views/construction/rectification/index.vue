<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">整改工单</span>
      <div class="header-actions">
        <ScopeToggle @change="loadList" />
        <el-button :icon="Refresh" plain @click="loadList">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建整改</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目">
          <el-select
            v-model="searchForm.project_id"
            placeholder="全部"
            clearable
            filterable
            style="width: 220px"
          >
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="`${p.code ? p.code + ' - ' : ''}${p.name || ''}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="编号 / 整改内容" clearable style="width: 220px" />
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
        <el-table-column prop="code" label="整改编号" width="160" fixed show-overflow-tooltip />
        <el-table-column label="项目" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.project?.name || row.project_id || '-' }}</template>
        </el-table-column>
        <el-table-column prop="title" label="整改内容" min-width="240" show-overflow-tooltip />
        <el-table-column label="责任人" width="100" align="center">
          <template #default="{ row }">{{ row.owner?.name || row.owner_id || '-' }}</template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止日期" width="120" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="plain" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" align="center" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="goDetail(row)">详情</el-button>
            <el-button
              v-if="row.status !== 'completed'"
              link
              type="success"
              :icon="CircleCheck"
              @click="handleComplete(row)"
            >完成</el-button>
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

    <!-- 简易 dialog -->
    <el-dialog
      v-model="showFormDialog"
      title="新建整改工单"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="项目" required>
          <el-select v-model="formData.project_id" filterable placeholder="请选择" style="width: 100%">
            <el-option
              v-for="p in projectOptions"
              :key="p.id"
              :label="`${p.code ? p.code + ' - ' : ''}${p.name || ''}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="整改内容" required>
          <el-input v-model="formData.title" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="责任人">
          <el-select v-model="formData.owner_id" filterable placeholder="请选择" style="width: 100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="formData.deadline"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, CircleCheck } from '@element-plus/icons-vue'
import { rectificationApi } from '@/api/construction'
import { getProjectList, getUserList } from '@/api/modules'
import ScopeToggle from '@/components/ScopeToggle.vue'

const router = useRouter()

const statusOptions = [
  { value: 'pending',   label: '待处理' },
  { value: 'in_progress', label: '处理中' },
  { value: 'completed', label: '已完成' },
  { value: 'rejected',  label: '已驳回' },
]
const statusLabel = (s: string) => statusOptions.find(x => x.value === s)?.label || s || '-'
const statusTagType = (s: string): any => ({
  pending: 'info', in_progress: 'warning', completed: 'success', rejected: 'danger',
} as Record<string, string>)[s] || 'info'

const loading = ref(false)
const saving = ref(false)
const page = ref(1)
const pageSize = ref(10)
const list = ref<any[]>([])
const projectOptions = ref<any[]>([])
const userOptions = ref<any[]>([])

const searchForm = reactive<{ project_id: number | null; status: string; keyword: string }>({
  project_id: null, status: '', keyword: '',
})

const showFormDialog = ref(false)
const formData = reactive({ project_id: null as number | null, title: '', owner_id: null as number | null, deadline: '' })

const filteredList = computed(() => {
  let arr = [...list.value]
  if (searchForm.project_id) arr = arr.filter(r => Number(r.project_id) === Number(searchForm.project_id))
  if (searchForm.status) arr = arr.filter(r => r.status === searchForm.status)
  if (searchForm.keyword) {
    const kw = searchForm.keyword.toLowerCase()
    arr = arr.filter(r =>
      (r.code || '').toLowerCase().includes(kw) ||
      (r.title || '').toLowerCase().includes(kw)
    )
  }
  return arr
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

const loadList = async () => {
  loading.value = true
  try {
    const params: any = { per_page: 500, page: 1 }
    if (searchForm.project_id) params.project_id = searchForm.project_id
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const res: any = await rectificationApi.list(params)
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    list.value = arr
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [p, u] = await Promise.all([
      getProjectList({ per_page: 500 }),
      getUserList({ per_page: 500 }),
    ])
    projectOptions.value = ((p as any)?.data || p || []).map((x: any) => ({ id: x.id, code: x.code, name: x.name }))
    userOptions.value = ((u as any)?.data || u || [])
  } catch {
    projectOptions.value = []
    userOptions.value = []
  }
}

const handleSearch = () => { page.value = 1; loadList() }
const handleReset = () => {
  searchForm.project_id = null
  searchForm.status = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}

const handleAdd = () => {
  formData.project_id = null
  formData.title = ''
  formData.owner_id = null
  formData.deadline = ''
  showFormDialog.value = true
}

const handleSave = async () => {
  if (!formData.project_id || !formData.title) {
    ElMessage.warning('请填写项目与整改内容')
    return
  }
  saving.value = true
  try {
    await rectificationApi.create({
      project_id: formData.project_id,
      title: formData.title,
      owner_id: formData.owner_id,
      deadline: formData.deadline,
    })
    ElMessage.success('已创建')
    showFormDialog.value = false
    await loadList()
  } catch { /* 拦截器已提示 */ }
  finally { saving.value = false }
}

const goDetail = (row: any) => router.push(`/construction/rectification/${row.id}`)

const handleComplete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认完成整改「${row.code}」？完成后将不能再修改。`,
      '完成确认',
      { type: 'success', confirmButtonText: '确认完成', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    await rectificationApi.complete(row.id)
    ElMessage.success('已完成')
    await loadList()
  } catch { /* 拦截器已提示 */ }
}

onMounted(() => {
  loadOptions()
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
.filter-bar {
  background: #fff; padding: 16px 20px; border-radius: 8px;
  margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.content-card {
  background: #fff; padding: 20px; border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
