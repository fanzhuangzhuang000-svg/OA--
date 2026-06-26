import { get, post, put, del, patch } from '@/utils/request'

// ==================== 线索池 ====================
export function getLeads(params?: any) { return get('/sales/leads', params) }
export function getLeadSourceOptions() { return get('/sales/leads/source-options') }
export function createLead(data: any) { return post('/sales/leads', data) }
export function updateLead(id: number, data: any) { return put(`/sales/leads/${id}`, data) }
export function deleteLead(id: number) { return del(`/sales/leads/${id}`) }
export function updateLeadStatus(id: number, status: string) { return patch(`/sales/leads/${id}/status`, { status }) }
export function convertLeadToOpp(id: number, data?: any) { return post(`/sales/leads/${id}/convert-to-opp`, data || {}) }

// ==================== 商机池 ====================
export function getOpps(params?: any) { return get('/sales/opps', params) }
export function getOppStageOptions() { return get('/sales/opps/stage-options') }
export function getOppFunnel() { return get('/sales/opps/funnel') }
export function getOppLostReasons() { return get('/sales/opps/lost-reasons') }
export function createOpp(data: any) { return post('/sales/opps', data) }
export function updateOpp(id: number, data: any) { return put(`/sales/opps/${id}`, data) }
export function updateOppStage(id: number, stage: string, probability?: number) {
  return patch(`/sales/opps/${id}/stage`, { stage, probability })
}
export function markOppWon(id: number, data: any) { return post(`/sales/opps/${id}/mark-won`, data) }
export function markOppLost(id: number, data: any) { return post(`/sales/opps/${id}/mark-lost`, data) }
export function reviveOpp(id: number) { return post(`/sales/opps/${id}/revive`, {}) }

// ==================== 报价单 ====================
export function getQuotes(params?: any) { return get('/sales/quotes', params) }
export function getQuoteDetail(id: number) { return get(`/sales/quotes/${id}`) }
export function getQuoteStatusOptions() { return get('/sales/quotes/status-options') }
export function updateQuoteStatus(id: number, status: string, data?: any) {
  return put(`/sales/quotes/${id}/status`, { status, ...(data || {}) })
}
export function newQuoteVersion(id: number) { return post(`/sales/quotes/${id}/new-version`) }

// ==================== 推荐人 ====================
export function getReferrers(params?: any) { return get('/sales/referrers', params) }
export function createReferrer(data: any) { return post('/sales/referrers', data) }
export function updateReferrer(id: number, data: any) { return put(`/sales/referrers/${id}`, data) }
export function deleteReferrer(id: number) { return del(`/sales/referrers/${id}`) }

// ==================== 项目池 ====================
export function getProjectPool(params?: any) { return get('/sales/pool', params) }
export function convertPoolToProject(id: number, data: any) { return post(`/sales/pool/${id}/convert-to-project`, data) }

// ==================== 客户（表单下拉用） ====================
export function getCustomerOptions(params?: any) { return get('/customers', { per_page: 200, ...(params || {}) }) }

// ==================== 居间费结算 (v0.3.11 P0 块六) ====================
export function getReferralSettlements(params?: any) { return get('/sales/referral-settlements', params) }
export function getReferralSettlementDetail(id: number) { return get(`/sales/referral-settlements/${id}`) }
export function getReferralSettlementStats() { return get('/sales/referral-settlements/stats') }
export function approveReferralSettlement(id: number) { return post(`/sales/referral-settlements/${id}/approve`, {}) }
export function payReferralSettlement(id: number, data: any) { return post(`/sales/referral-settlements/${id}/pay`, data) }

// ==================== 销售产品库 (v0.3.11 块四) ====================
export function getSalesProducts(params?: any) { return get('/sales/products', params) }
export function getSalesProductCategories() { return get('/sales/products/categories') }

// 报价单 items 批量增删
export function addQuoteItems(quoteId: number, data: any) { return post(`/sales/quotes/${quoteId}/items`, data) }
