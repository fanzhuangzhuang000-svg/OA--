<template>
  <div class="page-container">
    <!-- 顶部标题 + 操作 -->
    <div class="page-header">
      <div class="title-area">
        <el-button :icon="ArrowLeft" text @click="$router.back()">返回项目列表</el-button>
        <span class="page-title">{{ project.name || '加载中...' }}</span>
        <el-tag :type="statusTagType(project.status)" effect="light">{{ statusLabel(project.status) }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button :icon="Edit" @click="$router.push('/project/create')">编辑</el-button>
        <el-button :icon="Share" @click="handleShare">分享</el-button>
        <el-button :icon="Printer" @click="handlePrint">打印</el-button>
        <el-button type="primary" :icon="Document" @click="handleGenReport">导出报告</el-button>
      </div>
    </div>

    <!-- 顶部 overview 卡（含风险 banner） -->
    <div class="overview-card">
      <div v-if="risks.length > 0" class="risk-banner">
        <div class="risk-banner-head">
          <el-icon :size="18" color="#A32D2D"><WarningFilled /></el-icon>
          <span class="risk-banner-title">项目风险预警</span>
          <el-tag type="danger" size="small" effect="dark">共 {{ risks.length }} 项</el-tag>
        </div>
        <div class="risk-banner-list">
          <div v-for="(r, i) in risks" :key="i" class="risk-item" :class="'risk-' + r.level">
            <el-icon :size="14" :color="r.level === 'danger' ? '#A32D2D' : '#BA7517'">
              <component :is="r.level === 'danger' ? CircleClose : WarningFilled" />
            </el-icon>
            <span class="risk-title">{{ r.title }}</span>
            <span class="risk-desc">{{ r.desc }}</span>
            <el-button
              :type="r.level === 'danger' ? 'danger' : 'warning'"
              size="small"
              plain
              style="margin-left: auto"
              @click="handleRiskAction(r)"
            >
              {{ riskActionLabel(r.type) }}
            </el-button>
          </div>
        </div>
      </div>

      <el-row :gutter="0">
        <el-col :span="6" class="overview-item">
          <div class="ov-label">项目编号</div>
          <div class="ov-value">{{ project.project_no || project.code || '-' }}</div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">所属客户</div>
          <div class="ov-value">{{ customerName }}</div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">合同金额</div>
          <div class="ov-value highlight">¥ {{ totalBudget }} 万</div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">已回款 ({{ paymentRate }}%)</div>
          <div class="ov-value" :style="{ color: paymentRate >= 50 ? '#1D9E75' : '#BA7517' }">
            ¥ {{ paidAmount }} 万
            <el-tag v-if="paymentOverdueCount > 0" type="danger" size="small" effect="dark" style="margin-left: 6px">
              {{ paymentOverdueCount }} 逾期
            </el-tag>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="0">
        <el-col :span="6" class="overview-item">
          <div class="ov-label">物料到位率</div>
          <div class="ov-value" :style="{ color: fulfillRate >= 80 ? '#1D9E75' : fulfillRate >= 50 ? '#BA7517' : '#A32D2D' }">
            {{ fulfillRate }}%
          </div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">当前阶段</div>
          <div class="ov-value">
            <el-tag :type="stageTagType(stageLabel)" effect="dark">{{ stageLabel }}</el-tag>
          </div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">项目经理</div>
          <div class="ov-value small">
            <el-avatar :size="24" style="background: #0C447C">{{ managerName.charAt(0) }}</el-avatar>
            {{ managerName }}
          </div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">团队人数</div>
          <div class="ov-value">{{ (project.members || []).length }} 人</div>
        </el-col>
      </el-row>
      <el-row :gutter="0">
        <el-col :span="6" class="overview-item">
          <div class="ov-label">计划工期</div>
          <div class="ov-value small">{{ formatDate(project.start_date) }} ~ {{ formatDate(project.end_date) }}</div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">完成进度</div>
          <div class="ov-value">
            <el-progress :percentage="displayProgress" :status="progressStatus" :stroke-width="12" />
          </div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">采购单</div>
          <div class="ov-value small">
            总 {{ tracking.purchase_stats.total_orders }} · 已完成 {{ tracking.purchase_stats.completed_orders }}
          </div>
        </el-col>
        <el-col :span="6" class="overview-item">
          <div class="ov-label">物料领用</div>
          <div class="ov-value small">{{ tracking.material_stats.issued_records || 0 }} 笔</div>
        </el-col>
      </el-row>
    </div>

    <!-- Tabs 内容 -->
    <div class="content-card">
      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="项目信息" name="basic">
          <BasicInfoTab
            :project="project"
            :paid-amount="paidAmount"
            :contract-no="contractNo"
          />
        </el-tab-pane>

        <el-tab-pane label="阶段流程" name="stage">
          <StageFlowTab
            :project="project"
            :tracking="tracking"
            :display-progress="displayProgress"
            :paid-amount="paidAmount"
            :manager-name="managerName"
            @preview="handleDeliverablePreview"
            @download="handleDeliverableDownload"
          />
        </el-tab-pane>

        <el-tab-pane label="施工日志" name="log">
          <ConstructionLogTab
            :logs="constructionLogs"
            @add="showAddLogDialog = true"
            @export="handleExportLogs"
            @view="handleViewLog"
          />
        </el-tab-pane>

        <el-tab-pane label="成本核算" name="cost">
          <CostTab
            :project="project"
            :material-stats="tracking.material_stats"
            :purchase-stats="tracking.purchase_stats"
            :total-contract="totalContract"
            :paid-amount="Number(paidAmount.replace(/,/g, '')) * 10000"
          />
        </el-tab-pane>

        <el-tab-pane label="工序验收" name="process">
          <ProcessTab
            :instances="processInstances"
            :inspections="processInspections"
            :process-loading="processLoading"
            :project-id="projectId"
            @open-instance="goProcessInstance"
            @refresh="loadProcessData"
          />
        </el-tab-pane>

        <el-tab-pane label="施工进度" name="construction-progress">
          <div class="construction-progress-tab">
            <el-empty
              v-if="processInstances.length === 0"
              :description="`该项目暂无工序数据, 可在「施工 → 工序实例」中维护`"
            >
              <el-button
                type="primary"
                :icon="Connection"
                @click="goConstructionProcessList"
              >前往「施工 → 工序实例」</el-button>
            </el-empty>

            <div v-else class="progress-quick">
              <el-alert
                title="工序属于现场施工管理, 详细操作已迁移到「施工」菜单"
                type="info"
                :closable="false"
                show-icon
                style="margin-bottom: 16px"
              />
              <!-- V0.4.9 A1: 真实甘特图 -->
              <MiniGantt :instances="processInstances" />

              <el-row :gutter="16" style="margin-top: 16px">
                <el-col :span="8">
                  <el-statistic title="工序实例总数" :value="processInstances.length" />
                </el-col>
                <el-col :span="8">
                  <el-statistic
                    title="已完成"
                    :value="processInstances.filter(i => i.status === 'completed' || i.status === 'accepted').length"
                    :value-style="{ color: '#1D9E75' }"
                  />
                </el-col>
                <el-col :span="8">
                  <el-statistic
                    title="进行中"
                    :value="processInstances.filter(i => i.status === 'in_progress' || i.status === 'pending').length"
                    :value-style="{ color: '#BA7517' }"
                  />
                </el-col>
              </el-row>
              <div class="progress-actions" style="margin-top: 24px">
                <el-button
                  type="primary"
                  :icon="Connection"
                  @click="goConstructionProcessList"
                >前往「施工 → 工序实例」</el-button>
                <el-button
                  :icon="View"
                  @click="goConstructionInspections"
                >查看验收记录</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- V0.4.8 C1: 跨页复用 Gantt.vue, 工序时间线嵌入项目详情 -->
        <el-tab-pane label="施工甘特图" name="gantt">
          <div class="gantt-tab">
            <div class="gantt-tab-header">
              <h3 style="margin: 0 0 16px 0">项目 #{{ projectId }} 工序时间线</h3>
              <el-alert
                title="甘特图数据来自工序实例, 跨项目看板见「施工 → 工序实例」"
                type="info"
                :closable="false"
                show-icon
                style="margin-bottom: 16px"
              />
              <ProjectGantt v-if="projectId" :id="Number(projectId)" mode="embedded" />
              <el-empty v-else description="项目 ID 缺失, 无法加载甘特图" />
            </div>
          </div>
        </el-tab-pane>

        <!-- V0.5.7 块1 — 售后记录 tab -->
        <el-tab-pane :label="`售后记录 (${(maintenanceData?.stats?.work_order_count || 0) + (maintenanceData?.stats?.repair_order_count || 0)})`" name="maintenance">
          <div v-if="maintenanceLoading" class="loading-state">加载中...</div>
          <div v-else>
            <!-- 阶段校验提示 -->
            <el-alert
              v-if="!maintenanceData?.can_create_maintenance?.allowed"
              :title="maintenanceData?.can_create_maintenance?.reason"
              type="warning"
              :closable="false"
              show-icon
              style="margin-bottom: 16px"
            />
            <!-- 4 个统计卡 -->
            <div class="m-stats">
              <div class="m-stat">
                <div class="m-num">{{ maintenanceData?.stats?.work_order_count || 0 }}</div>
                <div class="m-label">维修工单</div>
              </div>
              <div class="m-stat">
                <div class="m-num">{{ maintenanceData?.stats?.repair_order_count || 0 }}</div>
                <div class="m-label">返修单</div>
              </div>
              <div class="m-stat">
                <div class="m-num">{{ maintenanceData?.stats?.in_repair_count || 0 }}</div>
                <div class="m-label">在修中</div>
              </div>
              <div class="m-stat">
                <div class="m-num">¥{{ (maintenanceData?.stats?.total_cost || 0).toFixed(0) }}</div>
                <div class="m-label">售后总成本</div>
              </div>
            </div>

            <!-- 操作按钮 (受阶段限制) -->
            <div class="m-actions">
              <el-button
                :disabled="!maintenanceData?.can_create_maintenance?.allowed"
                type="primary"
                :icon="Plus"
                @click="goCreateWorkOrder"
              >
                新建维修工单
              </el-button>
              <el-button
                :disabled="!maintenanceData?.can_create_maintenance?.allowed"
                :icon="Box"
                @click="goCreateRepair"
              >
                新建返修单
              </el-button>
              <el-tag v-if="!maintenanceData?.can_create_maintenance?.allowed" type="info" size="small">
                需进入「结算/质保」阶段
              </el-tag>
            </div>

            <!-- 列表 -->
            <div v-if="!maintenanceData?.items?.length" class="m-empty">
              暂无售后记录
            </div>
            <div v-else class="m-list">
              <div v-for="item in maintenanceData.items" :key="`${item.type}-${item.id}`" class="m-card" @click="goMaintenanceItem(item)">
                <div class="m-card-top">
                  <span class="m-code">{{ item.code }}</span>
                  <el-tag v-if="item.type === 'work_order'" size="small" type="primary">工单</el-tag>
                  <el-tag v-else size="small" type="warning">返修</el-tag>
                  <el-tag v-if="item.source_type === 'work_order'" size="small" effect="plain" type="info">
                    来自 {{ item.source_code }}
                  </el-tag>
                </div>
                <div class="m-fault">{{ item.fault_description }}</div>
                <div class="m-foot">
                  <el-tag :type="STATUS_TAG[item.status]?.type || 'info'" size="small">
                    {{ STATUS_TAG[item.status]?.label || item.status }}
                  </el-tag>
                  <span v-if="item.method_type" class="m-method">{{ METHOD_LABEL[item.method_type] || item.method_type }}</span>
                  <span class="m-time">{{ formatDate(item.created_at || item.updated_at || item.received_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 施工日志添加 dialog -->
    <AddLogDialog
      v-model:visible="showAddLogDialog"
      :form="addLogForm"
      :submitting="addLogSubmitting"
      @submit="handleAddLog"
    />

    <!-- 施工日志详情 dialog -->
    <LogDetailDialog v-model:visible="showLogDetailDialog" :log="currentLog" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get } from '@/utils/request'
import { printTable, printHtml, exportExcelLike } from '@/utils/exporter'
import {
  ArrowLeft, Edit, Share, Printer, Document,
  WarningFilled, CircleClose,
  Connection, View, Plus, Box,
} from '@element-plus/icons-vue'
import BasicInfoTab from './components/BasicInfoTab.vue'
import StageFlowTab from './components/StageFlowTab.vue'
import ConstructionLogTab from './components/ConstructionLogTab.vue'
import CostTab from './components/CostTab.vue'
import ProcessTab from './components/ProcessTab.vue'
import MiniGantt from '@/components/MiniGantt.vue'
import ProjectGantt from './Gantt.vue'
import AddLogDialog from './components/detail/AddLogDialog.vue'
import LogDetailDialog from './components/detail/LogDetailDialog.vue'
import { useProjectDetail } from '@/composables/useProjectDetail'
import {
  type TagType, type Risk,
  getCustomerName, getManagerName, computeTotalBudgetWan,
  STAGE_LABEL_MAP, statusLabel, typeLabel, formatDate,
  RISK_ACTION_MAP, riskActionLabel,
} from './types'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.id))

const activeTab = ref('stage')
const showAddLogDialog = ref(false)
const showLogDetailDialog = ref(false)
const addLogSubmitting = ref(false)
const currentLog = ref<any>(null)
const contractNo = ref('-')

const addLogForm = reactive({
  date: new Date().toISOString().slice(0, 10),
  weather: '晴',
  content: '',
  work_hours: 8,
  problems: '',
})

const {
  loading, project, tracking, constructionLogs,
  processInstances, processInspections, processLoading,
  loadProject, loadTracking, loadLogs, loadProcessData, addLog,
} = useProjectDetail(() => projectId.value)

// ============== 计算属性 ==============
const customerName = computed(() => getCustomerName(project.value))
const managerName = computed(() => getManagerName(project.value))
const totalBudget = computed(() => computeTotalBudgetWan(project.value))
const paidAmount = computed(() => (Number(tracking.value.payment?.paid_amount) / 10000 || 0).toFixed(2))
const paymentRate = computed(() => Number(tracking.value.payment?.payment_rate) || 0)
const paymentOverdueCount = computed(() => Number(tracking.value.payment?.overdue_count) || 0)
const displayProgress = computed(() => Number(tracking.value.display_progress) || Number(project.value.progress) || 0)
const totalContract = computed(() => Number(tracking.value.payment?.contract_amount) || 0)
const fulfillRate = computed(() => Number(tracking.value.purchase_stats?.fulfill_rate) || 0)
const risks = computed(() => tracking.value.risks || [])
const stageLabel = computed(() => STAGE_LABEL_MAP[project.value.stage || ''] || project.value.stage || '-')

const progressStatus = computed((): 'success' | 'warning' | 'exception' => {
  if (project.value.status === 'completed') return 'success'
  if (project.value.status === 'suspended') return 'exception'
  if (displayProgress.value >= 80) return 'success'
  if (displayProgress.value >= 50) return 'warning'
  return 'success'
})

const statusTagType = (s?: string): TagType => {
  if (s === 'completed') return 'success'
  if (s === 'in_progress') return 'warning'
  if (s === 'suspended') return 'danger'
  return 'info'
}

const stageTagType = (s?: string): TagType => {
  const map: Record<string, TagType> = {
    立项: 'primary', 询价: 'info', 合同: 'warning', 采购: 'warning',
    施工: 'danger', 结算: 'success', 质保: 'success',
  }
  return map[s || ''] || 'info'
}

// ============== 行为 ==============
const handleAddLog = async () => {
  addLogSubmitting.value = true
  try {
    const ok = await addLog(addLogForm)
    if (ok) {
      showAddLogDialog.value = false
      // 重置表单
      addLogForm.content = ''
      addLogForm.problems = ''
      addLogForm.work_hours = 8
    }
  } finally {
    addLogSubmitting.value = false
  }
}

const handleViewLog = (row: any) => {
  currentLog.value = row
  showLogDetailDialog.value = true
}

const handleRiskAction = (risk: Risk) => {
  const m = RISK_ACTION_MAP[risk.type] || { tab: 'stage', msg: '请查看详情' }
  ElMessage.warning(m.msg)
  activeTab.value = m.tab
}

const handleDeliverableDownload = (row: any) => {
  // 模拟下载: 走通用下载通道
  if (row.url || row.file_url) {
    const a = document.createElement('a')
    a.href = row.url || row.file_url
    a.download = row.name || 'download'
    a.click()
  } else {
    ElMessage.info(`交付物「${row.name}」暂未上传文件`)
  }
}
const handleDeliverablePreview = (row: any) => ElMessage.info(`预览功能开发中：${row.name}`)
const handleExportLogs = () => {
  // 施工日志 tab 的日志
  const logs = (logList && logList.value && logList.value.length) ? logList.value : []
  if (logs.length === 0) {
    ElMessage.warning('暂无施工日志可导出')
    return
  }
  const headers = ['日期', '进度', '工时', '施工内容', '天气', '人员', '状态']
  const rows = logs.map((l: any) => [
    l.work_date || l.date || '-',
    (l.progress || 0) + '%',
    l.work_hours || 0,
    l.content || '-',
    l.weather || '-',
    l.workers || '-',
    l.status || '-',
  ])
  exportExcelLike(headers, rows, '施工日志', { title: '项目施工日志' })
}
const handlePrint = () => {
  // 整页打印: 走打印通道, 先隐藏不需要的元素
  const css = document.createElement('style')
  css.id = '__print_hide__'
  css.textContent = `
    @page { size: A4 portrait; margin: 1.5cm; }
    body { background: #fff !important; }
    .el-header, .el-aside, .sidebar, .nav, .page-actions, .toolbar, .no-print, .el-tabs__nav-wrap, .el-tabs__header { display: none !important; }
  `
  document.head.appendChild(css)
  window.print()
  setTimeout(() => css.remove(), 500)
}
const handleShare = async () => {
  if (!project.value) {
    ElMessage.warning('项目未加载')
    return
  }
  const url = `${window.location.origin}/project/detail/${project.value.id}`
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('项目详情链接已复制到剪贴板')
  } catch {
    // 降级: 弹窗让用户手动复制
    ElMessageBox.prompt('复制以下链接', '分享项目', { inputValue: url, confirmButtonText: '关闭' })
      .catch(() => {})
  }
}
const goProcessInstance = (id: number | string) => {
  if (!id) {
    ElMessage.warning('缺少工序实例 ID')
    return
  }
  router.push(`/construction/process/instances/detail/${id}`)
}

// 跳转「施工 → 工序实例」并附带项目过滤
const goConstructionProcessList = () => {
  if (!projectId.value) {
    ElMessage.warning('项目 ID 缺失')
    return
  }
  router.push({
    path: '/construction/process/instances',
    query: { project_id: String(projectId.value) },
  })
}

// 跳转「施工 → 验收记录」
const goConstructionInspections = () => {
  if (!projectId.value) {
    ElMessage.warning('项目 ID 缺失')
    return
  }
  router.push({
    path: '/construction/process/inspections',
    query: { project_id: String(projectId.value) },
  })
}

// 导出项目跟踪报告 — 走 printTable (统一通道)
const handleGenReport = async () => {
  if (!project.value || !project.value.id) {
    ElMessage.warning('项目未加载完成')
    return
  }
  const p = project.value
  const headers = ['字段', '内容']
  const rows = [
    ['项目编号', p.code || '-'],
    ['项目名称', p.name || '-'],
    ['客户', p.customer?.name || '-'],
    ['项目类型', p.type || '-'],
    ['当前阶段', p.stage || '-'],
    ['项目进度', (p.progress || 0) + '%'],
    ['负责人', p.manager?.name || '-'],
    ['开始日期', p.start_date?.slice(0, 10) || '-'],
    ['截止日期', p.end_date?.slice(0, 10) || '-'],
    ['合同金额', p.contract_amount ? '¥' + Number(p.contract_amount).toFixed(2) : '-'],
    ['项目状态', p.status || '-'],
    ['项目描述', p.description || '-'],
  ]
  printTable(`项目跟踪报告 - ${p.name || p.code || ''}`, headers, rows, { orientation: 'portrait' })
}

onMounted(() => {
  loadProject()
  loadTracking()
  loadLogs()
  loadProcessData()
})

// V0.5.7 块1 — 售后 tab 数据
const maintenanceData = ref<any>(null)
const maintenanceLoading = ref(false)

const STATUS_TAG: Record<string, { type: string; label: string }> = {
  pending:    { type: 'info',    label: '待派单' },
  assigned:   { type: 'primary', label: '已派单' },
  in_progress:{ type: 'warning', label: '进行中' },
  resolved:   { type: 'success', label: '已解决' },
  cancelled:  { type: 'info',    label: '已取消' },
  converted_to_repair: { type: 'danger', label: '🔁 已转返修' },
  received:       { type: 'info',    label: '已接件' },
  sent_for_repair:{ type: 'primary', label: '寄修中' },
  in_repair:      { type: 'warning', label: '维修中' },
  repaired:       { type: 'success', label: '已修好' },
  sent_back:      { type: 'warning', label: '寄回中' },
  closed:         { type: 'success', label: '已关闭' },
}
const METHOD_LABEL: Record<string, string> = {
  free_warranty: '🆓 保内',
  free_contract: '🆓 合同',
  paid_repair:   '💰 付费维修',
  paid_replace:  '💰 付费换新',
  returned:      '↩️ 退回',
}

const loadMaintenance = async () => {
  if (!project.value?.id) return
  maintenanceLoading.value = true
  try {
    const res: any = await get(`/projects/${project.value.id}/maintenance`)
    maintenanceData.value = res.data
  } catch { maintenanceData.value = null }
  finally { maintenanceLoading.value = false }
}

const goCreateWorkOrder = () => {
  router.push({ path: '/maintenance/work-orders/create', query: { project_id: project.value?.id } })
}
const goCreateRepair = () => {
  router.push({ path: '/maintenance/repairs/create', query: { project_id: project.value?.id } })
}
const goMaintenanceItem = (item: any) => {
  if (item.type === 'work_order') router.push(`/maintenance/work-orders/${item.id}`)
  else router.push(`/maintenance/repairs/${item.id}`)
}
const formatDate = (s?: string) => {
  if (!s) return ''
  const d = new Date(s)
  return `${d.getMonth() + 1}-${d.getDate()}`
}

// 监听 activeTab 变化, 切到 maintenance 时才加载
watch(activeTab, (v) => {
  if (v === 'maintenance' && !maintenanceData.value) loadMaintenance()
})
</script>

<style lang="scss" scoped>
/* V0.5.7 块1 — 售后 tab 样式 */
.m-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.m-stat { background: #fff; padding: 16px; border-radius: 6px; text-align: center; border-top: 3px solid #409EFF; }
.m-stat:nth-child(2) { border-top-color: #E6A23C; }
.m-stat:nth-child(3) { border-top-color: #F56C6C; }
.m-stat:nth-child(4) { border-top-color: #67C23A; }
.m-num { font-size: 22px; font-weight: 700; }
.m-label { font-size: 12px; color: #909399; margin-top: 4px; }
.m-actions { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.m-empty { padding: 60px; text-align: center; color: #C0C4CC; font-size: 13px; background: #fff; border-radius: 6px; }
.m-list { display: flex; flex-direction: column; gap: 8px; }
.m-card { background: #fff; padding: 12px 16px; border-radius: 6px; cursor: pointer; transition: all 0.15s; border-left: 3px solid transparent; }
.m-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left-color: #409EFF; transform: translateX(2px); }
.m-card-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.m-code { font-size: 12px; color: #409EFF; font-family: monospace; font-weight: 500; }
.m-fault { font-size: 13px; color: #303133; line-height: 1.4; margin-bottom: 6px; }
.m-foot { display: flex; align-items: center; gap: 12px; font-size: 11px; color: #909399; }
.m-method { color: #E6A23C; }
.m-time { margin-left: auto; }
.loading-state { padding: 60px; text-align: center; color: #909399; }
@media (max-width: 768px) { .m-stats { grid-template-columns: repeat(2, 1fr); } }
</style>
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
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.title-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}
.header-actions {
  display: flex;
  gap: 8px;
}

.overview-card {
  background: #fff;
  border-radius: 8px;
  padding: 0 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  margin-bottom: 12px;
  overflow: hidden;
}

.overview-item {
  padding: 16px 8px;
  border-bottom: 1px solid #f0f0f0;
}

.ov-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.ov-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ov-value.small {
  font-size: 14px;
  font-weight: 500;
}
.ov-value.highlight {
  color: #0C447C;
  font-size: 20px;
}

.risk-banner {
  background: linear-gradient(90deg, #fdecec 0%, #fff5e6 100%);
  border-left: 4px solid #A32D2D;
  padding: 12px 16px;
  margin: 0 -20px 8px -20px;
  border-bottom: 1px solid #f0d5d5;
}
.risk-banner-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.risk-banner-title {
  font-weight: 600;
  color: #A32D2D;
}
.risk-banner-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.risk-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(255,255,255,0.6);
  border-radius: 4px;
  font-size: 13px;
}
.risk-title {
  font-weight: 600;
  color: #303133;
}
.risk-desc {
  color: #606266;
  font-size: 12px;
}

.content-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.detail-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }
}
.construction-progress-tab {
  padding: 24px 0;
}
.progress-quick {
  max-width: 720px;
  margin: 0 auto;
}
.progress-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
