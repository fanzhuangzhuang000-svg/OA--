<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="从产品库选择"
    width="900px"
    top="5vh"
    :close-on-click-modal="false"
  >
    <el-form inline class="picker-search">
      <el-form-item label="分类">
        <el-select v-model="filter.category_id" placeholder="全部分类" clearable style="width:180px" @change="loadProducts">
          <el-option v-for="c in productCategories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="搜索">
        <el-input v-model="filter.keyword" placeholder="编码/名称" clearable style="width:220px" @keyup.enter="loadProducts" />
      </el-form-item>
      <el-form-item>
        <el-button @click="resetFilter">重置</el-button>
        <el-button type="primary" @click="loadProducts">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table
      ref="pickerTable"
      :data="products"
      v-loading="loading"
      border
      max-height="450"
      @selection-change="(rows: any[]) => selection = rows"
    >
      <el-table-column type="selection" width="55" :selectable="(row: any) => !isPicked(row)" />
      <el-table-column prop="code" label="编码" width="120" />
      <el-table-column prop="name" label="产品名称" min-width="180" />
      <el-table-column prop="spec" label="规格" width="120" />
      <el-table-column prop="unit" label="单位" width="60" align="center" />
      <el-table-column label="参考售价" width="100" align="right">
        <template #default="{ row }">¥ {{ Number(row.sale_price || 0).toFixed(2) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      small
      layout="prev, pager, next, total"
      :total="total"
      :page-size="filter.per_page"
      v-model:current-page="filter.page"
      @current-change="loadProducts"
      style="margin-top:8px; justify-content: flex-end"
    />

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :disabled="!selection.length" @click="handleConfirm">
        加入 ({{ selection.length }})
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getSalesProducts, getSalesProductCategories } from '@/api/sales'

const props = defineProps<{
  visible: boolean
  existingItems: any[]   // 已存在的需求条目 (按 code/name 去重)
}>()
const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'pick', items: any[]): void
}>()

const products = ref<any[]>([])
const productCategories = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const selection = ref<any[]>([])

const filter = reactive({
  category_id: null as number | null,
  keyword: '',
  page: 1,
  per_page: 20,
})

const isPicked = (row: any) =>
  props.existingItems.some((i) => i.product_id === row.id || (i.code && i.code === row.code))

const loadProducts = async () => {
  loading.value = true
  try {
    const r: any = await getSalesProducts({
      page: filter.page,
      per_page: filter.per_page,
      category_id: filter.category_id || undefined,
      keyword: filter.keyword || undefined,
    })
    products.value = r?.data || []
    total.value = r?.total || 0
  } catch (e) {
    products.value = []
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filter.category_id = null
  filter.keyword = ''
  filter.page = 1
  loadProducts()
}

watch(
  () => props.visible,
  async (v) => {
    if (v) {
      selection.value = []
      filter.page = 1
      if (productCategories.value.length === 0) {
        try {
          const r: any = await getSalesProductCategories()
          productCategories.value = r?.data || []
        } catch (e) { /* ignore */ }
      }
      loadProducts()
    }
  },
  { immediate: true },
)

const handleConfirm = () => {
  if (!selection.value.length) return
  const newItems = selection.value.map((p) => ({
    product_id: p.id,
    code: p.code,
    name: p.name,
    spec: p.spec || '',
    qty: 1,
    unit: p.unit || '件',
    _source: 'product_picker',  // 标记来源, 方便删除
  }))
  emit('pick', newItems)
  emit('update:visible', false)
  ElMessage.success(`已加入 ${newItems.length} 个产品`)
}
</script>

<style scoped>
.picker-search { padding: 0 0 12px; }
</style>
