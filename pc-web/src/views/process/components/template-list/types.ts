// process/TemplateList 子组件共享 types
// v0.3.25 从 views/process/TemplateList.vue 抽出

export interface ProcessTemplate {
  id: number
  industry: string
  code: string
  name: string
  sort_order: number
  duration_days?: number
  acceptance_points?: string
  status: 0 | 1
  created_at?: string
  _statusLoading?: boolean
}

export interface TemplateStats {
  total: number
  active: number
  industryCount: number
  todayNew: number
}

export interface SearchForm {
  industry: string
  keyword: string
}

export const INDUSTRY_MAP: Record<string, string> = {
  government: '政府机关',
  finance: '金融行业',
  education: '教育行业',
  commercial: '商业地产',
  healthcare: '医疗机构',
  manufacturing: '制造业',
  transport: '交通运输',
  energy: '能源化工',
  retail: '零售连锁',
  other: '其他',
}

export const INDUSTRY_COLORS: Record<string, { bg: string; color: string }> = {
  government:  { bg: '#fee2e2', color: '#A32D2D' },
  finance:     { bg: '#dbeafe', color: '#0C447C' },
  education:   { bg: '#dcfce7', color: '#1D9E75' },
  commercial:  { bg: '#fef3c7', color: '#BA7517' },
  healthcare:  { bg: '#f3e8ff', color: '#534AB7' },
  manufacturing: { bg: '#ffe4e6', color: '#be185d' },
  transport:   { bg: '#cffafe', color: '#0e7490' },
  energy:      { bg: '#fed7aa', color: '#c2410c' },
  retail:      { bg: '#fce7f3', color: '#be185d' },
  other:       { bg: '#f1f5f9', color: '#475569' },
}

export const formatDate = (s?: string): string => s ? s.replace('T', ' ').slice(0, 16) : '-'

export const emptyStats = (): TemplateStats => ({
  total: 0, active: 0, industryCount: 0, todayNew: 0,
})

export const defaultTemplateForm = () => ({
  id: 0,
  industry: '',
  code: '',
  name: '',
  sort_order: 0,
  duration_days: 1,
  acceptance_points: '',
  status: 1 as 0 | 1,
})
