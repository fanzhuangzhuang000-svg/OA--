<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="`报价请求详情 - ${detail?.code || ''}`"
    width="1000px"
    destroy-on-close
  >
    <template v-if="detail">
      <el-descriptions :column="3" border>
        <el-descriptions-item label="编号">{{ detail.code }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag>{{ detail.status_label || detail.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="项目">{{ detail.project?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="截止时间">{{ detail.deadline || '-' }}</el-descriptions-item>
        <el-descriptions-item label="中标供应商">{{ detail.awardedSupplier?.name || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">需求清单</el-divider>
      <el-table :data="detail.required_items ?? []" border>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="spec" label="规格" />
        <el-table-column prop="qty" label="数量" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
      </el-table>

      <el-divider content-position="left">报价列表（{{ quotes.length }}）</el-divider>
      <el-table :data="quotes" border v-loading="loading">
        <el-table-column prop="supplier.name" label="供应商" width="180" />
        <el-table-column prop="code" label="报价单号" width="160" />
        <el-table-column prop="total_amount" label="总金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="lead_time_days" label="交付(天)" width="90" align="right" />
        <el-table-column prop="payment_terms" label="账期" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="quoteStatusType(row.status)" size="small">
              {{ quoteStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'submitted'" size="small" link type="primary" @click="$emit('shortlist', row)">入围</el-button>
            <el-button v-if="['submitted', 'shortlisted'].includes(row.status)" size="small" link type="success" @click="$emit('award', row)">中标</el-button>
            <el-button v-if="['submitted', 'shortlisted'].includes(row.status)" size="small" link type="danger" @click="$emit('reject', row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
    <el-skeleton v-else :rows="6" animated />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { externalQuote } from '@/api/external-quote'
import type { ExternalQuote, ExternalQuoteRequest } from '@/api/external-quote'

const props = defineProps<{ visible: boolean; detail: ExternalQuoteRequest | null }>()
defineEmits<{
  'update:visible': [v: boolean]
  shortlist: [row: ExternalQuote]
  award: [row: ExternalQuote]
  reject: [row: ExternalQuote]
}>()

const quotes = ref<ExternalQuote[]>([])
const loading = ref(false)

watch(
  () => props.detail,
  async (val) => {
    if (val?.id) {
      loading.value = true
      try {
        const res: any = await externalQuote.listQuotes(val.id)
        quotes.value = res?.data ?? []
      } finally {
        loading.value = false
      }
    } else {
      quotes.value = []
    }
  },
  { immediate: true },
)

const quoteStatusLabel = (s?: string) => ({ submitted: '已提交', shortlisted: '入围', awarded: '已中标', rejected: '已驳回' }[s ?? ''] ?? s ?? '-')
const quoteStatusType = (s?: string) => ({ submitted: 'info', shortlisted: 'warning', awarded: 'success', rejected: 'danger' }[s ?? ''] ?? '')
</script>
