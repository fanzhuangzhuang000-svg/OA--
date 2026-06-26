<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    title="选择物料"
    width="800px"
    :close-on-click-modal="false"
    top="5vh"
  >
    <div style="display:flex;gap:8px;margin-bottom:12px">
      <el-select
        :model-value="categoryFilter"
        @update:model-value="(v: any) => emit('update:categoryFilter', v)"
        clearable placeholder="选择分类" style="width:200px"
      >
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input
        :model-value="searchKey"
        @update:model-value="(v: string) => emit('update:searchKey', v)"
        placeholder="搜索物料名称 / 编码 / 规格" clearable :prefix-icon="Search" style="flex:1"
      />
    </div>
    <el-table :data="filteredItems" stripe border style="width:100%" max-height="420" highlight-current-row @row-click="emit('rowClick', $event)">
      <el-table-column type="index" label="#" width="48" />
      <el-table-column prop="code" label="编码" width="140">
        <template #default="{row}"><span class="item-code">{{ row.code }}</span></template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
      <el-table-column label="规格" width="120" show-overflow-tooltip>
        <template #default="{row}"><span v-if="row.spec">{{ row.spec }}</span><span v-else class="text-muted">-</span></template>
      </el-table-column>
      <el-table-column label="分类" width="120" show-overflow-tooltip>
        <template #default="{row}"><span v-if="row.category">{{ row.category.name }}</span><span v-else class="text-muted">-</span></template>
      </el-table-column>
      <el-table-column label="当前库存" width="120" align="center">
        <template #default="{row}">
          <el-tag :type="(row.current_stock??0)<=0?'danger':(row.current_stock??0)<10?'warning':'success'" size="small" effect="plain">{{ row.current_stock??0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="70" align="center" />
    </el-table>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :disabled="!selectedItem" @click="emit('confirm')">确定选择</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'

defineProps<{
  visible: boolean
  categoryFilter: any
  categories: any[]
  searchKey: string
  filteredItems: any[]
  selectedItem: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'update:categoryFilter', v: any): void
  (e: 'update:searchKey', v: string): void
  (e: 'rowClick', evt: any): void
  (e: 'confirm'): void
}>()
</script>

<style lang="scss" scoped>
.item-code { font-family: monospace; color: #0C447C; }
.text-muted { color: #c0c4cc; }
</style>
