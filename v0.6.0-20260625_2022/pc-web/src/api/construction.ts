import { get, post, put, del } from '@/utils/request'

// ===================== 项目预算 (Construction Budget) 8 端点 =====================
export const construction = {
  // 预算列表
  listBudgets: (params: any) => get('/construction/budgets', { params }),
  getBudgetSummary: (projectId: number) => get(`/construction/budgets/summary/${projectId}`),
  getBudget: (id: number) => get(`/construction/budgets/${id}`),
  createBudget: (data: any) => post('/construction/budgets', data),
  updateBudget: (id: number, data: any) => put(`/construction/budgets/${id}`, data),
  approveBudget: (id: number) => post(`/construction/budgets/${id}/approve`),
  reviseBudget: (id: number, data: any) => post(`/construction/budgets/${id}/revise`, data),
  deleteBudget: (id: number) => del(`/construction/budgets/${id}`),
}

// ===================== V0.4.3 施工团队 (Teams) 7 端点 =====================
export const teamApi = {
  list:        (params: any) => get('/construction/teams', { params }),
  show:        (id: number) => get(`/construction/teams/${id}`),
  create:      (data: any) => post('/construction/teams', data),
  update:      (id: number, data: any) => put(`/construction/teams/${id}`, data),
  remove:      (id: number) => del(`/construction/teams/${id}`),
  addMembers:  (id: number, members: any[]) => post(`/construction/teams/${id}/members`, { members }),
  removeMember:(id: number, memberId: number) => del(`/construction/teams/${id}/members/${memberId}`),
}

// ===================== V0.4.3 开工单 (Commencement Orders) 7 端点 =====================
export const commencementApi = {
  list:     (params: any) => get('/construction/commencement-orders', { params }),
  show:     (id: number) => get(`/construction/commencement-orders/${id}`),
  create:   (data: any) => post('/construction/commencement-orders', data),
  update:   (id: number, data: any) => put(`/construction/commencement-orders/${id}`, data),
  approve:  (id: number) => post(`/construction/commencement-orders/${id}/approve`),
  start:    (id: number) => post(`/construction/commencement-orders/${id}/start`),
  complete: (id: number) => post(`/construction/commencement-orders/${id}/complete`),
}

// ===================== V0.4.3 施工日志 (Logs) 7 端点 =====================
export const logApi = {
  list:           (params: any) => get('/construction/logs', { params }),
  show:           (id: number) => get(`/construction/logs/${id}`),
  create:         (data: any) => post('/construction/logs', data),
  update:         (id: number, data: any) => put(`/construction/logs/${id}`, data),
  submit:         (id: number) => post(`/construction/logs/${id}/submit`),
  updateProgress: (id: number, data: any) => post(`/construction/logs/${id}/progress`, data),
  overdue:        (params: any) => get('/construction/logs/overdue', { params }),
}

// ===================== V0.4.3 整改工单 (Rectifications) 4 端点 — V0.4.4 占位 =====================
export const rectificationApi = {
  list:     (params: any) => get('/construction/rectifications', { params }),
  show:     (id: number) => get(`/construction/rectifications/${id}`),
  create:   (data: any) => post('/construction/rectifications', data),
  complete: (id: number) => post(`/construction/rectifications/${id}/complete`),
}

// ===================== V0.4.3 工序字典 (Work Processes) 4 端点 =====================
export const workProcessApi = {
  list:   (params: any) => get('/construction/work-processes', { params }),
  create: (data: any) => post('/construction/work-processes', data),
  update: (id: number, data: any) => put(`/construction/work-processes/${id}`, data),
  remove: (id: number) => del(`/construction/work-processes/${id}`),
}

// ===================== V0.4.3 施工发包 (External Works) 7 端点 =====================
export const externalWorkApi = {
  list:     (params: any) => get('/construction/external-works', { params }),
  show:     (id: number) => get(`/construction/external-works/${id}`),
  create:   (data: any) => post('/construction/external-works', data),
  update:   (id: number, data: any) => put(`/construction/external-works/${id}`, data),
  close:    (id: number) => post(`/construction/external-works/${id}/close`),
  submitBid:(id: number, data: any) => post(`/construction/external-works/${id}/bids`, data),
  listBids: (id: number) => get(`/construction/external-works/${id}/bids`),
  award:    (id: number, data: any) => post(`/construction/external-works/${id}/award`, data),
}
