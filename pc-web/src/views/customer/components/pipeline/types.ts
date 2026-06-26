// customer/Pipeline 子组件共享 types
// v0.3.25 从 views/customer/Pipeline.vue 抽出

export type PipelineStage = 'lead' | 'contacted' | 'quoted' | 'negotiating' | 'won' | 'lost' | string

export interface PipelineCard {
  id: number
  name: string
  industry?: string
  expected_amount: number
  expected_close_date?: string
  last_follow_ago?: string
  tags?: string[]
  assigned_user?: { id: number; name?: string; avatar?: string }
}

export interface PipelineColumn {
  stage: PipelineStage
  label: string
  color: string
  count: number
  total: number
  cards: PipelineCard[]
}

export interface PipelineKpi {
  total_opportunities: number
  total_amount: number
  new_this_month: number
  avg_won_days: number | null
  lost_count: number
}

export interface WeeklyTrend {
  week: string
  new_count: number
  won_count: number
  lost_count: number
}

export const formatAmount = (n: number | string): string => {
  const v = Number(n) || 0
  if (v >= 10000) return (v / 10000).toFixed(1) + '万'
  return v.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}
