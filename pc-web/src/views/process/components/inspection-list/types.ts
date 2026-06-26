// process/InspectionList 子组件共享 types
// v0.3.25 从 views/process/InspectionList.vue 抽出

export interface Inspection {
  id: number
  project_id: number
  project_name?: string
  process_instance_id?: number
  template_name?: string
  inspector_id?: number
  inspector_name?: string
  inspected_at?: string
  result?: 'pass' | 'fail' | 'rectify' | string
  comment?: string
  defects?: string
}

export interface InspectionStats {
  total: number
  pass: number
  fail: number
}

export interface InspectionFilters {
  project_id: number | null
  process_instance_id: number | null
  result: string
}

export interface ProjectOption { id: number; name: string }
export interface ProcessInstanceOption { id: number; label: string }

export const RESULT_OPTIONS = [
  { value: 'pass', label: '合格' },
  { value: 'fail', label: '不合格' },
  { value: 'rectify', label: '需整改' },
]

export const formatDate = (s?: string): string =>
  s ? String(s).replace('T', ' ').slice(0, 16) : '-'

export const resultLabel = (r?: string): string =>
  RESULT_OPTIONS.find((o) => o.value === r)?.label || r || '-'

export const resultTagType = (r?: string): 'success' | 'danger' | 'warning' | 'info' => {
  if (r === 'pass') return 'success'
  if (r === 'fail') return 'danger'
  if (r === 'rectify') return 'warning'
  return 'info'
}

export const emptyStats = (): InspectionStats => ({ total: 0, pass: 0, fail: 0 })
