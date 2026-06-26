<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">对外报价看板</span>
      <div class="header-actions">
        <el-button :icon="Refresh" plain @click="loadList">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">新建报价请求</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input v-model="filter.keyword" placeholder="编号/标题" clearable style="width:240px" />
        </el-form-item>
        <el-form-item label="项目">
          <el-input v-model="filter.project_id" placeholder="项目ID" clearable style="width:140px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadList">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <QuoteKanban :data="list" @view="handleView" />

    <RequestFormDialog
      v-model:visible="showCreateDialog"
      @saved="loadList"
    />

    <QuoteDetailDialog
      v-model:visible="showDetailDialog"
      :detail="currentDetail"
      @shortlist="handleShortlist"
      @award="handleAward"
      @reject="handleReject"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { externalQuote } from '@/api/external-quote'
import type { ExternalQuote, ExternalQuoteRequest } from '@/api/external-quote'
import QuoteKanban from './components/QuoteKanban.vue'
import RequestFormDialog from './components/RequestFormDialog.vue'
import QuoteDetailDialog from './components/QuoteDetailDialog.vue'

const list = ref<ExternalQuoteRequest[]>([])
const filter = reactive({ keyword: '', project_id: '' })

const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentDetail = ref<ExternalQuoteRequest | null>(null)

const loadList = async () => {
  const res: any = await externalQuote.listRequests({
    keyword: filter.keyword || undefined,
    project_id: filter.project_id ? Number(filter.project_id) : undefined,
    per_page: 200,
  })
  list.value = res?.data?.items ?? []
}

const handleView = async (row: ExternalQuoteRequest) => {
  const res: any = await externalQuote.getRequest(row.id)
  currentDetail.value = res.data
  showDetailDialog.value = true
}

const handleShortlist = async (quote: ExternalQuote) => {
  try {
    await ElMessageBox.confirm(`确认将「${quote.supplier?.name}」的报价入围？`, '入围确认', { type: 'success' })
  } catch { return }
  await externalQuote.shortlist(quote.id)
  ElMessage.success('已入围')
  await refreshDetail()
  loadList()
}

const handleAward = async (quote: ExternalQuote) => {
  try {
    await ElMessageBox.confirm(
      `确认「${quote.supplier?.name}」中标 ¥${quote.total_amount}？定标后将自动生成采购单。`,
      '中标确认',
      { type: 'success', confirmButtonText: '确认定标', cancelButtonText: '取消' },
    )
  } catch { return }
  try {
    const res: any = await externalQuote.award(quote.id)
    const data = res.data ?? {}
    ElMessage.success(
      `定标成功！PO: ${data.po?.po_no || '-'} / Payable: ${data.payable?.ref_no || '-'}`,
    )
    await refreshDetail()
    loadList()
  } catch (e: any) {
    /* 拦截器已提示 */
  }
}

const handleReject = async (quote: ExternalQuote) => {
  let reason = ''
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回报价', {
      inputType: 'textarea',
      inputPlaceholder: '原因',
    })
    reason = value
  } catch { return }
  await externalQuote.reject(quote.id, reason)
  ElMessage.success('已驳回')
  await refreshDetail()
  loadList()
}

const refreshDetail = async () => {
  if (!currentDetail.value?.id) return
  const res: any = await externalQuote.getRequest(currentDetail.value.id)
  currentDetail.value = res.data
}

onMounted(loadList)
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
  .header-actions { display: flex; gap: 8px; }
}
.filter-bar { background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); }
</style>
