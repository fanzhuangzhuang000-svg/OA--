// Project detail shared types — v0.3.12
// 5 个 tab 子组件 + 父组件共用的类型与映射

export type TagType = 'primary' | 'success' | 'info' | 'warning' | 'danger'

export interface ProjectMember {
  id: number | string
  name?: string
  pivot?: { role?: string }
}

export interface Project {
  id: number | string
  project_no?: string
  code?: string
  name: string
  type?: string
  customer?: string | { name: string }
  customer_name?: string
  manager?: string | { name: string }
  address?: string
  location?: string
  amount?: number
  description?: string
  members?: ProjectMember[]
  start_date?: string
  end_date?: string
  actual_start?: string
  priority?: string | number
  status?: string
  stage?: string
  progress?: number
  // 预算 5 项（来自 tracking 接口）
  budget_device?: number
  budget_material?: number
  budget_labor?: number
  budget_outsource?: number
  budget_other?: number
  contract?: { contract_no?: string }
}

export interface PaymentNode {
  id: number | string
  name: string
  percentage: number
  amount: number
  planned_date?: string
  actual_date?: string
  status: 'paid' | 'pending' | 'overdue' | 'partial'
}

export interface PaymentSummary {
  contract_amount: number
  paid_amount: number
  payment_rate: number
  overdue_count: number
  overdue_amount: number
  pending_count: number
  nodes: PaymentNode[]
}

export interface PurchaseStats {
  total_orders: number
  completed_orders: number
  pending_orders: number
  total_amount: number
  total_items_qty: number
  total_received_qty: number
  fulfill_rate: number
}

export interface MaterialStats {
  issued_records: number
  issued_cost: number
}

export interface Risk {
  level: 'danger' | 'warning'
  type: string
  title: string
  desc: string
}

export interface TimelineEntry {
  stage: string
  action: string
  time: string
  content: string
  operator?: string
}

export interface Tracking {
  current_stage: string
  current_stage_index?: number
  current_stage_label: string
  display_progress: number
  stage_progress: any[]
  payment: PaymentSummary
  purchase_stats: PurchaseStats
  material_stats: MaterialStats
  risks: Risk[]
  timeline: TimelineEntry[]
}

export interface ConstructionLog {
  id: number | string
  date: string
  weather: string
  content: string
  work_hours: number
  problems?: string
  operator_name?: string
}

export interface ProcessInstance {
  id: number | string
  template_name?: string
  status?: string
  planned_start?: string
  planned_end?: string
  actual_start?: string
  actual_end?: string
  assignee_name?: string
}

export interface ProcessInspection {
  id: number | string
  process_instance_id: number | string
  inspector_name?: string
  inspected_at?: string
  result?: 'pass' | 'fail' | 'rectify'
  comment?: string
  defects?: string
  process_name?: string
}

// 字段适配器 helpers
export const getCustomerName = (p: Project): string => {
  if (!p) return '-'
  if (typeof p.customer === 'string') return p.customer
  return p.customer?.name || p.customer_name || '-'
}

export const getManagerName = (p: Project): string => {
  if (!p) return '-'
  if (typeof p.manager === 'string') return p.manager
  return p.manager?.name || '-'
}

export const computeTotalBudgetWan = (p: Project): string => {
  if (!p) return '0.00'
  const sum = (Number(p.budget_device) || 0) + (Number(p.budget_material) || 0) +
              (Number(p.budget_labor) || 0) + (Number(p.budget_outsource) || 0) +
              (Number(p.budget_other) || 0)
  if (sum > 0) return (sum / 10000).toFixed(2)
  return (Number(p.amount) || 0).toString()
}

export const computeTotalBudgetYuan = (p: Project): number => {
  if (!p) return 0
  return (Number(p.budget_device) || 0) + (Number(p.budget_material) || 0) +
         (Number(p.budget_labor) || 0) + (Number(p.budget_outsource) || 0) +
         (Number(p.budget_other) || 0)
}

// 阶段常量
export const STAGES = [
  { name: '立项', description: '项目立项与审批', key: 'initiation' },
  { name: '询价', description: '设备询价比价', key: 'inquiry' },
  { name: '合同', description: '合同签订', key: 'contract' },
  { name: '采购', description: '设备采购', key: 'purchase' },
  { name: '施工', description: '现场施工', key: 'construction' },
  { name: '结算', description: '项目结算', key: 'settlement' },
  { name: '质保', description: '质保期运维', key: 'warranty' },
] as const

export const STAGE_LABEL_MAP: Record<string, string> = {
  initiation: '立项', inquiry: '询价', contract: '合同', purchase: '采购',
  construction: '施工', settlement: '结算', warranty: '质保',
}

export const STAGE_INDEX_MAP: Record<string, number> = {
  initiation: 0, inquiry: 1, contract: 2, purchase: 3,
  construction: 4, settlement: 5, warranty: 6,
}

// 类型标签
export const TYPE_LABEL_MAP: Record<string, string> = {
  camera: '视频监控', access_control: '门禁', alarm: '报警', comprehensive: '综合安防',
  monitor: '视频监控', access: '门禁', integrated: '综合安防',
  network: '网络', cloud: '云平台', other: '其他',
}

export const STATUS_LABEL_MAP: Record<string, string> = {
  pending: '未启动', in_progress: '进行中', suspended: '已暂停', completed: '已完工',
  active: '正常', inactive: '停用', draft: '草稿',
}

export const typeLabel = (t?: string): string => TYPE_LABEL_MAP[t || ''] || t || '其他'
export const statusLabel = (s?: string): string => STATUS_LABEL_MAP[s || ''] || s || '-'

// 风险类型 → 跳转 tab
export const RISK_ACTION_MAP: Record<string, { tab: string; msg: string }> = {
  overdue: { tab: 'stage', msg: '请在阶段流程中推进项目或调整截止日期' },
  payment_overdue: { tab: 'stage', msg: '已切换到合同付款节点，请催收或登记到账' },
  progress_lag: { tab: 'stage', msg: '请检查项目执行情况并更新进度' },
  material_shortage: { tab: 'log', msg: '已切换到施工日志，请记录物料到场情况' },
  deadline_soon: { tab: 'stage', msg: '请评估是否能按期完成' },
}

export const riskActionLabel = (type: string): string => {
  const map: Record<string, string> = {
    overdue: '推进阶段', payment_overdue: '查看付款', progress_lag: '更新进度',
    material_shortage: '记录物料', deadline_soon: '评估工期',
  }
  return map[type] || '处理'
}

export const formatDate = (d: any): string => d ? String(d).slice(0, 10) : '-'
