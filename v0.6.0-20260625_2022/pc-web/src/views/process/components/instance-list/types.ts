// InstanceList 子组件共享 types
// v0.3.19 从 process/InstanceList.vue 抽出

export interface Instance {
  id: number
  project_id: number
  project_name?: string
  template_id: number
  template_name?: string
  assignee_id?: number
  assignee_name?: string
  progress: number
  planned_start?: string
  planned_end?: string
  actual_start?: string
  actual_end?: string
  status: string
  is_overdue?: boolean
}

export interface InstanceStat {
  key: keyof InstanceStats
  label: string
  value: number
  color: string
  bg: string
  icon: any  // Component
}

export interface InstanceStats {
  in_progress: number
  accepted: number
  rejected: number
  overdue: number
}

export interface SearchForm {
  project_id: number | null
  status: string
  is_overdue: boolean
}

export interface ProjectOption { id: number; name: string }
export interface UserOption { id: number; name: string }
export interface TemplateOption { id: number; name: string }

export interface OptionItem { value: string; label: string }

export const STATUS_OPTIONS: OptionItem[] = [
  { value: 'pending', label: '待开始' },
  { value: 'in_progress', label: '进行中' },
  { value: 'accepted', label: '已验收' },
  { value: 'rejected', label: '已驳回' },
  { value: 'overdue', label: '超期' },
]

export const REJECT_REASONS = ['质量问题', '工期延误', '材料不达标', '工艺不符', '其他']

// 状态 tag 类型
export type StatusTagType = 'primary' | 'success' | 'info' | 'warning' | 'danger'
export const STATUS_TAG_TYPE_MAP: Record<string, StatusTagType> = {
  pending: 'info',
  in_progress: 'primary',
  accepted: 'success',
  rejected: 'danger',
  overdue: 'warning',
}

// 进度颜色: < 30 红, 30-70 橙, > 70 绿
export const progressColor = (p: number): string => {
  if (p < 30) return '#A32D2D'
  if (p <= 70) return '#BA7517'
  return '#1D9E75'
}

// 状态 → 标签
export const statusLabel = (s: string): string => {
  if (s === 'overdue') return '超期'
  return STATUS_OPTIONS.find(o => o.value === s)?.label || s
}

// 状态 → tag 类型
export const statusTagType = (s: string): StatusTagType => {
  return STATUS_TAG_TYPE_MAP[s] || 'info'
}
