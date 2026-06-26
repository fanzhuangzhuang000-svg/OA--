<template>
  <div class="page-container">
    <div class="page-header">
      <el-button :icon="ArrowLeft" plain @click="goBack">返回</el-button>
      <span class="page-title" style="margin-left: 16px">质保金详情</span>
    </div>

    <div v-loading="loading" v-if="detail">
      <el-card shadow="hover" style="margin-bottom: 16px">
        <template #header>
          <div style="display: flex; align-items: center; gap: 12px">
            <span style="font-size: 18px; font-weight: 600">质保金 #{{ detail.id }}</span>
            <el-tag :type="statusTagType(detail.status)" effect="plain">{{ statusLabel(detail.status) }}</el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="项目">{{ detail.project?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ detail.customer?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="质保期">{{ detail.warranty?.warranty_no || '-' }}</el-descriptions-item>
          <el-descriptions-item label="合同金额">¥ {{ formatAmount(detail.contract_amount) }}</el-descriptions-item>
          <el-descriptions-item label="质保金比例">{{ detail.deposit_rate }}%</el-descriptions-item>
          <el-descriptions-item label="质保金">¥ {{ formatAmount(detail.deposit_amount) }}</el-descriptions-item>
          <el-descriptions-item label="已释放">¥ {{ formatAmount(detail.released_amount) }}</el-descriptions-item>
          <el-descriptions-item label="已没收">¥ {{ formatAmount(detail.forfeited_amount) }}</el-descriptions-item>
          <el-descriptions-item label="余额">
            <strong :style="{ color: '#67C23A' }">¥ {{ formatAmount(balance(detail)) }}</strong>
          </el-descriptions-item>
          <el-descriptions-item label="留置日期">{{ detail.hold_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="预计释放">{{ detail.expected_release_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ detail.payment_method || '-' }}</el-descriptions-item>
          <el-descriptions-item label="银行账户" :span="3">{{ detail.bank_account || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">{{ detail.notes || detail.reason || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { warrantyDepositApi } from '@/api/warranty'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref<any>(null)

const id = computed(() => Number(route.params.id))

const statusLabel = (s: string) => ({ held: '留置中', partial_released: '部分释放', fully_released: '全部释放', forfeited: '已没收' } as any)[s] || s
const statusTagType = (s: string) => ({ held: 'info', partial_released: 'warning', fully_released: 'success', forfeited: 'danger' } as any)[s] || 'info'

const formatAmount = (v: any) => {
  const n = parseFloat(v) || 0
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
const balance = (row: any) =>
  (parseFloat(row.deposit_amount) || 0) - (parseFloat(row.released_amount) || 0) - (parseFloat(row.forfeited_amount) || 0)

async function loadDetail() {
  loading.value = true
  try {
    const res: any = await warrantyDepositApi.show(id.value)
    detail.value = res.data || res
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || 'unknown'))
  } finally {
    loading.value = false
  }
}

function goBack() { router.push('/project/warranty/deposit') }

onMounted(loadDetail)
</script>
