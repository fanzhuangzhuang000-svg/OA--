import { get, post, put, del } from '@/utils/request'

/**
 * V0.6.0 招标中心 — 内部 API
 *
 * 端点：/api/tenders + /api/portal (内部用, 走 Bearer token)
 */

// ============= 类型定义 =============

export interface TenderProject {
  id: number
  code: string
  name: string
  description?: string
  type: 'rfq' | 'tender' | 'negotiation'
  status: 'draft' | 'bidding' | 'evaluating' | 'awarded' | 'cancelled' | 'closed'
  status_label?: string
  public_token?: string
  project_id?: number
  project?: { id: number; name: string; code?: string }
  rfq_id?: number
  required_items?: Array<{ name: string; spec?: string; qty: number; unit?: string }>
  invited_supplier_ids?: number[]
  deadline?: string
  open_at?: string
  publish_at?: string
  awarded_at?: string
  score_config?: { technical: number; price: number; business: number }
  awarded_bid_id?: number
  awarded_supplier_id?: number
  awardedSupplier?: { id: number; name: string; code?: string }
  creator?: { id: number; name: string }
  created_by?: number
  bids_summary?: TenderBid[]
  attachments?: TenderAttachment[]
}

export interface TenderBid {
  id: number
  code: string
  tender_project_id: number
  supplier_id: number
  supplier?: { id: number; name: string; code?: string }
  total_amount: number
  lead_time_days?: number
  technical_proposal?: string
  remark?: string
  status: 'draft' | 'submitted' | 'shortlisted' | 'awarded' | 'rejected' | 'withdrawn'
  status_label?: string
  submitted_at?: string
  scores?: { technical: number; price: number; business: number }
  total_score?: number
  items?: TenderBidItem[]
}

export interface TenderBidItem {
  id: number
  bid_id: number
  name: string
  spec?: string
  unit?: string
  quantity: number
  unit_price: number
  total_price: number
}

export interface TenderAttachment {
  id: number
  tender_project_id?: number
  tender_bid_id?: number
  uploaded_by_user_id?: number
  uploaded_by_supplier_id?: number
  file_name: string
  file_path: string
  mime_type?: string
  file_size?: number
  category: string
  visibility: 'public' | 'eval_only'
  url?: string
  created_at?: string
}

// ============= API 封装 =============

export const tender = {
  // 列表
  list: (params?: {
    keyword?: string
    status?: string
    project_id?: number
    per_page?: number
  }) => get('/tenders', { params }),

  // 详情
  get: (id: number) => get(`/tenders/${id}`),

  // 新建 (草稿)
  create: (data: Partial<TenderProject>) => post('/tenders', data),

  // 修改
  update: (id: number, data: Partial<TenderProject>) => put(`/tenders/${id}`, data),

  // 发布
  publish: (id: number) => post(`/tenders/${id}/publish`),

  // 关闭
  close: (id: number) => post(`/tenders/${id}/close`),

  // 取消
  cancel: (id: number) => post(`/tenders/${id}/cancel`),

  // 评标
  evaluate: (id: number, evaluations: Array<{ bid_id: number; technical: number; price: number; business: number }>) =>
    post(`/tenders/${id}/evaluate`, { evaluations }),

  // 中标
  award: (id: number, bid_id: number) => post(`/tenders/${id}/award`, { bid_id }),

  // 投标列表 (含 items)
  listBids: (id: number) => get(`/tenders/${id}/bids`),

  // 内部代投 (E2E 用)
  createBidAsAdmin: (id: number, data: any) => post(`/tenders/${id}/bids`, data),

  // 附件
  listAttachments: (id: number) => get(`/tenders/${id}/attachments`),
  uploadAttachment: (id: number, formData: FormData) => post(`/tenders/${id}/attachments`, formData),
  deleteAttachment: (id: number, attId: number) => del(`/tenders/${id}/attachments/${attId}`),
}
