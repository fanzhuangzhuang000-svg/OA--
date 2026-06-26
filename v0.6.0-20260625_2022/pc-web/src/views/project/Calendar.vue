<template>
  <div class="page-container">
    <div class="page-header">
      <div class="title-area">
        <span class="page-title">合同付款日历</span>
        <el-tag effect="light" type="info">{{ calendar.length }} 个月</el-tag>
        <el-tag v-if="summary.overdue_count > 0" type="danger" effect="dark" size="small">{{ summary.overdue_count }} 个逾期</el-tag>
        <el-tag v-if="summary.soon_count > 0" type="warning" effect="dark" size="small">{{ summary.soon_count }} 个 7 天内到期</el-tag>
      </div>
      <div class="header-actions">
        <el-radio-group v-model="filterStatus" size="default" @change="loadList">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="pending">待付</el-radio-button>
          <el-radio-button value="paid">已付</el-radio-button>
          <el-radio-button value="overdue">逾期</el-radio-button>
        </el-radio-group>
        <el-button :icon="Refresh" @click="loadList">刷新</el-button>
        <el-button :icon="List" @click="$router.push('/project/list')">返回列表</el-button>
      </div>
    </div>

    <!-- 顶部汇总卡片 -->
    <div class="summary-row">
      <div class="summary-card" style="border-color: #0C447C">
        <div class="sum-label">合同节点总数</div>
        <div class="sum-value">{{ summary.total_count }}</div>
        <div class="sum-extra">总金额 ¥ {{ formatMoney(summary.total_amount) }}</div>
      </div>
      <div class="summary-card" style="border-color: #1D9E75">
        <div class="sum-label">已付款</div>
        <div class="sum-value" style="color: #1D9E75">¥ {{ formatMoney(summary.paid_amount) }}</div>
        <div class="sum-extra">回款率 {{ paymentRate }}%</div>
      </div>
      <div class="summary-card" style="border-color: #BA7517">
        <div class="sum-label">待付款</div>
        <div class="sum-value" style="color: #BA7517">¥ {{ formatMoney(summary.pending_amount) }}</div>
        <div class="sum-extra">{{ summary.total_count - summary.overdue_count - Math.floor(summary.paid_amount / (summary.total_amount || 1) * summary.total_count) }} 个待付节点</div>
      </div>
      <div class="summary-card" style="border-color: #A32D2D">
        <div class="sum-label">逾期</div>
        <div class="sum-value" style="color: #A32D2D">¥ {{ formatMoney(summary.overdue_amount) }}</div>
        <div class="sum-extra">{{ summary.overdue_count }} 个逾期节点</div>
      </div>
    </div>

    <div class="content-card">
      <el-empty v-if="!calendar.length" description="暂无付款节点" :image-size="80" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="month in calendar"
          :key="month.month"
          :timestamp="monthLabel(month.month)"
          placement="top"
          type="primary"
        >
          <el-card shadow="hover" class="month-card">
            <div class="month-header">
              <div>
                <span class="month-title">{{ monthLabel(month.month) }}</span>
                <el-tag size="small" type="info" effect="plain" style="margin-left: 8px">{{ month.count }} 个节点</el-tag>
              </div>
              <div class="month-amount">
                ¥ {{ formatMoney(month.total_amount) }}
                <span class="month-paid">已付 ¥{{ formatMoney(month.paid_amount) }}</span>
              </div>
            </div>
            <el-table :data="month.items" border size="default" :show-header="false">
              <el-table-column label="" width="40">
                <template #default="{ row }">
                  <el-icon :size="16" :color="statusColor(row)">
                    <component :is="statusIcon(row)" />
                  </el-icon>
                </template>
              </el-table-column>
              <el-table-column label="" min-width="200">
                <template #default="{ row }">
                  <div class="item-name">{{ row.name }}</div>
                  <div class="item-sub">
                    <span class="item-project" @click="goProject(row.project_id)">@{{ row.project_name || '-' }}</span>
                    <span class="item-customer">· {{ row.customer_name || '-' }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="" width="120" align="right">
                <template #default="{ row }">
                  <div class="item-amount">¥ {{ formatMoney(row.amount) }}</div>
                  <div v-if="row.paid_amount > 0" class="item-paid-amount">已付 ¥ {{ formatMoney(row.paid_amount) }}</div>
                </template>
              </el-table-column>
              <el-table-column label="" width="140" align="center">
                <template #default="{ row }">
                  <div class="item-date">{{ formatDate(row.planned_date) }}</div>
                  <div v-if="row.status === 'pending'" class="item-due" :class="dueClass(row)">
                    <template v-if="row.days_left !== null">
                      <template v-if="row.days_left < 0">已超 {{ -row.days_left }} 天</template>
                      <template v-else-if="row.days_left === 0">今天到期</template>
                      <template v-else>还有 {{ row.days_left }} 天</template>
                    </template>
                  </div>
                  <div v-else-if="row.actual_date" class="item-due">已于 {{ formatDate(row.actual_date) }} 付清</div>
                </template>
              </el-table-column>
              <el-table-column label="" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row)" size="small" effect="dark">{{ statusLabel(row) }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get } from '@/utils/request'
import { Refresh, List, CircleCheck, Clock, Warning, CircleClose, CirclePlus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const summary = ref<any>({ total_count: 0, total_amount: 0, paid_amount: 0, pending_amount: 0, overdue_count: 0, overdue_amount: 0, soon_count: 0 })
const calendar = ref<any[]>([])
const items = ref<any[]>([])
const filterStatus = ref<string>('')

const paymentRate = computed(() => {
  if (!summary.value.total_amount) return 0
  return ((summary.value.paid_amount / summary.value.total_amount) * 100).toFixed(1)
})

const loadList = async () => {
  try {
    const params: Record<string, any> = { per_page: 500 }
    if (filterStatus.value) params.status = filterStatus.value
    const r: any = await get('/projects/payment-calendar', params)
    const d = r?.data || r || {}
    summary.value = d.summary || summary.value
    calendar.value = d.by_month || []
    items.value = d.items || []
  } catch (e) {
    ElMessage.error('加载付款日历失败')
  }
}

const formatMoney = (n: number) => Number(n || 0).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
const formatDate = (d: string) => d ? d.slice(0, 10) : '-'
const monthLabel = (m: string) => {
  if (!m) return ''
  const [y, mm] = m.split('-')
  return `${y} 年 ${parseInt(mm)} 月`
}

const statusIcon = (row: any) => {
  if (row.status === 'paid') return CircleCheck
  if (row.is_overdue) return CircleClose
  if (row.is_soon) return Warning
  return Clock
}
const statusColor = (row: any) => {
  if (row.status === 'paid') return '#1D9E75'
  if (row.is_overdue) return '#A32D2D'
  if (row.is_soon) return '#BA7517'
  return '#909399'
}
const statusLabel = (row: any) => {
  if (row.status === 'paid') return '已付'
  if (row.is_overdue) return '逾期'
  if (row.is_soon) return '即将到期'
  return '待付'
}
const statusTagType = (row: any): any => {
  if (row.status === 'paid') return 'success'
  if (row.is_overdue) return 'danger'
  if (row.is_soon) return 'warning'
  return 'info'
}
const dueClass = (row: any) => {
  if (row.is_overdue) return 'overdue'
  if (row.is_soon) return 'soon'
  return ''
}
const goProject = (pid: number) => { if (pid) router.push(`/project/detail/${pid}`) }

onMounted(() => {
  loadList()
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 16px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 14px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .title-area { display: flex; align-items: center; gap: 10px; }
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
  .header-actions { display: flex; gap: 8px; }
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}
.summary-card {
  background: #fff;
  border-left: 4px solid;
  border-radius: 6px;
  padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .sum-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
  .sum-value { font-size: 22px; font-weight: 700; color: #0C447C; }
  .sum-extra { font-size: 11px; color: #909399; margin-top: 2px; }
}

.content-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.month-card {
  margin-bottom: 8px;
  .month-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    .month-title { font-size: 16px; font-weight: 600; color: #0C447C; }
    .month-amount { font-size: 16px; font-weight: 600; color: #0C447C; }
    .month-paid { font-size: 12px; color: #1D9E75; margin-left: 8px; font-weight: normal; }
  }
  :deep(.el-table) { border-radius: 4px; }
}

.item-name { font-size: 13px; font-weight: 500; color: #303133; }
.item-sub { font-size: 11px; color: #909399; margin-top: 2px; }
.item-project { color: #0C447C; cursor: pointer; &:hover { text-decoration: underline; } }
.item-customer { color: #909399; }
.item-amount { font-size: 13px; font-weight: 600; color: #303133; }
.item-paid-amount { font-size: 11px; color: #1D9E75; }
.item-date { font-size: 13px; color: #303133; }
.item-due { font-size: 11px; margin-top: 2px; &.overdue { color: #A32D2D; font-weight: 600; } &.soon { color: #BA7517; font-weight: 600; } }
</style>
