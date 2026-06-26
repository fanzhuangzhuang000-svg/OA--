import { get, post, put, del } from '@/utils/request'

// 客户
export function getCustomerList(params?: any) { return get('/customers', params) }
export function getCustomerDetail(id: number) { return get(`/customers/${id}`) }
export function createCustomer(data: any) { return post('/customers', data) }
export function updateCustomer(id: number, data: any) { return put(`/customers/${id}`, data) }
export function deleteCustomer(id: number) { return del(`/customers/${id}`) }
export function getCustomerMap() { return get('/customers/map') }
export function getCustomerFollow(id: number, params?: any) { return get(`/customers/${id}/follows`, params) }
export function addCustomerFollow(id: number, data: any) { return post(`/customers/${id}/follows`, data) }
export function getCustomerHealth() { return get('/customers/health') }
// 销售漏斗看板
export function getCustomerPipeline(params?: any) { return get('/customers/pipeline', params) }
export function updateCustomerStage(id: number, stage: string) { return put(`/customers/${id}/stage`, { pipeline_stage: stage }) }
export function getPipelineWeeklyTrend() { return get('/customers/pipeline/weekly-trend') }
export function getFollowCalendar(month: string, userId?: number, customerId?: number) {
  return get('/follow-ups/calendar', { params: { month, user_id: userId, customer_id: customerId } })
}
export function getUserList(params?: any) { return get('/users', params) }

// 项目
export function getProjectList(params?: any) { return get('/projects', params) }
export function getProjectDetail(id: number) { return get(`/projects/${id}`) }
export function createProject(data: any) { return post('/projects', data) }
export function updateProject(id: number, data: any) { return put(`/projects/${id}`, data) }
export function deleteProject(id: number) { return del(`/projects/${id}`) }
export function getProjectGantt(id: number) { return get(`/projects/${id}/gantt`) }
export function updateProjectStage(id: number, data: any) { return put(`/projects/${id}/stage`, data) }

// 售后
export function getServiceOrderList(params?: any) { return get('/service/orders', params) }
export function getServiceOrderDetail(id: number | string) { return get(`/service/orders/${id}`) }
export function createServiceOrder(data: any) { return post('/service/orders', data) }
export function updateServiceOrder(id: number, data: any) { return put(`/service/orders/${id}`, data) }
export function assignServiceOrder(id: number, data: any) { return post(`/service/orders/${id}/assign`, data) }
export function completeServiceOrder(id: number, data: any) { return post(`/service/orders/${id}/complete`, data) }
export function getServiceStats(params?: any) { return get('/service/orders/stats', params) }

// 考勤
export function getAttendanceList(params?: any) { return get('/attendance', params) }
export function getAttendanceStats(params?: any) { return get('/attendance/stats', params) }
export function clockIn(data: any) { return post('/attendance/clock-in', data) }
export function clockOut(data: any) { return post('/attendance/clock-out', data) }
export function applyLeave(data: any) { return post('/attendance/leave', data) }
export function getLeaveList(params?: any) { return get('/attendance/leave', params) }

// ====== 排班 ======
export const schedule = {
  // 班次
  listShifts:    () => get('/schedules/shifts'),
  createShift:   (data: any) => post('/schedules/shifts', data),
  updateShift:   (id: number, data: any) => put(`/schedules/shifts/${id}`, data),
  deleteShift:   (id: number) => del(`/schedules/shifts/${id}`),
  // 班组
  listGroups:    () => get('/schedules/groups'),
  createGroup:   (data: any) => post('/schedules/groups', data),
  updateGroup:   (id: number, data: any) => put(`/schedules/groups/${id}`, data),
  deleteGroup:   (id: number) => del(`/schedules/groups/${id}`),
  syncMembers:   (id: number, user_ids: number[]) => post(`/schedules/groups/${id}/members`, { user_ids }),
  addMember:     (id: number, user_id: number) => post(`/schedules/groups/${id}/add-member`, { user_id }),
  removeMember:  (id: number, user_id: number) => del(`/schedules/groups/${id}/members/${user_id}`),
  // 排班
  index:         (params: any) => get('/schedules', params),
  batchSave:     (assignments: any[]) => post('/schedules', { assignments }),
  batchByGroup:  (data: any) => post('/schedules/batch-by-group', data),
  destroy:       (id: number) => del(`/schedules/${id}`),
  mySchedule:    (params?: any) => get('/schedules/my-schedule', params),
  smartSuggest:  (params: any) => get('/schedules/smart-suggest', params),
  nextReminder:  () => get('/schedules/next-reminder'),
  stats:         (params?: any) => get('/schedules/stats', params),
}

// 报销
export function getExpenseList(params?: any) { return get('/expenses', params) }
export function createExpense(data: any) { return post('/expenses', data) }
export function getExpenseDetail(id: number) { return get(`/expenses/${id}`) }
export function approveExpense(id: number, data: any) { return post(`/expenses/${id}/approve`, data) }

// 车辆
export function getVehicleList(params?: any) { return get('/vehicles', params) }
export function createVehicle(data: any) { return post('/vehicles', data) }
export function applyVehicle(data: any) { return post('/vehicles/apply', data) }
export function getVehicleApplyList(params?: any) { return get('/vehicles/applies', params) }
export function approveVehicleApply(id: number, data: any) { return post(`/vehicles/applies/${id}/approve`, data) }
export function getVehicleStats() { return get('/vehicles/stats') }
// 保险
export function getInsuranceList(params?: any) { return get('/vehicles/insurances', params) }
export function createInsurance(data: any) { return post('/vehicles/insurances', data) }
export function updateInsurance(id: number, data: any) { return put(`/vehicles/insurances/${id}`, data) }
export function deleteInsurance(id: number) { return del(`/vehicles/insurances/${id}`) }
// 保养
export function getMaintenanceList(params?: any) { return get('/vehicles/maintenances', params) }
export function createMaintenance(data: any) { return post('/vehicles/maintenances', data) }
export function updateMaintenance(id: number, data: any) { return put(`/vehicles/maintenances/${id}`, data) }
export function deleteMaintenance(id: number) { return del(`/vehicles/maintenances/${id}`) }
// 油卡
export function getFuelCardList(params?: any) { return get('/fuel-cards', params) }
export function createFuelCard(data: any) { return post('/fuel-cards', data) }
export function updateFuelCard(id: number, data: any) { return put(`/fuel-cards/${id}`, data) }
export function deleteFuelCard(id: number) { return del(`/fuel-cards/${id}`) }
export function getFuelCardRecharges(params?: any) { return get('/fuel-cards/recharges', params) }
export function createFuelCardRecharge(data: any) { return post('/fuel-cards/recharges', data) }
export function deleteFuelCardRecharge(id: number) { return del(`/fuel-cards/recharges/${id}`) }
export function getFuelCardStats() { return get('/fuel-cards/stats') }
// 库存分类
export function getInventoryCategoryList() { return get('/inventory-categories') }
export function getInventoryCategoryTree() { return get('/inventory-categories/tree') }
export function createInventoryCategory(data: any) { return post('/inventory-categories', data) }
export function updateInventoryCategory(id: number, data: any) { return put(`/inventory-categories/${id}`, data) }
export function deleteInventoryCategory(id: number) { return del(`/inventory-categories/${id}`) }

// 财务 - 应收/应付
export function getReceivables(params?: any) { return get('/finance/receivables', params) }
export function getReceivableDetail(id: number) { return get(`/finance/receivables/${id}`) }
export function createReceivable(data: any) { return post('/finance/receivables', data) }
export function updateReceivable(id: number, data: any) { return put(`/finance/receivables/${id}`, data) }
export function deleteReceivable(id: number) { return del(`/finance/receivables/${id}`) }
export function getPayables(params?: any) { return get('/finance/payables', params) }
export function getPayableDetail(id: number) { return get(`/finance/payables/${id}`) }
export function createPayable(data: any) { return post('/finance/payables', data) }
export function updatePayable(id: number, data: any) { return put(`/finance/payables/${id}`, data) }
export function deletePayable(id: number) { return del(`/finance/payables/${id}`) }

// 财务 - 收/付款记录
export function getReceipts(params?: any) { return get('/finance/receipts', params) }
export function getPayments(params?: any) { return get('/finance/payments', params) }

// 财务 - 资金账户/转账/总览
export function getFinanceOverview() { return get('/finance/overview') }
export function getFinanceAccounts(params?: any) { return get('/finance/accounts', params) }
export function createFinanceAccount(data: any) { return post('/finance/accounts', data) }
export function updateFinanceAccount(id: number, data: any) { return put(`/finance/accounts/${id}`, data) }
export function deleteFinanceAccount(id: number) { return del(`/finance/accounts/${id}`) }
export function createFinanceTransfer(data: any) { return post('/finance/transfers', data) }

// 财务 - 发票
export function getInvoices(params?: any) { return get('/finance/invoices', params) }
export function getInvoiceDetail(id: number) { return get(`/finance/invoices/${id}`) }
export function createInvoice(data: any) { return post('/finance/invoices', data) }
export function updateInvoice(id: number, data: any) { return put(`/finance/invoices/${id}`, data) }
export function deleteInvoice(id: number) { return del(`/finance/invoices/${id}`) }

// 采购
export function getPurchaseRequirements(params?: any) { return get('/purchase/requirements', params) }
export function getPurchaseRequirementDetail(id: number) { return get(`/purchase/requirements/${id}`) }
export function createPurchaseRequirement(data: any) { return post('/purchase/requirements', data) }
export function updatePurchaseRequirement(id: number, data: any) { return put(`/purchase/requirements/${id}`, data) }
export function deletePurchaseRequirement(id: number) { return del(`/purchase/requirements/${id}`) }

export function getPurchasePlans(params?: any) { return get('/purchase/plans', params) }
export function getPurchasePlanDetail(id: number) { return get(`/purchase/plans/${id}`) }
export function createPurchasePlan(data: any) { return post('/purchase/plans', data) }
export function updatePurchasePlan(id: number, data: any) { return put(`/purchase/plans/${id}`, data) }
export function deletePurchasePlan(id: number) { return del(`/purchase/plans/${id}`) }
export function approvePurchasePlan(id: number, data?: any) { return post(`/purchase/plans/${id}/approve`, data || {}) }

export function getPurchaseApprovals(params?: any) { return get('/purchase/approvals', params) }
export function createPurchaseApproval(data: any) { return post('/purchase/approvals', data) }
export function updatePurchaseApproval(id: number, data: any) { return put(`/purchase/approvals/${id}`, data) }
export function deletePurchaseApproval(id: number) { return del(`/purchase/approvals/${id}`) }

export function getPurchasePaymentRequests(params?: any) { return get('/purchase/payment-requests', params) }
export function createPurchasePaymentRequest(data: any) { return post('/purchase/payment-requests', data) }
export function updatePurchasePaymentRequest(id: number, data: any) { return put(`/purchase/payment-requests/${id}`, data) }
export function deletePurchasePaymentRequest(id: number) { return del(`/purchase/payment-requests/${id}`) }

export function getPurchasePayments(params?: any) { return get('/purchase/payments', params) }
export function createPurchasePayment(data: any) { return post('/purchase/payments', data) }
export function updatePurchasePayment(id: number, data: any) { return put(`/purchase/payments/${id}`, data) }
export function deletePurchasePayment(id: number) { return del(`/purchase/payments/${id}`) }

export function getPurchaseContracts(params?: any) { return get('/purchase/contracts', params) }
export function getPurchaseContractDetail(id: number) { return get(`/purchase/contracts/${id}`) }
export function createPurchaseContract(data: any) { return post('/purchase/contracts', data) }
export function updatePurchaseContract(id: number, data: any) { return put(`/purchase/contracts/${id}`, data) }
export function deletePurchaseContract(id: number) { return del(`/purchase/contracts/${id}`) }

export function getPurchaseShipments(params?: any) { return get('/purchase/shipments', params) }
export function createPurchaseShipment(data: any) { return post('/purchase/shipments', data) }
export function updatePurchaseShipment(id: number, data: any) { return put(`/purchase/shipments/${id}`, data) }
export function deletePurchaseShipment(id: number) { return del(`/purchase/shipments/${id}`) }

export function getPurchaseLogistics(params?: any) { return get('/purchase/logistics', params) }
export function createPurchaseLogistic(data: any) { return post('/purchase/logistics', data) }
export function updatePurchaseLogistic(id: number, data: any) { return put(`/purchase/logistics/${id}`, data) }
export function deletePurchaseLogistic(id: number) { return del(`/purchase/logistics/${id}`) }

// 审批
export function getApprovalList(params?: any) { return get('/approvals', params) }
export function getApprovalDetail(id: number) { return get(`/approvals/${id}`) }
export function createApproval(data: any) { return post('/approvals', data) }
export function updateApproval(id: number, data: any) { return put(`/approvals/${id}`, data) }
export function deleteApproval(id: number) { return del(`/approvals/${id}`) }
export function approveApproval(id: number, data?: any) { return post(`/approvals/${id}/approve`, data || {}) }
export function rejectApproval(id: number, data?: any) { return post(`/approvals/${id}/reject`, data || {}) }
export function transferApproval(id: number, data: any) { return post(`/approvals/${id}/transfer`, data) }
// 审批分类
export function getApprovalsFinance(params?: any) { return get('/approvals/finance', params) }
export function getApprovalsProject(params?: any) { return get('/approvals/project', params) }
export function getApprovalsOperation(params?: any) { return get('/approvals/operation', params) }

// ===================== 库存 (Inventory) 12 端点 =====================
export const inventory = {
  // 树 / 分类
  treeWithCounts: () => get('/inventory/tree-with-counts'),
  itemsByCategory: (params?: any) => get('/inventory/items-by-category', params),
  moveCategory: (id: number, parentId: number | null) => post(`/inventory-categories/${id}/move`, { parent_id: parentId }),
  getCategories: () => get('/inventory-categories'),
  createCategory: (data: any) => post('/inventory-categories', data),
  updateCategory: (id: number, data: any) => put(`/inventory-categories/${id}`, data),
  deleteCategory: (id: number) => del(`/inventory-categories/${id}`),

  // 物品 CRUD
  getItems: (params?: any) => get('/inventory', params),
  createItem: (data: any) => post('/inventory', data),
  updateItem: (id: number, data: any) => put(`/inventory/${id}`, data),
  deleteItem: (id: number) => del(`/inventory/${id}`),

  // 批量导入 / 模板
  // 注意: request 拦截器在检测到 FormData 时会自动清除 Content-Type,
  // 让浏览器自动添加 boundary, 因此这里不再显式传 Content-Type 头
  batchImport: (formData: FormData) => post('/inventory/items/batch-import', formData),
  exportTemplate: () => get('/inventory/items/export-template', undefined, { responseType: 'blob' }),

  // 批量处理
  batchDelete: (ids: number[]) => post('/inventory/batch-delete', { ids }),
  batchUpdate: (ids: number[], fields: Record<string, any>) => post('/inventory/batch-update', { ids, fields }),
  batchExport: (params: { ids?: number[]; keyword?: string; warehouse_id?: number; category_id?: number; status?: string }) =>
    post('/inventory/batch-export', params, { responseType: 'blob' }),

  // 预警
  warnings: () => get('/inventory/warnings'),

  // 仓库 (用于下拉)
  warehouses: () => get('/inventory/warehouses'),
}

// ===================== 采购 (Purchase) 37 端点 =====================
export const purchase = {
  // ---- 采购需求 (5 端点)
  getRequirements: (params?: any) => get('/purchase/requirements', params),
  getRequirementStats: () => get('/purchase/requirements/stats'),
  createRequirement: (data: any) => post('/purchase/requirements', data),
  updateRequirement: (id: number, data: any) => put(`/purchase/requirements/${id}`, data),
  deleteRequirement: (id: number) => del(`/purchase/requirements/${id}`),

  // ---- 采购计划 (7 端点)
  getPlans: (params?: any) => get('/purchase/plans', params),
  getPlanStats: () => get('/purchase/plans/stats'),
  createPlan: (data: any) => post('/purchase/plans', data),
  updatePlan: (id: number, data: any) => put(`/purchase/plans/${id}`, data),
  deletePlan: (id: number) => del(`/purchase/plans/${id}`),
  submitPlan: (id: number) => post(`/purchase/plans/${id}/submit`, {}),
  approvePlan: (id: number, data: any) => post(`/purchase/plans/${id}/approve`, data),

  // ---- 采购审批 (3 端点) — 独立采购审批单 (非 plan submit/approve)
  getApprovals: (params?: any) => get('/purchase/approvals', params),
  createApproval: (data: any) => post('/purchase/approvals', data),
  decideApproval: (id: number, data: any) => post(`/purchase/approvals/${id}/decide`, data),

  // ---- 采购付款申请 (4 端点：后端无 PUT/无单条 GET)
  getPaymentRequests: (params?: any) => get('/purchase/payment-requests', params),
  getPaymentRequestStats: () => get('/purchase/payment-requests/stats'),
  createPaymentRequest: (data: any) => post('/purchase/payment-requests', data),
  approvePaymentRequest: (id: number, data: any) => post(`/purchase/payment-requests/${id}/approve`, data),
  deletePaymentRequest: (id: number) => del(`/purchase/payment-requests/${id}`),

  // ---- 采购付款 (3 端点)
  getPayments: (params?: any) => get('/purchase/payments', params),
  getPaymentStats: () => get('/purchase/payments/stats'),
  createPayment: (data: any) => post('/purchase/payments', data),

  // ---- 采购合同 (7 端点)
  getContracts: (params?: any) => get('/purchase/contracts', params),
  getContractDetail: (id: number) => get(`/purchase/contracts/${id}`),
  getContractStats: () => get('/purchase/contracts/stats'),
  createContract: (data: any) => post('/purchase/contracts', data),
  updateContract: (id: number, data: any) => put(`/purchase/contracts/${id}`, data),
  deleteContract: (id: number) => del(`/purchase/contracts/${id}`),
  shipContract: (id: number, data: any) => post(`/purchase/contracts/${id}/ship`, data),

  // ---- 采购发货 (3 端点 — 只读)
  getShipments: (params?: any) => get('/purchase/shipments', params),
  getShipmentDetail: (id: number) => get(`/purchase/shipments/${id}`),
  getShipmentStats: () => get('/purchase/shipments/stats'),

  // ---- 采购物流 (4 端点)
  getShipmentLogistics: (shipmentId: number, params?: any) => get(`/purchase/shipments/${shipmentId}/logistics`, params),
  getShipmentTrack: (shipmentId: number) => get(`/purchase/shipments/${shipmentId}/track`),
  addLogisticsEvent: (shipmentId: number, data: any) => post(`/purchase/shipments/${shipmentId}/logistics-update`, data),
  updateLogisticsEvent: (shipmentId: number, logId: number, data: any) => put(`/purchase/shipments/${shipmentId}/logistics/${logId}`, data),
}

// ===================== 入职档案 (Employee Onboardings) =====================
export const onboardings = {
  list:   (params: any) => get('/employee-onboardings', params),
  show:   (id: number)  => get(`/employee-onboardings/${id}`),
  create: (data: any)   => post('/employee-onboardings', data),
  update: (id: number, data: any) => put(`/employee-onboardings/${id}`, data),
  archive: (id: number) => del(`/employee-onboardings/${id}`),
}

// ===================== 离职管理 (Employee Resignations) =====================
export const resignations = {
  list:              (params: any) => get('/employee-resignations', params),
  show:              (id: number)  => get(`/employee-resignations/${id}`),
  create:            (data: any)   => post('/employee-resignations', data),
  update:            (id: number, data: any) => put(`/employee-resignations/${id}`, data),
  submit:            (id: number)  => post(`/employee-resignations/${id}/submit`),
  approve:           (id: number)  => post(`/employee-resignations/${id}/approve`),
  cancel:            (id: number)  => post(`/employee-resignations/${id}/cancel`),
  complete:          (id: number, data: any) => post(`/employee-resignations/${id}/complete`, data),
  settlementPreview: (params: any) => get('/employee-resignations/settlement-preview', params),
}

// ===================== 工序管理 (Process) V1.1 工序验收 =====================
export const processApi = {
  // ---- 行业字典 (Industries) ----
  industries:        () => get('/process/industries'),

  // ---- 工序模板 (Templates) ----
  templateList:      (params: any) => get('/process/templates', params),
  templateDetail:    (id: number)   => get(`/process/templates/${id}`),
  templateCreate:    (data: any)    => post('/process/templates', data),
  templateUpdate:    (id: number, data: any) => put(`/process/templates/${id}`, data),
  templateDelete:    (id: number)   => del(`/process/templates/${id}`),

  // ---- 工序实例 (Instances) ----
  instanceList:      (params: any) => get('/process/instances', params),
  instanceCreate:    (data: any)    => post('/process/instances', data),
  instanceDetail:    (id: number)   => get(`/process/instances/${id}`),
  instanceUpdate:    (id: number, data: any) => put(`/process/instances/${id}`, data),
  instanceDelete:    (id: number)   => del(`/process/instances/${id}`),
  instanceAccept:    (id: number, data: any) => post(`/process/instances/${id}/accept`, data),
  instanceReject:    (id: number, data: any) => post(`/process/instances/${id}/reject`, data),
  instanceProgress:  (id: number, data: any) => post(`/process/instances/${id}/progress`, data),

  // ---- 验收记录 (Inspections) ----
  inspectionList:    (params: any) => get('/process/inspections', params),
  inspectionDetail:  (id: number)   => get(`/process/inspections/${id}`),
  inspectionCreate:  (data: any)    => post('/process/inspections', data),
  inspectionUpdate:  (id: number, data: any) => put(`/process/inspections/${id}`, data),
  inspectionDelete:  (id: number)   => del(`/process/inspections/${id}`),
}
