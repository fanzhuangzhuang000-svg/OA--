<template>
  <div class="page-container">
    <div class="page-header"><h2>入库单</h2></div>
    <div class="filter-bar">
      <el-select v-model="filterType" placeholder="入库类型" clearable style="width:160px" @change="loadList(1)">
        <el-option label="采购入库" value="inbound" /><el-option label="退库入库" value="return" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" @change="loadList(1)" />
      <el-input v-model="searchKey" placeholder="搜索单号/物料" clearable style="width:220px" :prefix-icon="Search" @keyup.enter="loadList(1)" @clear="loadList(1)" />
      <el-button type="primary" plain :icon="Plus" @click="handleCreate">新增入库单</el-button>
    </div>

    <div class="content-card">
      <el-table v-loading="loading" :data="list" stripe border style="width:100%">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="record_no" label="单号" width="170">
          <template #default="{row}"><span class="record-no">{{ row.record_no }}</span></template>
        </el-table-column>
        <el-table-column label="入库类型" width="90" align="center">
          <template #default="{row}"><el-tag :type="row.type==='inbound'?'success':'info'" size="small">{{ row.type==='inbound'?'采购入库':'退库入库' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="物料" min-width="170" show-overflow-tooltip>
          <template #default="{row}"><span v-if="row.inventoryItem">{{ row.inventoryItem.name }}({{ row.inventoryItem.code }})</span><span v-else class="muted">-</span></template>
        </el-table-column>
        <el-table-column label="仓库" width="90">
          <template #default="{row}">{{ row.warehouse?.name||'-' }}</template>
        </el-table-column>
        <el-table-column label="往来单位" width="150" show-overflow-tooltip>
          <template #default="{row}"><span v-if="row.party">{{ row.party.name }}</span><span v-else class="muted">-</span></template>
        </el-table-column>
        <el-table-column label="关联项目" width="150" show-overflow-tooltip>
          <template #default="{row}"><span v-if="row.project">{{ row.project.name }}</span><span v-else class="muted">-</span></template>
        </el-table-column>
        <el-table-column label="入库数量" width="100" align="right">
          <template #default="{row}"><span style="font-weight:600;color:#1D9E75">+{{ row.quantity }}</span><span class="unit-text"> {{ row.inventoryItem?.unit||'' }}</span></template>
        </el-table-column>
        <el-table-column label="入库后库存" width="100" align="center">
          <template #default="{row}">{{ row.remaining_stock }} {{ row.inventoryItem?.unit||'' }}</template>
        </el-table-column>
        <el-table-column label="操作人" width="90">
          <template #default="{row}">{{ row.operator?.name||'-' }}</template>
        </el-table-column>
        <el-table-column label="入库时间" width="150">
          <template #default="{row}">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="110" show-overflow-tooltip />
      </el-table>
      <div class="pagination-wrap">
        <el-pagination background layout="total,prev,pager,next" :total="pagination.total" :current-page="pagination.page" :page-size="pagination.per_page" @current-change="p=>loadList(p)" />
      </div>
    </div>

    <el-dialog v-model="showFormDialog" title="新增入库单" width="1500px" :close-on-click-modal="false" top="3vh">
      <div class="section-card">
        <div class="section-title"><el-icon><Document /></el-icon> 基本信息</div>
        <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="单号">
                <el-input :model-value="autoRecordNo" disabled style="width:100%">
                  <template #prefix><el-icon><Document /></el-icon></template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="入库类型">
                <el-radio-group v-model="form.type">
                  <el-radio value="inbound">采购入库</el-radio>
                  <el-radio value="return">退库入库</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="入库仓库" prop="warehouse_id">
                <el-select v-model="form.warehouse_id" placeholder="选择仓库" style="width:100%">
                  <el-option v-for="w in warehouseOptions" :key="w.id" :label="w.name" :value="w.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="往来单位" prop="party_id">
                <el-select v-model="form.party_id" filterable placeholder="选择供应商" style="width:100%" @change="onPartyChange">
                  <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="结算单位">
                <el-select v-model="form.settle_id" filterable placeholder="默认同往来单位" style="width:100%" clearable>
                  <el-option v-for="s in supplierOptions" :key="s.id" :label="s.name" :value="s.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="关联项目">
                <el-select v-model="form.project_id" filterable clearable placeholder="选择项目(可选)" style="width:100%">
                  <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="24">
              <el-form-item label="备注">
                <el-input v-model="form.remark" maxlength="500" show-word-limit />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <div class="section-card" style="margin-top:16px">
        <div class="section-title" style="display:flex;align-items:center;justify-content:space-between">
          <span><el-icon><Goods /></el-icon> 入库明细</span>
          <el-button size="small" type="primary" :icon="Plus" @click="addItemRow()">添加物料</el-button>
        </div>
        <el-table :data="form.items" stripe border style="width:100%" max-height="360">
          <el-table-column type="index" label="#" width="42" />
          <el-table-column label="编码" width="120">
            <template #default="{row}">
              <span v-if="row.item" class="item-code">{{ row.item.code }}</span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="物料名称" min-width="160">
            <template #default="{row,$index}">
              <div style="display:flex;gap:4px;align-items:center">
                <span v-if="row.item" style="flex:1">{{ row.item.name }}</span>
                <el-button size="small" type="primary" link @click="openPicker($index)">{{ row.item?'更换':'选择物料' }}</el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="规格" width="100" show-overflow-tooltip>
            <template #default="{row}"><span v-if="row.item?.spec">{{ row.item.spec }}</span><span v-else class="text-muted">-</span></template>
          </el-table-column>
          <el-table-column label="单位" width="60" align="center">
            <template #default="{row}">{{ row.item?.unit||'-' }}</template>
          </el-table-column>
          <el-table-column label="当前库存" width="80" align="center">
            <template #default="{row}">
              <el-tag v-if="row.item" :type="(row.item.current_stock??0)<=0?'danger':(row.item.current_stock??0)<10?'warning':'success'" size="small" effect="plain">{{ row.item.current_stock??0 }}</el-tag>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>
          <el-table-column label="入库数量" width="130">
            <template #default="{row}">
              <el-input-number v-model="row.quantity" :min="1" :step="1" style="width:110px" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="55" align="center">
            <template #default="{_,$index}">
              <el-button type="danger" link size="small" :icon="Delete" @click="removeItemRow($index)" />
            </template>
          </el-table-column>
        </el-table>
        <div v-if="form.items.length===0" style="text-align:center;padding:24px;color:#c0c4cc">
          <el-empty :image-size="50" description="暂无物料，点击上方「添加物料」按钮" />
        </div>
      </div>

      <template #footer>
        <el-button @click="showFormDialog=false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认入库</el-button>
      </template>
    </el-dialog>

    <InventoryItemPicker v-model:model-value="pickerVisible" :items="itemOptions" @select="onPickerSelect" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue"
import { Search, Plus, Document, Goods, Delete } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { get, post } from "@/utils/request"
import InventoryItemPicker from "./components/InventoryItemPicker.vue"

const filterType = ref("")
const dateRange = ref(null)
const searchKey = ref("")
const list = ref([])
const loading = ref(false)
const pagination = reactive({ page:1, per_page:15, total:0 })
const itemOptions = ref([])
const warehouseOptions = ref([])
const supplierOptions = ref([])
const projectOptions = ref([])

function formatDate(s) {
  if (!s) return "-"
  const d = new Date(s); if (isNaN(d.getTime())) return s
  const pad = n=>n.toString().padStart(2,"0")
  return d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate())+" "+pad(d.getHours())+":"+pad(d.getMinutes())
}

const autoRecordNo = computed(() => {
  const d = new Date()
  const pad = n=>n.toString().padStart(2,"0")
  return "RK-"+d.getFullYear()+pad(d.getMonth()+1)+pad(d.getDate())+"-XXXX"
})

async function loadList(page=1) {
  pagination.page = page; loading.value = true
  try {
    const res = await get("/inventory/stock-records", { page, per_page:pagination.per_page })
    const d = res||{}
    let items = d.data||d.items||d||[]
    if (!filterType.value) items = items.filter(r=>["inbound","return"].includes(r.type))
    if (searchKey.value) {
      const kw = searchKey.value.toLowerCase()
      items = items.filter(r=>(r.record_no||"").toLowerCase().includes(kw)||(r.inventoryItem?.name||"").toLowerCase().includes(kw)||(r.inventoryItem?.code||"").toLowerCase().includes(kw)||(r.party?.name||"").toLowerCase().includes(kw))
    }
    if (dateRange.value) {
      const [from,to] = dateRange.value
      items = items.filter(r=>{const t=(r.created_at||"").slice(0,10); return t>=from&&t<=to})
    }
    list.value = items; pagination.total = items.length
  } catch(e) { console.error(e); list.value=[]; pagination.total=0 }
  finally { loading.value=false }
}

async function loadItems() {
  try { const res=await get("/inventory",{per_page:200}); itemOptions.value=res.data||res.items||res||[] }
  catch(e){ console.warn(e) }
}
async function loadWarehouses() {
  try { const res=await get("/inventory/warehouses"); warehouseOptions.value=res.data||res||[] }
  catch(e){ console.warn(e) }
}
async function loadSuppliers() {
  try {
    const res=await get("/projects/suppliers",{per_page:500}); const d=res||{}
    supplierOptions.value=d.data?.data||d.data?.items||d.data||d.items||d||[]
  } catch(e){ console.warn(e) }
}
async function loadProjects() {
  try {
    const res=await get("/projects",{per_page:500}); const d=res||{}
    projectOptions.value=d.data?.data||d.data?.items||d.data||d.items||d||[]
  } catch(e){ console.warn(e) }
}

const showFormDialog = ref(false)
const formRef = ref()
const submitting = ref(false)
const pickerVisible = ref(false)
const pickerIndex = ref(-1)

const form = reactive({
  type: "inbound",
  warehouse_id: null,
  party_type: "supplier",
  party_id: null,
  settle_id: null,
  project_id: null,
  remark: "",
  items: [],
})

const formRules = {
  warehouse_id: [{ required:true, message:"请选择仓库", trigger:"change" }],
  party_id: [{ required:true, message:"请选择往来单位", trigger:"change" }],
}

function onPartyChange(v) { if (!form.settle_id) form.settle_id = v }

function addItemRow() {
  form.items.push({ item: null, quantity: 1 })
}

function removeItemRow(idx) {
  form.items.splice(idx, 1)
}

function openPicker(idx) {
  pickerIndex.value = idx
  pickerVisible.value = true
}

function onPickerSelect(item) {
  const idx = pickerIndex.value
  if (idx >= 0 && idx < form.items.length) {
    form.items[idx].item = { ...item }
    form.items[idx].quantity = 1
  }
}

function handleCreate() {
  form.type = "inbound"
  form.warehouse_id = warehouseOptions.value[0]?.id||null
  form.party_id = null
  form.settle_id = null
  form.project_id = null
  form.remark = ""
  form.items = [{ item: null, quantity: 1 }]
  showFormDialog.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  const validItems = form.items.filter(i=>i.item)
  if (validItems.length === 0) { ElMessage.warning("请至少选择一种物料"); return }

  submitting.value = true
  let successCount = 0
  let lastRecordNo = ""
  try {
    for (const row of validItems) {
      const payload = {
        inventory_item_id: row.item.id,
        quantity: row.quantity,
        warehouse_id: form.warehouse_id,
        type: form.type,
        party_type: form.party_type,
        party_id: form.party_id,
        settle_id: form.settle_id||form.party_id,
        project_id: form.project_id,
        remark: form.remark,
      }
      const r = await post("/inventory/stock-in", payload)
      successCount++
      lastRecordNo = r?.data?.record_no||""
    }
    ElMessage.success("入库完成，共 "+successCount+" 项物料成功"+(lastRecordNo?"，单号："+lastRecordNo:""))
    showFormDialog.value = false
    loadList(pagination.page)
  } catch(e) {
    if (successCount > 0) {
      ElMessage.warning("已成功入库 "+successCount+" 项，部分失败")
    } else {
      ElMessage.error(e?.response?.data?.message||e.message||"入库失败")
    }
  } finally {
    submitting.value = false
  }
}

onMounted(()=>{ loadList(1); loadItems(); loadWarehouses(); loadSuppliers(); loadProjects() })
</script>

<style scoped>
.page-container { padding:20px; background:#f5f7fa; min-height:100vh }
.page-header { margin-bottom:16px }
.page-header h2 { font-size:20px; color:#0C447C; margin:0 }
.filter-bar { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:16px; padding:16px; background:#fff; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,.06) }
.content-card { background:#fff; border-radius:8px; padding:16px; box-shadow:0 1px 4px rgba(0,0,0,.06) }
.pagination-wrap { display:flex; justify-content:flex-end; margin-top:16px }
.muted { color:#c0c4cc }
.unit-text { color:#909399; font-size:12px }
.record-no { font-family:"DIN Pro",monospace; font-weight:500; color:#0C447C }
.section-card { background:#fff; border:1px solid #e8ecf1; border-radius:8px; padding:16px 16px 0 }
.section-title { font-size:14px; font-weight:600; color:#0C447C; margin-bottom:12px; padding-bottom:8px; border-bottom:2px solid #e6f1fb; display:flex; align-items:center; gap:6px }
.section-title .el-icon { font-size:16px }
.item-code { font-family:"DIN Pro",monospace; font-weight:500; color:#0C447C; font-size:12px }
:deep(.el-dialog__body) { padding-top:12px }
</style>