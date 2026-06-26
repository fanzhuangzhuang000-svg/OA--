<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">工序字典</span>
      <div class="header-actions">
        <el-button :icon="Refresh" plain @click="loadList">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增工序</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="工序名 / 编码" clearable style="width: 220px" />
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
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="工序名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="分类" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ categoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="单位" width="80" align="center" prop="unit" />
        <el-table-column label="标准工时" width="110" align="right">
          <template #default="{ row }">{{ row.standard_hours || 0 }} h</template>
        </el-table-column>
        <el-table-column prop="sequence" label="排序" width="80" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" effect="plain" size="small">
              {{ row.status === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
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

    <!-- 工序表单 dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑工序' : '新增工序'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="编码" prop="code">
          <el-input v-model="formData.code" maxlength="50" placeholder="如：PR-001" />
        </el-form-item>
        <el-form-item label="工序名称" prop="name">
          <el-input v-model="formData.name" maxlength="50" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择" style="width: 100%">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="formData.unit" maxlength="20" placeholder="如：m / 个 / 台" />
        </el-form-item>
        <el-form-item label="标准工时">
          <el-input-number v-model="formData.standard_hours" :min="0" :step="0.5" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sequence" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { workProcessApi } from '@/api/construction'

const categoryOptions = [
  { value: 'preparation', label: '施工准备' },
  { value: 'main',        label: '主体施工' },
  { value: 'auxiliary',   label: '辅助工程' },
  { value: 'finishing',   label: '装饰收尾' },
  { value: 'inspection',  label: '验收交付' },
]
const categoryLabel = (k: string) => categoryOptions.find(c => c.value === k)?.label || k || '-'

const loading = ref(false)
const saving = ref(false)
const page = ref(1)
const pageSize = ref(10)
const list = ref<any[]>([])

const searchForm = reactive<{ category: string; keyword: string }>({
  category: '', keyword: '',
})

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()

const formData = reactive({
  code: '',
  name: '',
  category: 'main',
  unit: '',
  standard_hours: 0,
  sequence: 0,
  status: 'active',
  remark: '',
})

const formRules = {
  code:     [{ required: true, message: '请输入编码', trigger: 'blur' }],
  name:     [{ required: true, message: '请输入工序名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

const filteredList = computed(() => {
  let arr = [...list.value]
  if (searchForm.category) arr = arr.filter(r => r.category === searchForm.category)
  if (searchForm.keyword) {
    const kw = searchForm.keyword.toLowerCase()
    arr = arr.filter(r => (r.code || '').toLowerCase().includes(kw) || (r.name || '').toLowerCase().includes(kw))
  }
  return arr
})

const pagedList = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

const resetForm = () => {
  formData.code = ''
  formData.name = ''
  formData.category = 'main'
  formData.unit = ''
  formData.standard_hours = 0
  formData.sequence = 0
  formData.status = 'active'
  formData.remark = ''
}

const loadList = async () => {
  loading.value = true
  try {
    const params: any = { per_page: 500, page: 1 }
    if (searchForm.category) params.category = searchForm.category
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const res: any = await workProcessApi.list(params)
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    list.value = arr
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { page.value = 1 }
const handleReset = () => {
  searchForm.category = ''
  searchForm.keyword = ''
  page.value = 1
  loadList()
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  editingId.value = null
  showDialog.value = true
}

const handleEdit = (row: any) => {
  formData.code = row.code || ''
  formData.name = row.name || ''
  formData.category = row.category || 'main'
  formData.unit = row.unit || ''
  formData.standard_hours = Number(row.standard_hours || 0)
  formData.sequence = Number(row.sequence || 0)
  formData.status = row.status || 'active'
  formData.remark = row.remark || ''
  isEdit.value = true
  editingId.value = row.id
  showDialog.value = true
}

const handleSave = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      code: formData.code,
      name: formData.name,
      category: formData.category,
      unit: formData.unit,
      standard_hours: Number(formData.standard_hours || 0),
      sequence: Number(formData.sequence || 0),
      status: formData.status,
      remark: formData.remark,
    }
    if (isEdit.value && editingId.value) {
      await workProcessApi.update(editingId.value, payload)
      ElMessage.success('已更新')
    } else {
      await workProcessApi.create(payload)
      ElMessage.success('已创建')
    }
    showDialog.value = false
    await loadList()
  } catch { /* 拦截器已提示 */ }
  finally { saving.value = false }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认删除工序「${row.name}」？该操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
  } catch { return }
  try {
    await workProcessApi.remove(row.id)
    ElMessage.success('已删除')
    await loadList()
  } catch { /* 拦截器已提示 */ }
}

onMounted(() => loadList())
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
