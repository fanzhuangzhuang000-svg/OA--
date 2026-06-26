import { get, post } from '@/utils/request'

/**
 * V0.4.2 对外报价 API 封装
 *
 * 端点：/api/external-quotes + /api/supplier-portal
 */

// ============= 类型定义 =============

export interface ExternalQuoteRequest {
  id: number
  project_id?: number
  code: string
  title: string
  required_items: any[]
  required_files?: any[]
  deadline?: string
  status: 'open' | 'closed' | 'awarded' | 'cancelled'
  public_token: string
  awarded_supplier_id?: number
  awarded_quote_id?: number
  created_by?: number
  description?: string
  quotes_count?: number
  project?: { id: number; name: string; code?: string }
  creator?: { id: number; name: string }
  awardedSupplier?: { id: number; name: string; code?: string }
  awardedQuote?: { id: number }
  has_quoted?: boolean  // 供应商门户标记
  status_label?: string
}

export interface ExternalQuote {
  id: number
  request_id: number
  supplier_id: number
  code: string
  items: any[]
  total_amount: number
  valid_until?: string
  lead_time_days: number
  payment_terms: string
  attachments?: any[]
  note?: string
  submitted_by?: number
  submitted_at?: string
  status: 'submitted' | 'shortlisted' | 'awarded' | 'rejected'
  reviewed_by?: number
  reviewed_at?: string
  supplier?: { id: number; name: string; code?: string }
  submitter?: { id: number; name: string }
  request?: { id: number; code: string; title: string; status: string; deadline?: string }
  status_label?: string
}

export interface AwardResult {
  quote: ExternalQuote
  request: ExternalQuoteRequest
  po: { id: number; po_no: string; total_amount: number; status: string }
  payable: { id: number; amount: number; status: string; ref_no: string }
}

// ============= API（内部员工） =============

export const externalQuote = {
  // 报价请求列表
  listRequests: (params?: {
    keyword?: string
    status?: string
    project_id?: number
    page?: number
    per_page?: number
  }) => get('/external-quotes/requests', { params }),

  // 创建报价请求
  createRequest: (data: {
    project_id?: number
    title: string
    required_items: any[]
    required_files?: any[]
    deadline?: string
    description?: string
  }) => post('/external-quotes/requests', data),

  // 报价请求详情
  getRequest: (id: number) => get(`/external-quotes/requests/${id}`),

  // 关闭
  closeRequest: (id: number) => post(`/external-quotes/requests/${id}/close`),

  // 取消
  cancelRequest: (id: number) => post(`/external-quotes/requests/${id}/cancel`),

  // 请求下的报价列表
  listQuotes: (id: number, params?: { status?: string }) =>
    get(`/external-quotes/requests/${id}/quotes`, { params }),

  // 入围
  shortlist: (quoteId: number) => post(`/external-quotes/${quoteId}/shortlist`),

  // 驳回
  reject: (quoteId: number, reason?: string) =>
    post(`/external-quotes/${quoteId}/reject`, { reason }),

  // 中标
  award: (quoteId: number) => post(`/external-quotes/${quoteId}/award`),
}

// ============= 供应商门户 =============

export const supplierPortal = {
  // 当前供应商 profile
  profile: () => get('/supplier-portal/profile'),

  // 可报价请求列表
  quoteRequests: () => get('/supplier-portal/quote-requests'),

  // 提交报价
  submitQuote: (requestId: number, data: {
    items: Array<{ name: string; qty: number; unit?: string; price: number }>
    total_amount: number
    valid_until?: string
    lead_time_days?: number
    payment_terms?: string
    attachments?: any[]
    note?: string
  }) => post(`/supplier-portal/quote-requests/${requestId}/submit`, data),

  // 我方历史报价
  myQuotes: () => get('/supplier-portal/quotes'),
}
