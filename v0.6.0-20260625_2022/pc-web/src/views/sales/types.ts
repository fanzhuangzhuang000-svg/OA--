// Opportunity shared constants & types — v0.3.13
// 6 段阶段值映射 (与 backend SalesController::STAGES 一致)

export type StageValue =
  | 'requirement' | 'solution' | 'negotiation' | 'contracting' | 'won' | 'lost'

export interface StageOption {
  value: StageValue
  label: string
  color: string
  icon?: string
}

export const STAGE_OPTIONS: StageOption[] = [
  { value: 'requirement', label: '需求确认', color: '#0C447C' },
  { value: 'solution', label: '方案制定', color: '#185FA5' },
  { value: 'negotiation', label: '报价谈判', color: '#BA7517' },
  { value: 'contracting', label: '合同拟定', color: '#1D9E75' },
  { value: 'won', label: '成交', color: '#67C23A' },
  { value: 'lost', label: '战败', color: '#A32D2D' },
]

export const STAGE_TAG_TYPE: Record<StageValue, 'primary' | 'info' | 'warning' | 'success' | 'danger'> = {
  requirement: 'primary',
  solution: 'info',
  negotiation: 'warning',
  contracting: 'success',
  won: 'success',
  lost: 'danger',
}

export const stageLabel = (s?: string): string =>
  STAGE_OPTIONS.find((o) => o.value === s)?.label || s || '-'

export const stageTagType = (s?: string): 'primary' | 'info' | 'warning' | 'success' | 'danger' =>
  (STAGE_TAG_TYPE as any)[s || ''] || 'info'

export const probabilityColor = (p?: number): string => {
  const v = Number(p) || 0
  if (v >= 70) return '#1D9E75'
  if (v >= 40) return '#0C447C'
  return '#BA7517'
}

export const formatMoney = (n?: number) =>
  Number(n || 0).toLocaleString('zh-CN', { maximumFractionDigits: 0 })

export const formatDate = (d?: string | null) => (d ? String(d).slice(0, 10) : '-')

// 终态判断
export const isClosed = (s?: string) => s === 'won' || s === 'lost'
