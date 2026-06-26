import { get, post, put, del } from '@/utils/request'

// ===================== V0.4.5 质保期 (Warranties) 8 端点 =====================
export const warrantyApi = {
  list:        (params: any) => get('/warranties', { params }),
  show:        (id: number) => get(`/warranties/${id}`),
  create:      (data: any) => post('/warranties', data),
  update:      (id: number, data: any) => put(`/warranties/${id}`, data),
  remove:      (id: number) => del(`/warranties/${id}`),
  renew:       (id: number, data: any) => post(`/warranties/${id}/renew`, data),
  terminate:   (id: number, data: any) => post(`/warranties/${id}/terminate`, data),
  expiring:    (params: any) => get('/warranties/expiring', { params }),
}

// ===================== V0.4.5 质保服务工单 (Warranty Service Orders) 8 端点 =====================
export const warrantyOrderApi = {
  list:            (params: any) => get('/warranty-service-orders', { params }),
  show:            (id: number) => get(`/warranty-service-orders/${id}`),
  create:          (data: any) => post('/warranty-service-orders', data),
  assign:          (id: number, data: any) => post(`/warranty-service-orders/${id}/assign`, data),
  start:           (id: number, data: any) => post(`/warranty-service-orders/${id}/start`, data),
  complete:        (id: number, data: any) => post(`/warranty-service-orders/${id}/complete`, data),
  cancel:          (id: number, data: any) => post(`/warranty-service-orders/${id}/cancel`, data),
  technicianStats: (id: number) => get(`/warranty-service-orders/technician-stats?technician_id=${id}`),
}

// ===================== V0.4.5 质保金 (Warranty Deposits) 6 端点 =====================
export const warrantyDepositApi = {
  list:           (params: any) => get('/warranty-deposits', { params }),
  show:           (id: number) => get(`/warranty-deposits/${id}`),
  create:         (data: any) => post('/warranty-deposits', data),
  partialRelease: (id: number, data: any) => post(`/warranty-deposits/${id}/partial-release`, data),
  fullRelease:    (id: number, data: any) => post(`/warranty-deposits/${id}/full-release`, data),
  forfeit:        (id: number, data: any) => post(`/warranty-deposits/${id}/forfeit`, data),
}
