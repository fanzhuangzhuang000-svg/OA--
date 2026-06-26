<template>
  <div class="inventory-container">
    <InventoryWarningBanner
      :low-stock="warnings.low_stock"
      :expiring="warnings.expiring"
      @click="handleWarningClick"
    />

    <InventoryToolbar
      v-model="searchKey"
      @search="onSearch"
      @import="showBatchImport = true"
      @export="handleBatchExport"
      @create="handleCreateItem"
    />

    <InventoryBatchBar
      :count="selectedIds.length"
      @edit="handleBatchEdit"
      @set-active="handleBatchSetActive"
      @set-inactive="handleBatchSetInactive"
      @delete="handleBatchDelete"
      @clear="clearSelection"
    />

    <div class="inventory-body">
      <div class="inventory-body__tree">
        <CategoryTree
          v-model="currentCategoryId"
          @refresh="onTreeRefresh"
        />
      </div>
      <div class="inventory-body__table">
        <ItemTable
          :list="itemList"
          :total="itemTotal"
          :page="itemPage"
          :per-page="itemPerPage"
          :loading="itemLoading"
          :warehouse-options="warehouseOptions"
          :current-category="currentCategoryId"
          :selected-ids="selectedIds"
          @search="onItemSearch"
          @page-change="onItemPageChange"
          @size-change="onItemSizeChange"
          @detail="showItemDetail"
          @edit="handleEditItem"
          @delete="handleDeleteItem"
          @stock-in="handleStockIn"
          @stock-out="handleStockOut"
          @selection-change="onSelectionChange"
        />
      </div>
    </div>

    <ItemDrawer
      v-model:visible="drawerVisible"
      :item="currentItem"
      @edit="handleEditItem"
    />

    <ItemFormDrawer
      v-model:visible="formDrawerVisible"
      :item="formEditingItem"
      @success="handleFormSuccess"
    />

    <BatchImportDialog
      v-model:visible="showBatchImport"
      @success="handleImportSuccess"
    />

    <InventoryBatchEditDialog
      v-model:visible="batchEditVisible"
      :submitting="batchEditSubmitting"
      :warehouse-options="warehouseOptions"
      :category-options="categoryOptionsForEdit"
      :selected-count="selectedIds.length"
      @submit="submitBatchEdit"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * Inventory 主页 — v0.3.14 C4 拆分版
 *
 * 新增/抽离子组件:
 *  - InventoryWarningBanner.vue    预警横幅
 *  - InventoryToolbar.vue         顶部工具条
 *  - InventoryBatchBar.vue        批量操作浮动栏
 *  - InventoryBatchEditDialog.vue 批量编辑字段 dialog
 *
 * 既有组件:
 *  - CategoryTree / ItemTable / ItemDrawer / ItemFormDrawer / BatchImportDialog
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { inventory } from '@/api/modules'
import { exportExcelLike } from '@/utils/exporter'
import CategoryTree from './components/CategoryTree.vue'
import ItemTable from './components/ItemTable.vue'
import ItemDrawer from './components/ItemDrawer.vue'
import ItemFormDrawer from './components/ItemFormDrawer.vue'
import BatchImportDialog from './components/BatchImportDialog.vue'
import InventoryWarningBanner from './components/InventoryWarningBanner.vue'
import InventoryToolbar from './components/InventoryToolbar.vue'
import InventoryBatchBar from './components/InventoryBatchBar.vue'
import InventoryBatchEditDialog from './components/InventoryBatchEditDialog.vue'

const router = useRouter()

const currentCategoryId = ref<number | null>(null)
const searchKey = ref('')

const warnings = reactive({ total: 0, low_stock: 0, expiring: 0 })

const itemList = ref<any[]>([])
const itemTotal = ref(0)
const itemPage = ref(1)
const itemPerPage = ref(15)
const itemLoading = ref(false)
const lastSearch = ref<{ keyword: string; warehouse_id: number | null; status: string; sort: string; order: string }>({
  keyword: '', warehouse_id: null, status: '', sort: '', order: '',
})

const warehouseOptions = ref<any[]>([])
const categoryTree = ref<any[]>([])

const drawerVisible = ref(false)
const currentItem = ref<any>(null)

const formDrawerVisible = ref(false)
const formEditingItem = ref<any>(null)

const showBatchImport = ref(false)

const selectedIds = ref<number[]>([])
const batchEditVisible = ref(false)
const batchEditSubmitting = ref(false)
const categoryOptionsForEdit = computed(() => categoryTree.value)

async function loadWarnings() {
  try {
    const res: any = await inventory.warnings()
    const d = res || {}
    warnings.low_stock = Number(d.low_stock || d.data?.low_stock || 0)
    warnings.expiring = Number(d.expiring || d.data?.expiring || 0)
    warnings.total = warnings.low_stock + warnings.expiring
  } catch (e) { /* silent */ }
}

async function loadWarehouses() {
  try {
    const res: any = await inventory.warehouses()
    warehouseOptions.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) { /* silent */ }
}

async function loadCategoryTree() {
  try {
    const res: any = await inventory.treeWithCounts()
    categoryTree.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) { /* silent */ }
}

async function loadItems() {
  itemLoading.value = true
  try {
    const params: any = {
      page: itemPage.value,
      per_page: itemPerPage.value,
      ...lastSearch.value,
    }
    if (currentCategoryId.value) params.category_id = currentCategoryId.value
    if (lastSearch.value.keyword) {
      params.keyword = lastSearch.value.keyword
      params.search = lastSearch.value.keyword
    }
    const res: any = await inventory.itemsByCategory(params)
    const d = res || {}
    const listData = d.list?.data ?? d.data ?? []
    const total = d.list?.total ?? d.total ?? 0
    itemList.value = Array.isArray(listData) ? listData : []
    itemTotal.value = Number(total) || 0
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '加载物品失败')
    itemList.value = []
    itemTotal.value = 0
  } finally {
    itemLoading.value = false
  }
}

function onSearch() {
  itemPage.value = 1
  lastSearch.value.keyword = searchKey.value
  loadItems()
}

function onItemSearch(payload: { keyword: string; warehouse_id: number | null; status: string; sort: string; order: string }) {
  itemPage.value = 1
  lastSearch.value = payload
  if (payload.keyword !== searchKey.value) searchKey.value = payload.keyword
  loadItems()
}

function onItemPageChange(p: number) {
  itemPage.value = p
  loadItems()
}

function onItemSizeChange(s: number) {
  itemPage.value = 1
  itemPerPage.value = s
  loadItems()
}

function onTreeRefresh() {
  loadWarnings()
  loadItems()
}

function handleWarningClick() {
  ElMessage.info('请在列表中筛选库存状态查看详情')
}

function showItemDetail(row: any) {
  currentItem.value = row
  drawerVisible.value = true
}

function handleCreateItem() {
  formEditingItem.value = null
  formDrawerVisible.value = true
}

function handleEditItem(row: any) {
  currentItem.value = row
  drawerVisible.value = false
  formEditingItem.value = row
  formDrawerVisible.value = true
}

function handleFormSuccess() {
  loadItems()
  loadWarnings()
}

async function handleDeleteItem(row: any) {
  try {
    await ElMessageBox.confirm(`确认删除物品「${row.name}」?`, '删除确认', { type: 'error' })
    await inventory.deleteItem(row.id)
    ElMessage.success('已删除')
    loadItems()
    loadWarnings()
  } catch (e: any) {
    if (e === 'cancel' || e?.message === 'cancel') return
    ElMessage.error(e?.response?.data?.message || e?.message || '删除失败')
  }
}

function handleStockIn(row: any) {
  router.push({ path: '/inventory/inbound', query: { item_id: String(row.id) } })
}

function handleStockOut(row: any) {
  router.push({ path: '/inventory/outbound', query: { item_id: String(row.id) } })
}

function handleImportSuccess() {
  showBatchImport.value = false
  ElMessage.success('导入完成, 正在刷新列表')
  loadItems()
  loadWarnings()
}

onMounted(() => {
  loadWarnings()
  loadWarehouses()
  loadItems()
  loadCategoryTree()
})

function onSelectionChange(ids: number[]) {
  selectedIds.value = ids
}
function clearSelection() {
  selectedIds.value = []
}
function handleBatchEdit() {
  batchEditVisible.value = true
}

async function submitBatchEdit(fields: Record<string, any>) {
  if (Object.keys(fields).length === 0) {
    ElMessage.warning('请至少填写一个要修改的字段')
    return
  }
  batchEditSubmitting.value = true
  try {
    const res: any = await inventory.batchUpdate(selectedIds.value, fields)
    const cnt = res?.data?.updated_count ?? 0
    ElMessage.success(`已更新 ${cnt} 项`)
    batchEditVisible.value = false
    clearSelection()
    await loadItems()
    await loadCategoryTree()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '批量更新失败')
  } finally {
    batchEditSubmitting.value = false
  }
}

async function handleBatchSetActive() {
  await applyBatchField('status', 'active', '已启用')
}
async function handleBatchSetInactive() {
  await applyBatchField('status', 'inactive', '已禁用')
}

async function applyBatchField(field: string, value: any, successText: string) {
  if (!selectedIds.value.length) return
  try {
    const res: any = await inventory.batchUpdate(selectedIds.value, { [field]: value })
    const cnt = res?.data?.updated_count ?? 0
    ElMessage.success(`${successText} ${cnt} 项`)
    clearSelection()
    await loadItems()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '操作失败')
  }
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedIds.value.length} 项物料? 仅可删除"无库存+无流水"的物料, 其他会自动跳过。`,
      '批量删除确认',
      { type: 'error' },
    )
  } catch { return }
  try {
    const res: any = await inventory.batchDelete(selectedIds.value)
    const d = res?.data || {}
    ElMessage.success(`已删除 ${d.deleted_count ?? 0} 项, 跳过 ${d.skipped_count ?? 0} 项`)
    if (d.skipped?.length) console.warn('[batchDelete skipped]', d.skipped)
    clearSelection()
    await loadItems()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '批量删除失败')
  }
}

async function handleBatchExport() {
  try {
    const params: any = selectedIds.value.length > 0 ? { ids: selectedIds.value } : {
      keyword: lastSearch.value.keyword,
      warehouse_id: lastSearch.value.warehouse_id,
    }
    // 后端 batchExport 直接返 Blob, 透传给浏览器 (后端会负责 .xls 格式)
    const blob: any = await inventory.batchExport(params)
    const today = new Date().toISOString().slice(0, 10)
    const filename = selectedIds.value.length > 0
      ? `库存导出_选中${selectedIds.value.length}项_${today}.xls`
      : `库存导出_全部_${today}.xls`
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    ElMessage.success(selectedIds.value.length > 0
      ? `已导出 ${selectedIds.value.length} 项选中物料`
      : '已导出当前搜索结果')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '导出失败')
  }
}
</script>

<style lang="scss" scoped>
.inventory-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  background: #f5f7fa;
  gap: 16px;
  overflow: hidden;
}
.inventory-body {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 16px;
  overflow: hidden;
}
.inventory-body__tree {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  overflow: hidden;
}
.inventory-body__table {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
