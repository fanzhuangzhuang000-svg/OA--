<template>
  <div class="page-container">
    <RiskBanner :summary="riskSummary" @jump="handleRiskJump" @viewAll="goAllProjects" />

    <StatCards :stats="stats" @jump="goPath" />

    <TempRoleWarning />

    <MaintenanceWidget />

    <!-- V0.5.7 块5 — Dashboard 多维度 widget (4 维度) -->
    <DashboardWidgets :days="90" />

    <QuickActions :actions="quickActions" @jump="goPath" />

    <el-row :gutter="16" class="main-content">
      <el-col :span="14">
        <ProjectProgressTable :projects="projectList" @viewAll="goAllProjects" />
      </el-col>
      <el-col :span="10">
        <TodoListCard :todos="todoList" @click="handleTodoClick" />
        <ServiceStatsCard :data="serviceStats" @viewAll="goServiceStats" />
      </el-col>
    </el-row>

    <el-row :gutter="16" class="bottom-content">
      <el-col :span="10">
        <AttendanceCard :data="todayAttendance" @viewAll="goAttendance" />
      </el-col>
      <el-col :span="14">
        <RevenueChart :data="revenueData" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
/**
 * Dashboard 首页 — v0.3.14 C1 拆分版
 * 7 个子组件:
 *  - RiskBanner.vue            风险预警横幅
 *  - StatCards.vue             4 张统计卡
 *  - QuickActions.vue          8 快捷入口
 *  - ProjectProgressTable.vue  项目进度表
 *  - TodoListCard.vue          待办卡
 *  - ServiceStatsCard.vue      工单统计
 *  - AttendanceCard.vue        今日考勤
 *  - RevenueChart.vue          营收趋势
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardData, getTodoList, getProjectProgress, getServiceStats, getRevenueTrend } from '@/api/dashboard'
import { get } from '@/utils/request'
import RiskBanner from './components/RiskBanner.vue'
import StatCards from './components/StatCards.vue'
import TempRoleWarning from './components/TempRoleWarning.vue'
import MaintenanceWidget from './components/MaintenanceWidget.vue'
import DashboardWidgets from './components/DashboardWidgets.vue'
import QuickActions from './components/QuickActions.vue'
import ProjectProgressTable from './components/ProjectProgressTable.vue'
import TodoListCard from './components/TodoListCard.vue'
import ServiceStatsCard from './components/ServiceStatsCard.vue'
import AttendanceCard from './components/AttendanceCard.vue'
import RevenueChart from './components/RevenueChart.vue'

const router = useRouter()

// 顶部统计
const stats = reactive([
  { label: '今日待办', value: '0', icon: 'Bell', color: '#D85A30', trend: 0, path: '/message/list' },
  { label: '进行中项目', value: '0', icon: 'Files', color: '#185FA5', trend: 0, path: '/project/list' },
  { label: '待处理工单', value: '0', icon: 'SetUp', color: '#A32D2D', trend: 0, path: '/service/orders' },
  { label: '本月营收', value: '¥0', icon: 'Money', color: '#1D9E75', trend: 0, path: '/finance/overview' },
])

const quickActions = [
  { label: '签到打卡', icon: 'Location', path: '/attendance/overview', bg: '#E6F1FB', color: '#185FA5' },
  { label: '新建项目', icon: 'FolderAdd', path: '/project/create', bg: '#E1F5EE', color: '#1D9E75' },
  { label: '报修工单', icon: 'SetUp', path: '/service/create', bg: '#FCEBEB', color: '#A32D2D' },
  { label: '费用报销', icon: 'Money', path: '/expense/apply', bg: '#FAEEDA', color: '#BA7517' },
  { label: '用车申请', icon: 'Van', path: '/vehicle/apply', bg: '#EEEDFE', color: '#534AB7' },
  { label: '公司网盘', icon: 'FolderOpened', path: '/disk', bg: '#FAECE7', color: '#D85A30' },
  { label: '员工管理', icon: 'User', path: '/employee/list', bg: '#E6F1FB', color: '#0C447C' },
  { label: '客户管理', icon: 'OfficeBuilding', path: '/customer/list', bg: '#E1F5EE', color: '#1D9E75' },
]

// 风险预警
const riskSummary = ref({
  total: 0,
  danger: 0,
  warning: 0,
  projects: new Set<number>(),
  preview: [] as Array<{ projectId: number; projectName: string; title: string; level: string; id: string; idx: number }>,
})

const projectList = ref<any[]>([])
const todoList = ref<any[]>([])
const revenueData = ref<any[]>([])

const todayAttendance = reactive({
  normal: 0, late: 0, absent: 0, field: 0, leave: 0,
})

const serviceStats = reactive({
  todayNew: 0, processing: 0, todayDone: 0, monthDone: 0,
})

async function loadDashboard() {
  try {
    const r1: any = await getDashboardData()
    if (r1 && r1.code === 0 && r1.data) {
      const d = r1.data
      stats[0].value = String(d.pendingTodos ?? d.today_todos ?? 0)
      stats[1].value = String(d.activeProjects ?? d.active_projects ?? 0)
      stats[2].value = String(d.pendingServiceOrders ?? d.pending_service_orders ?? 0)
      stats[3].value = '¥' + (d.monthlyRevenue ?? d.monthly_revenue ?? 0)
      if (typeof d.todayAttendance === 'number') {
        todayAttendance.normal = d.todayAttendance
      } else if (d.todayAttendance && typeof d.todayAttendance === 'object') {
        Object.assign(todayAttendance, d.todayAttendance)
      }
    }
  } catch (e) { /* ignore */ }

  try {
    const r2: any = await getProjectProgress()
    if (r2 && r2.code === 0 && Array.isArray(r2.data)) {
      projectList.value = r2.data.map((s: any, i: number) => ({
        id: i,
        name: `${s.label}阶段项目`,
        stage: s.label,
        progress: s.pct ?? 0,
        manager: '—',
        deadline: '',
      }))
    }
  } catch (e) { /* ignore */ }

  try {
    const r3: any = await getTodoList()
    if (r3 && r3.code === 0 && Array.isArray(r3.data)) {
      todoList.value = r3.data.map((t: any, i: number) => ({
        id: i,
        type: t.label,
        content: `${t.count} 项待处理`,
        time: '尽快处理',
        tagType: i % 3 === 0 ? 'danger' : (i % 3 === 1 ? 'warning' : 'info'),
        link: '',
      }))
    }
  } catch (e) { /* ignore */ }

  try {
    const r4: any = await getServiceStats()
    if (r4 && r4.code === 0 && r4.data) {
      serviceStats.todayNew = r4.data.todayNew ?? r4.data.today_new ?? 0
      serviceStats.processing = r4.data.processing ?? 0
      serviceStats.todayDone = r4.data.todayDone ?? r4.data.today_done ?? 0
      serviceStats.monthDone = r4.data.monthDone ?? r4.data.month_done ?? 0
    }
  } catch (e) { /* ignore */ }

  try {
    const r5: any = await getRevenueTrend()
    if (r5 && r5.code === 0 && Array.isArray(r5.data)) {
      revenueData.value = r5.data.map((r: any) => ({
        month: r.month,
        contract: r.height ?? 0,
        payment: Math.round((r.height ?? 0) * 0.65),
      }))
    }
  } catch (e) { /* ignore */ }

  await loadRiskSummary()
}

async function loadRiskSummary() {
  try {
    const r: any = await get('/projects', { per_page: 6 })
    const items = r?.data?.data || r?.data || []
    const summaries: any[] = []
    const projects = new Set<number>()
    for (const p of items) {
      try {
        const tr: any = await get(`/projects/${p.id}/tracking`)
        const td = tr?.data || tr || {}
        const risks = Array.isArray(td.risks) ? td.risks : []
        for (const rk of risks) {
          projects.add(p.id)
          summaries.push({
            projectId: p.id,
            projectName: p.name?.slice(0, 16) || `项目${p.id}`,
            title: rk.title,
            level: rk.level,
            id: rk.type,
            idx: `${p.id}-${rk.type}`,
          })
        }
      } catch (e) { /* ignore single project error */ }
    }
    summaries.sort((a, b) => (b.level === 'danger' ? 1 : 0) - (a.level === 'danger' ? 1 : 0))
    riskSummary.value = {
      total: summaries.length,
      danger: summaries.filter((s) => s.level === 'danger').length,
      warning: summaries.filter((s) => s.level === 'warning').length,
      projects,
      preview: summaries.slice(0, 6),
    }
  } catch (e) { /* ignore */ }
}

// === 跳转处理 ===
const goPath = (path: string) => router.push(path)
const goAllProjects = () => router.push('/project/list')
const goServiceStats = () => router.push('/service/stats')
const goAttendance = () => router.push('/attendance/overview')

const handleRiskJump = (payload: { projectId: number; riskId: string }) => {
  router.push({ path: `/project/detail/${payload.projectId}` })
}

const handleTodoClick = (todo: { link?: string }) => {
  if (todo.link) router.push(todo.link)
}

import { onMounted } from 'vue'
onMounted(() => { loadDashboard() })
</script>

<style lang="scss" scoped>
.main-content, .bottom-content { margin-bottom: 16px; }
.service-stats-card { margin-top: 16px; }
.todo-card { margin-bottom: 16px; }

/* ============================================================
   Dashboard UI Refresh v1.0.1
============================================================ */
.page-container {
  padding: 20px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f5f7fa;
  min-height: 100%;
}
.page-container :deep(.el-card) {
  border-radius: 8px;
  border: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.page-container :deep(.el-card__header) {
  padding: 0 20px;
  min-height: 48px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f0f2f5;
}
.page-container :deep(.el-card__body) {
  padding: 16px 20px;
}
</style>
