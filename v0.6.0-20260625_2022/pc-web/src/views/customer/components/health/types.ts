// customer/Health 子组件共享 types
// v0.3.25 从 views/customer/Health.vue 抽出

export interface HealthSummary {
  total: number
  avg_score: number | null
  new_this_month: number
  growth_pct: number | null
}

export interface HealthRow {
  id: number
  name: string
  health_level: 'healthy' | 'good' | 'normal' | 'danger' | string
  health_score: number
  score_breakdown?: Record<string, number>
  last_follow_at?: string
  avatarColor?: string
}

export interface LevelCount {
  healthy: number
  good: number
  normal: number
  danger: number
}

export type TagType = 'success' | 'primary' | 'warning' | 'danger' | 'info'

export const HEALTH_DIM_LABELS: Record<string, string> = {
  recency: '最近跟进',
  frequency: '跟进频率',
  response: '响应速度',
  project: '项目活跃',
  satisfaction: '满意度',
}

export const healthDimensionLabel = (k: string): string => HEALTH_DIM_LABELS[k] || k

export const healthColor = (s: number): string => {
  if (s >= 80) return '#1D9E75'
  if (s >= 60) return '#0C447C'
  if (s >= 40) return '#BA7517'
  return '#A32D2D'
}

export const healthTagType = (level?: string, score?: number): TagType => {
  if (level === 'healthy' || (score != null && score >= 80)) return 'success'
  if (level === 'good' || (score != null && score >= 60)) return 'primary'
  if (level === 'normal' || (score != null && score >= 40)) return 'warning'
  if (level === 'danger' || (score != null && score < 40)) return 'danger'
  return 'info'
}

export const healthChipText = (level?: string, score?: number): string => {
  if (level === 'healthy' || (score != null && score >= 80)) return '健康'
  if (level === 'good' || (score != null && score >= 60)) return '良好'
  if (level === 'normal' || (score != null && score >= 40)) return '一般'
  if (level === 'danger' || (score != null && score < 40)) return '预警'
  return level || '—'
}

const AVATAR_COLORS = ['#0C447C', '#1D9E75', '#BA7517', '#534AB7', '#A32D2D']
export const avatarColor = (id: number) => AVATAR_COLORS[(id || 0) % AVATAR_COLORS.length]

export const emptySummary = (): HealthSummary => ({
  total: 0,
  avg_score: null,
  new_this_month: 0,
  growth_pct: null,
})

export const emptyLevelCount = (): LevelCount => ({
  healthy: 0, good: 0, normal: 0, danger: 0,
})
