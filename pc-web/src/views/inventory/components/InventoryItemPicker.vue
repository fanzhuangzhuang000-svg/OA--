<template>
  <el-dialog :model-value="show" @update:model-value="(v) => { if(!v) emit('close'); }" title="选择物料" width="800px"
    :close-on-click-modal="false" top="5vh" append-to-body :destroy-on-close="false">
    <div class="picker-search" style="display:flex;gap:8px">
      <el-select v-model="categoryFilter" clearable placeholder="选择分类" style="width:200px" @change="onSearch">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input v-model="searchKey" placeholder="搜索物料名称 / 编码 / 规格"
        clearable :prefix-icon="SearchI" style="flex:1" @input="onSearch" />
    </div>
    <el-table v-loading="loading" :data="filteredItems" stripe border
      style="width:100%" max-height="420" highlight-current-row @row-click="onRowClick">
      <el-table-column type="index" label="#" width="48" />
      <el-table-column prop="code" label="编码" width="140">
        <template #default="{ row }"><span class="item-code">{{ row.code }}</span></template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="spec" label="规格" width="120" show-overflow-tooltip>
        <template #default="{ row }"><span v-if="row.spec">{{ row.spec }}</span><span v-else class="text-muted">-</span></template>
      </el-table-column>
      <el-table-column label="分类" width="120" show-overflow-tooltip>
        <template #default="{ row }"><span v-if="row.category">{{ row.category.name }}</span><span v-else class="text-muted">-</span></template>
      </el-table-column>
      <el-table-column label="当前库存" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="(row.current_stock??0)<=0?'danger':(row.current_stock??0)<10?'warning':'success'"
            size="small" effect="plain">{{ row.current_stock??0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="70" align="center" />
    </el-table>
    <template #footer>
      <el-button @click="emit('update:model-value', false)">取消</el-button>
      <el-button type="primary" :disabled="!selectedItem" @click="handleConfirm">确定选择</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { Search as SearchI } from "@element-plus/icons-vue"

const props = defineProps<{ show: boolean; items: any[] }>()
const emit = defineEmits<{ (e: "close"): void; (e: "select", item: any): void }>()

const searchKey = ref("")
const categoryFilter = ref<number|null>(null)
const loading = ref(false)
const selectedItem = ref<any>(null)

const categories = computed(() => {
  const map = new Map()
  for (const i of props.items) {
    if (i.category?.id) map.set(i.category.id, i.category)
  }
  return [...map.values()]
})

const filteredItems = computed(() => {
  const kw = searchKey.value.trim().toLowerCase()
  const catId = categoryFilter.value
  return props.items.filter(i => {
    if (catId && i.category?.id !== catId) return false
    if (!kw) return true
    return (i.name||"").toLowerCase().includes(kw) ||
      (i.code||"").toLowerCase().includes(kw) ||
      (i.spec||"").toLowerCase().includes(kw) ||
      (i.category?.name||"").toLowerCase().includes(kw)
  })
})

function onSearch() { selectedItem.value = null }
function onRowClick(row: any) { selectedItem.value = row }
function handleConfirm() {
  if (selectedItem.value) { emit("select", selectedItem.value); emit("close"); selectedItem.value = null; searchKey.value = ""; categoryFilter.value = null }
}
</script>

<style scoped>
.picker-search { margin-bottom:12px }
.item-code { font-family:"DIN Pro","Consolas",monospace; font-weight:500; color:#0C447C; font-size:12px }
.text-muted { color:#c0c4cc }
:deep(.el-table__row) { cursor:pointer }
:deep(.el-table__row.current-row) { background-color:#e6f1fb!important }
</style>