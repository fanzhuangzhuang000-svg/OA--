// useProjectDetail — v0.3.12
// 父组件 + 5 个 tab 子组件共享的数据加载 + 状态管理 composable
import { ref, computed, watch } from 'vue'
import { get, post } from '@/utils/request'
import { processApi } from '@/api/modules'
import { ElMessage } from 'element-plus'
import type {
  Project, Tracking, ConstructionLog, ProcessInstance, ProcessInspection,
} from '../types'

/**
 * 把分页响应解包成数组
 * 后端: {code, data: {current_page, data, total}} → 拦截器解包后 res = {current_page, data, total}
 */
function extractList(res: any): any[] {
  if (!res) return []
  if (Array.isArray(res)) return res
  if (Array.isArray(res.data)) return res.data
  return []
}

const EMPTY_TRACKING: Tracking = {
  current_stage: '', current_stage_label: '', display_progress: 0, stage_progress: [],
  payment: { contract_amount: 0, paid_amount: 0, payment_rate: 0, overdue_count: 0, overdue_amount: 0, pending_count: 0, nodes: [] },
  purchase_stats: { total_orders: 0, completed_orders: 0, pending_orders: 0, total_amount: 0, total_items_qty: 0, total_received_qty: 0, fulfill_rate: 0 },
  material_stats: { issued_records: 0, issued_cost: 0 },
  risks: [], timeline: [],
}

export function useProjectDetail(projectId: () => number) {
  const loading = ref(false)
  const project = ref<Project>({} as Project)
  const tracking = ref<Tracking>(JSON.parse(JSON.stringify(EMPTY_TRACKING)))
  const constructionLogs = ref<ConstructionLog[]>([])
  const processInstances = ref<ProcessInstance[]>([])
  const processInspections = ref<ProcessInspection[]>([])
  const processLoading = ref(false)

  // 1) 项目基础信息
  const loadProject = async () => {
    loading.value = true
    try {
      const res: any = await get(`/projects/${projectId()}`)
      project.value = (res && (res.id || res.project_no)) ? res : (res?.data || res || {})
    } catch (e: any) {
      const msg = e?.response?.data?.message || e?.message || '加载项目失败'
      ElMessage.error(msg)
      project.value = {} as Project
    } finally {
      loading.value = false
    }
  }

  // 2) 项目跟踪数据（付款节点 / 风险 / 时间线 / 物料统计）
  const loadTracking = async () => {
    try {
      const res: any = await get(`/projects/${projectId()}/tracking`)
      const d = (res && (res.current_stage || res.project_id)) ? res : (res?.data || res || {})
      tracking.value = d && d.payment ? d : JSON.parse(JSON.stringify(EMPTY_TRACKING))
    } catch (e: any) {
      console.error('加载项目跟踪数据失败', e?.message || e)
    }
  }

  // 3) 施工日志
  const loadLogs = async () => {
    try {
      const res: any = await get(`/projects/${projectId()}/construction-logs`, { per_page: 50 })
      constructionLogs.value = extractList(res)
    } catch (e) { console.error('加载施工日志失败', e) }
  }

  // 4) 工序实例 + 验收记录
  const loadProcessData = async () => {
    if (!projectId()) return
    processLoading.value = true
    try {
      const [instRes, inspRes] = await Promise.all([
        processApi.instanceList({ project_id: projectId(), per_page: 50 }),
        processApi.inspectionList({ project_id: projectId(), per_page: 20 }),
      ])
      processInstances.value = extractList(instRes)
      processInspections.value = extractList(inspRes)
    } catch (e: any) {
      console.error('[loadProcessData]', e)
      processInstances.value = []
      processInspections.value = []
    } finally {
      processLoading.value = false
    }
  }

  // 5) 新增施工日志
  const addLog = async (logData: any) => {
    try {
      await post(`/projects/${projectId()}/construction-logs`, logData)
      ElMessage.success('施工日志已记录')
      await loadLogs()
      return true
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.message || e?.message || '记录失败')
      return false
    }
  }

  // 全量刷新 — 父组件挂载时一次拉完
  const loadAll = async () => {
    await Promise.all([
      loadProject(),
      loadTracking(),
      loadLogs(),
      loadProcessData(),
    ])
  }

  return {
    // 状态
    loading, project, tracking, constructionLogs, processInstances, processInspections, processLoading,
    // 方法
    loadProject, loadTracking, loadLogs, loadProcessData, addLog, loadAll,
  }
}
