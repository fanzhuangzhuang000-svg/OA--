<template>
  <div class="page-container">
    <div class="page-header">
      <h2>物料退库</h2>
    </div>
    <div class="filter-bar">
      <el-input v-model="searchKey" placeholder="搜索单号/物料" clearable style="width: 240px" :prefix-icon="Search" @keyup.enter="loadList(1)" @clear="loadList(1)" />
      <el-button type="primary" plain :icon="Plus" @click="handleCreate">新增退库</el-button>
    </div>

    <div class="content-card">
      <el-table v-loading="loading" :data="list" stripe border style="width: 100%">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="record_no" label="退库单号" width="180" />
        <el-table-column label="物料" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.inventoryItem">{{ row.inventoryItem.name }}（{{ row.inventoryItem.code }}）</span>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="退回仓库" width="120">
          <template #default="{ row }">{{ row.warehouse?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="退库数量" width="120" align="right">
          <template #default="{ row }">
            <span style="font-weight: 600; color: #1D9E75">+{{ row.quantity }}</span>
            <span class="unit-text"> {{ row.inventoryItem?.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="退库后库存" width="120" align="center">
          <template #default="{ row }">{{ row.remaining_stock }} {{ row.inventoryItem?.unit || '' }}</template>
        </el-table-column>
        <el-table-column label="退库人" width="100">
          <template #default="{ row }">{{ row.operator?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="退库时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="退库原因" min-width="200" show-overflow-tooltip />
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

    <el-dialog v-model="showFormDialog" title="新增物料退库" width="1500px" :close-on-click-modal="false">
      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px">
        退库单将增加物料库存。常见场景：项目剩余物料退回、领用错退。
      </el-alert>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="物料" prop="inventory_item_id">
          <el-select v-model="form.inventory_item_id" filterable placeholder="搜索物料名称/编号" style="width: 100%">
            <el-option
              v-for="it in itemOptions"
              :key="it.id"
              :label="`${it.name}（${it.code}）`"
              :value="it.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="退库数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="退回仓库" prop="warehouse_id">
          <el-select v-model="form.warehouse_id" placeholder="选择仓库" style="width: 100%">
            <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="退库原因" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="请说明退库原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="success" :loading="submitting" @click="handleSubmit">确认退库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { Search, Plus, Document, Goods, Delete } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { get, post } from "@/utils/request"
import InventoryItemPicker from "./components/InventoryItemPicker.vue" 

const searchKey = ref('')
const list = ref<any[]>([])
const loading = ref(false)
const pagination = reactive({ page: 1, per_page: 15, total: 0 })
const itemOptions = ref<any[]>([])
const warehouseOptions = ref<any[]>([])

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
    const res: any = await get('/inventory/stock-records', { type: 'return', page, per_page: pagination.per_page })
    const d = res || {}
    let items = d.data || d.items || d || []
    if (searchKey.value) {
      const kw = searchKey.value.toLowerCase()
      items = items.filter((r: any) =>
        (r.record_no || '').toLowerCase().includes(kw) ||
        (r.inventoryItem?.name || '').toLowerCase().includes(kw)
      )
    }
    list.value = items
    pagination.total = items.length
  } catch (e) {
    console.error('[loadList]', e)
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

async function loadWarehouses() {
  try {
    const res: any = await get('/inventory/warehouses')
    warehouseOptions.value = res.data || res || []
  } catch (e) { console.warn('[loadWarehouses]', e) }
}

const showFormDialog = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  warehouse_id: null,
  type: 'return',
  remark: '',
  items: [],
})
const rules = {
  inventory_item_id: [{ required: true, message: '请选择物料', trigger: 'change' }],
  quantity:          [{ required: true, type: 'number' as const, min: 1, message: '请输入数量' }],
  warehouse_id:      [{ required: true, message: '请选择仓库', trigger: 'change' }],
  remark:            [{ required: true, message: '请填写退库原因', trigger: 'blur' }],
}

function handleCreate() {
  form.warehouse_id = warehouseOptions.value[0]?.id||null
  form.remark = ""
  form.items = [{ item: null, quantity: 1 }]
  showFormDialog.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await post('/inventory/stock-in', form)
    ElMessage.success('退库成功，库存已恢复')
    showFormDialog.value = false
    loadList(pagination.page)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e.message || '退库失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadList(1)
  loadItems()
  loadWarehouses()
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
</style>
