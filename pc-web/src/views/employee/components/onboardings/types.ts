// employee/Onboardings 子组件共享 types
// v0.3.22 从 views/employee/Onboardings.vue 抽出

export type StatusType = 'success' | 'warning' | 'info' | 'danger'

export interface Onboarding {
  id: number
  name: string
  username: string
  phone?: string
  email?: string
  department?: { id: number; name: string }
  position?: { id: number; name: string }
  mentor?: { id: number; name?: string; username?: string }
  hire_date?: string
  probation_months?: number
  contract_start_date?: string
  contract_end_date?: string
  status?: 'active' | 'probation' | 'archived' | string
  id_card_no?: string
  id_card_file_id?: number
  id_card_file_name?: string
  driver_license_no?: string
  driver_license_expire?: string
  driver_license_file_id?: number
  driver_license_file_name?: string
  education_level?: string
  education_school?: string
  education_major?: string
  education_file_id?: number
  education_file_name?: string
  contract_file_id?: number
  contract_file_name?: string
}

export interface Department { id: number; name: string }
export interface Position { id: number; name: string; department_id?: number }
export interface UserOption { id: number; name: string; username: string; is_active?: boolean }

export interface OnboardingFilters {
  keyword: string
  department_id: number | null
  status: string
  contract_expiring: boolean
  probation_expiring: boolean
}

export interface OnboardingPagination {
  page: number
  pageSize: number
  total: number
}

// ============ 状态/枚举 ============

export const STATUS_MAP: Record<string, { label: string; type: StatusType }> = {
  active:    { label: '在职',   type: 'success' },
  probation: { label: '试用期', type: 'warning' },
  archived:  { label: '已归档', type: 'info' },
}

export const STATUS_OPTIONS = [
  { value: 'active', label: '在职' },
  { value: 'probation', label: '试用期' },
  { value: 'archived', label: '已归档' },
]

export const EDUCATION_MAP: Record<string, string> = {
  high_school: '高中',
  college: '大专',
  bachelor: '本科',
  master: '硕士',
  doctor: '博士',
}

export const EDUCATION_OPTIONS = [
  { value: 'high_school', label: '高中' },
  { value: 'college', label: '大专' },
  { value: 'bachelor', label: '本科' },
  { value: 'master', label: '硕士' },
  { value: 'doctor', label: '博士' },
]

// ============ 工具函数 ============

export const statusLabel = (s: string): string => STATUS_MAP[s]?.label || s
export const statusTag = (s: string): StatusType => STATUS_MAP[s]?.type || 'info'
export const educationLabel = (s?: string): string => s ? (EDUCATION_MAP[s] || s) : ''

export function isContractExpiring(date?: string): boolean {
  if (!date) return false
  const d = new Date(date).getTime()
  const now = Date.now()
  return d >= now && d - now <= 30 * 86400 * 1000
}
