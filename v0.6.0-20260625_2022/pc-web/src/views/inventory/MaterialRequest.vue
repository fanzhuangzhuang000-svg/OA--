<template>
  <div class="page-container">
    <div class="page-header">
      <h2>物料申领</h2>
    </div>
    <div class="filter-bar">
      <el-input v-model="searchKey" placeholder="搜索单号/物料" clearable style="width: 240px" :prefix-icon="Search" @keyup.enter="loadList(1)" @clear="loadList(1)" />
      <el-button type="primary" plain :icon="Plus" @click="handleCreate">新增申领</el-button>
    </div>

    <div class="content-card">
      <el-table v-loading="loading" :data="list" stripe border style="width: 100%">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="审批单号" width="160">
          <template #default="{row}"><span class="record-no">{{ row.code }}</span></template>
        </el-table-column>
        <el-table-column label="申领内容" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.title }}
          </template>
        </el-table-column>
        <el-table-column label="申领人" width="100">
          <template #default="{ row }">{{ row.warehouse?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="申领数量" width="120" align="right">
          <template #default="{ row }">
            <span style="font-weight: 600; color: #A32D2D">-{{ row.quantity }}</span>
            <span class="unit-text"> {{ row.inventoryItem?.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="申领后库存" width="120" align="center">
          <template #default="{ row }">{{ row.remaining_stock }} {{ row.inventoryItem?.unit || '' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{row}">
            <el-tag :type="row.status==='approved'?'success':row.status==='rejected'?'danger':'warning'" size="small">{{ {pending:'待审批',approved:'已通过',rejected:'已驳回',transferred:'已转交',cancelled:'已取消'}[row.status]||row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">{{ row.created_at?.slice(0,16)||'-' }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="申领说明" min-width="200" show-overflow-tooltip />
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="pagination.total"
          :current-page="pagination.page"
          :page-size="pagination.per_page"
          @current-change="(p) => loadList(p)"
        />
      </div>
    </div>

    <RequestFormDialog
      v-model:visible="showFormDialog"
      :form="form"
      :rules="rules"
      :project-options="projectOptions"
      :warehouse-options="warehouseOptions"
      :user-options="userOptions"
      :submitting="submitting"
      @add-item="addItemRow"
      @remove-item="(i: number) => form.items.splice(i, 1)"
      @pick-item="openPickerByUid"
      @submit="handleSubmit"
    />

    <ItemPickerDialog
      v-model:visible="pickerVisible"
      v-model:category-filter="pickerCategoryFilter"
      v-model:search-key="pickerSearchKey"
      :categories="pickerCategories"
      :filtered-items="pickerFilteredItems"
      :selected-item="pickerSelectedItem"
      @row-click="(evt: any) => pickerSelectedItem = evt.row"
      @confirm="pickerConfirm"
    />

</div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { get, post } from '@/utils/request'
import RequestFormDialog from './components/material-request/RequestFormDialog.vue'
import ItemPickerDialog from './components/material-request/ItemPickerDialog.vue'

const searchKey = ref('')
const list = ref<any[]>([])
const loading = ref(false)
const pagination = reactive({ page: 1, per_page: 15, total: 0 })
const itemOptions = ref<any[]>([])
const warehouseOptions = ref<any[]>([])
const projectOptions = ref<any[]>([])
const userOptions = ref<any[]>([])

const formatDate = (s?: string) => {
  if (!s) return '-'
  const d = new Date(s)
  if (isNaN(d.getTime())) return s
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}



async function loadList(page = 1) {
  pagination.page = page
  loading.value = true
  try {
    const res: any = await get('/approvals/operation', { sub_type: 'material-request', page, per_page: pagination.per_page })
    const d = res || {}
    list.value = d.data?.data || d.data || d || []
    pagination.total = d.data?.total || list.value.length
  } catch (e) {
    console.error(e)
    list.value = []
  } finally {
    loading.value = false
  }
}

async function loadItems() {
  try {
    const res: any = await get('/inventory', { per_page: 200 })
    const d = res || {}
    itemOptions.value = d.data || d.items || d || []
  } catch (e) { console.warn('[loadItems]', e) }
}

async function loadProjects() {
  try { const res=await get('/projects',{per_page:500}); const d=res||{}; projectOptions.value=d.data?.data||d.data?.items||d.data||d.items||d||[] }
  catch(e){ console.warn(e) }
}

async function loadUsers() {
  try { const res=await get('/employees',{per_page:500}); const d=res||{}; userOptions.value=d.data?.data||d.data?.items||d.data||d.items||d||[] }
  catch(e){ console.warn(e) }
}

async function loadCurrentUser() {
  try { const res=await get('/auth/me'); curUser.value=res.data||res||null }
  catch(e){}
}

async function loadWarehouses() {
  try {
    const res: any = await get('/inventory/warehouses')
    warehouseOptions.value = res.data || res || []
  } catch (e) { console.warn('[loadWarehouses]', e) }
}

const curUser = ref<any>(null)

const showFormDialog = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  warehouse_id: null,
  type: 'outbound',
  project_id: null,
  applicant_id: null,
  remark: '',
  items: [],
})
const rules = {
  project_id:   [{ required: true, message: "请选择项目", trigger: "change" }],
  warehouse_id: [{ required: true, message: "请选择仓库", trigger: "change" }],
  applicant_id: [{ required: true, message: "请选择申领人", trigger: "change" }],
  remark:       [{ required: true, message: "请填写申领说明", trigger: "blur" }],
}

function handleCreate() {
  form.warehouse_id = warehouseOptions.value[0]?.id||null
  form.project_id = null
  form.applicant_id = curUser.value?.id||null
  form.remark = ""
  form.items = [{ item: null, quantity: 1 }]
  showFormDialog.value = true
}

const pickerVisible = ref(false)
const pickerIndex = ref(-1)

function addItemRow() {
  form.items.push({ uid: Date.now() + Math.random(), item: null, quantity: 1 })
}

function removeItemRow(idx) {
  form.items.splice(idx, 1)
}


function openPickerByUid(uid) {
  const idx = form.items.findIndex(i => i.uid === uid)
  if (idx >= 0) openPicker(idx)
}


function openPicker(idx) {
  pickerIndex.value = idx
  pickerVisible.value = true
}


function openPickerByKey(key) { 
  const idx = form.items.findIndex(i => i.uid === key)
  if (idx >= 0) openPicker(idx)
}

// Picker dialog state
const pickerSearchKey = ref("")
const pickerCategoryFilter = ref(null)
const pickerSelectedItem = ref(null)

const pickerCategories = computed(() => {
  const map = new Map()
  for (const i of itemOptions.value) {
    if (i.category?.id) map.set(i.category.id, i.category)
  }
  return [...map.values()]
})

const pickerFilteredItems = computed(() => {
  const kw = pickerSearchKey.value.trim().toLowerCase()
  const catId = pickerCategoryFilter.value
  return itemOptions.value.filter(i => {
    if (catId && i.category?.id !== catId) return false
    if (!kw) return true
    return (i.name||"").toLowerCase().includes(kw) ||
      (i.code||"").toLowerCase().includes(kw) ||
      (i.spec||"").toLowerCase().includes(kw) ||
      (i.category?.name||"").toLowerCase().includes(kw)
  })
})

function pickerRowClick(row) { pickerSelectedItem.value = row }
function pickerConfirm() {
  if (pickerSelectedItem.value) {
    onPickerSelect(pickerSelectedItem.value)
    pickerVisible.value = false
    pickerSelectedItem.value = null
    pickerSearchKey.value = ""
    pickerCategoryFilter.value = null
  }
}
function onPickerSelect(item) {
  const idx = pickerIndex.value
  if (idx >= 0 && idx < form.items.length) {
    form.items[idx].item = { ...item }
    form.items[idx].quantity = Math.min(form.items[idx].quantity||1, item.current_stock||1)

  }
}

async function handleSubmit() {
  if (!formRef.value) { ElMessage.error("表单未初始化"); return }
  try {
    const valid = await formRef.value.validate()
    if (!valid) { ElMessage.warning("请检查表单填写"); submitting.value = false; return }
  } catch(e) {
    ElMessage.warning("请检查表单填写")
    submitting.value = false
    return
  }
  const validItems = form.items.filter(i=>i.item)
  if (validItems.length === 0) { ElMessage.warning("请至少选择一种物料"); return }

  submitting.value = true
  try {
    const itemsPayload = validItems.map(i=>({
      inventory_item_id: i.item.id,
      quantity: i.quantity,
      warehouse_id: form.warehouse_id,
    }))
    await post("/approvals/operation", {
      sub_type: "material-request",
      title: "物料申领",
      payload: {
        items: itemsPayload,
        project_id: form.project_id,
        remark: form.remark,
      },
      applicant_id: form.applicant_id,
    })
    ElMessage.success("申领已提交，等待审批通过后自动出库")
    showFormDialog.value = false
    loadList(pagination.page)
  } catch(e) {
    ElMessage.error(e?.response?.data?.message||e.message||"提交审批失败")
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadList(1)
  loadItems()
  loadWarehouses()
  loadProjects()
  loadUsers()
  loadCurrentUser()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header { margin-bottom: 16px; h2 { font-size: 20px; color: #0C447C; margin: 0; } }
.filter-bar {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  margin-bottom: 16px; padding: 16px;
  background: #fff; border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.content-card {
  background: #fff; border-radius: 8px; padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
.muted { color: #c0c4cc; }
.section-card { background:#fff; border:1px solid #e8ecf1; border-radius:8px; padding:16px 16px 0 }
.section-title { font-size:14px; font-weight:600; color:#0C447C; margin-bottom:12px; padding-bottom:8px; border-bottom:2px solid #e6f1fb; display:flex; align-items:center; gap:6px }
.section-title .el-icon { font-size:16px }
.item-code { font-family:"DIN Pro",monospace; font-weight:500; color:#0C447C; font-size:12px }
:deep(.el-dialog__body) { padding-top:12px }
.unit-text { color: #909399; font-size: 12px; }
.form-tip { font-size: 12px; color: #909399; margin-top: 4px; }
</style>