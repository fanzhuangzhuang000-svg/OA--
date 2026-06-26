// Leads shared constants & types — v0.3.13 → v0.5.8
// v0.5.8: 7 段状态值（与 backend SalesController boardMap 一致）
//   5 段老值兼容：contacting (前端归一为 contacted) / converted / discarded

export type LeadStatus =
  | 'new' | 'contacted' | 'contacting'
  | 'qualified' | 'proposal' | 'negotiating'
  | 'converted' | 'discarded'
export type LeadRating = 'A' | 'B' | 'C' | 'D'

export const STATUS_OPTIONS: { value: LeadStatus; label: string }[] = [
  { value: 'new', label: '新线索' },
  { value: 'contacted', label: '跟进中' },
  { value: 'contacting', label: '跟进中' },
  { value: 'qualified', label: '合格' },
  { value: 'proposal', label: '方案报价' },
  { value: 'negotiating', label: '谈判中' },
  { value: 'converted', label: '已转商机' },
  { value: 'discarded', label: '已丢弃' },
]

export const RATING_OPTIONS: { value: LeadRating; label: string }[] = [
  { value: 'A', label: 'A - 高价值' },
  { value: 'B', label: 'B - 中等' },
  { value: 'C', label: 'C - 一般' },
  { value: 'D', label: 'D - 低' },
]

export const STATUS_TAG_TYPE: Record<LeadStatus, 'primary' | 'info' | 'warning' | 'success' | 'danger'> = {
  new: 'primary',
  contacted: 'warning',
  contacting: 'warning',
  qualified: 'success',
  proposal: 'warning',
  negotiating: 'warning',
  converted: 'info',
  discarded: 'danger',
}

export const RATING_TAG_TYPE: Record<LeadRating, 'primary' | 'success' | 'info' | 'danger'> = {
  A: 'success', B: 'primary', C: 'info', D: 'danger',
}

export const SOURCE_TAG_TYPE: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
  online: 'primary', phone: 'success', exhibition: 'warning', referral: 'danger', other: 'info',
}

export const statusLabel = (s?: string): string =>
  STATUS_OPTIONS.find((o) => o.value === s)?.label || s || '-'

export const statusTagType = (s?: string): 'primary' | 'info' | 'warning' | 'success' | 'danger' =>
  (STATUS_TAG_TYPE as any)[s || ''] || 'info'

export const ratingTagType = (r?: string): 'primary' | 'success' | 'info' | 'danger' =>
  (RATING_TAG_TYPE as any)[r || ''] || 'info'

export const sourceLabel = (s: string, options: any[] = []) =>
  options.find((o) => o.value === s)?.label || s || '-'

export const sourceTagType = (s?: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' =>
  (SOURCE_TAG_TYPE as any)[s || ''] || 'info'

export const formatMoney = (n?: number) =>
  Number(n || 0).toLocaleString('zh-CN', { maximumFractionDigits: 0 })

export const formatDate = (d?: string | null) => (d ? String(d).slice(0, 10) : '-')

// 丢弃原因（固定选项）
export const DISCARD_REASONS: { value: string; label: string }[] = [
  { value: 'no_intent', label: '客户无意向' },
  { value: 'budget', label: '预算不足' },
  { value: 'competitor', label: '已选其他供应商' },
  { value: 'no_contact', label: '联系不上' },
  { value: 'other', label: '其他' },
]
