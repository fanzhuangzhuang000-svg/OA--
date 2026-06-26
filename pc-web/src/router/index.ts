import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken, removeToken } from '@/utils/auth'
import { useUserStore } from '@/stores/user'
import { startIdleMonitor, stopIdleMonitor } from '@/composables/useIdleTimer'

NProgress.configure({ showSpinner: false })

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/project-overview',
    children: [
      // 工作台（保留: 签到打卡入口, 默认跳总览看板, 加 alias 兼容老链接）
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      },
      // ---- V0.4.5 总览看板 (顶级, 替换工作台为默认页) ----
      {
        path: 'project-overview',
        name: 'ProjectOverview',
        component: () => import('@/views/dashboard/Overview.vue'),
        meta: { title: '总览看板', icon: 'DataBoard' }
      },
      // ---- 考勤管理 ----
      {
        path: 'attendance',
        name: 'Attendance',
        redirect: '/attendance/overview',
        alias: '/attendance',
        meta: { title: '考勤管理', icon: 'Calendar' },
        children: [
          { path: 'overview', name: 'AttendanceOverview', component: () => import('@/views/attendance/index.vue'), meta: { title: '考勤总览' } },
          { path: 'record', name: 'AttendanceRecord', component: () => import('@/views/attendance/Record.vue'), meta: { title: '打卡记录' } },
          { path: 'leave', name: 'AttendanceLeave', component: () => import('@/views/attendance/Leave.vue'), meta: { title: '请假管理' } },
          { path: 'overtime', name: 'AttendanceOvertime', component: () => import('@/views/attendance/Overtime.vue'), meta: { title: '加班管理' } },
          { path: 'report', name: 'AttendanceReport', component: () => import('@/views/attendance/Report.vue'), meta: { title: '考勤报表' } },
          { path: 'shifts', name: 'AttendanceShifts', component: () => import('@/views/attendance/Shifts.vue'), meta: { title: '班次配置' } },
          { path: 'groups', name: 'AttendanceGroups', component: () => import('@/views/attendance/Groups.vue'), meta: { title: '班组管理' } },
          { path: 'schedule', name: 'AttendanceSchedule', component: () => import('@/views/attendance/Schedule.vue'), meta: { title: '排班计划' } },
          { path: 'my-schedule', name: 'AttendanceMySchedule', component: () => import('@/views/attendance/MySchedule.vue'), meta: { title: '我的排班' } }
        ]
      },
      // ---- 员工管理 ----
      {
        path: 'employee',
        name: 'Employee',
        redirect: '/employee/list',
        alias: '/employee',
        meta: { title: '员工管理', icon: 'User' },
        children: [
          { path: 'list', name: 'EmployeeList', component: () => import('@/views/employee/Organization.vue'), meta: { title: '员工列表' } },
          { path: 'org', name: 'EmployeeOrg', component: () => import('@/views/employee/Organization.vue'), meta: { title: '组织架构' } },
          { path: 'onboardings', name: 'EmployeeOnboardings', component: () => import('@/views/employee/Onboardings.vue'), meta: { title: '入职档案' } },
          { path: 'resignations', name: 'EmployeeResignations', component: () => import('@/views/employee/Resignations.vue'), meta: { title: '离职管理' } },
          { path: 'skill', name: 'EmployeeSkill', component: () => import('@/views/employee/Skill.vue'), meta: { title: '技能标签' } }
        ]
      },
      // ---- 客户管理 ----
      {
        path: 'customer',
        name: 'Customer',
        redirect: '/customer/list',
        alias: '/customer',
        meta: { title: '客户管理', icon: 'OfficeBuilding' },
        children: [
          { path: 'list', name: 'CustomerList', component: () => import('@/views/customer/index.vue'), meta: { title: '客户列表', permission: 'customer.view' } },
          { path: 'health', name: 'CustomerHealth', component: () => import('@/views/customer/Health.vue'), meta: { title: '客户健康度' } },
          { path: 'pipeline', name: 'CustomerPipeline', component: () => import('@/views/customer/Pipeline.vue'), meta: { title: '销售漏斗' } },
          { path: 'follow-calendar', name: 'CustomerFollowCalendar', component: () => import('@/views/customer/FollowCalendar.vue'), meta: { title: '跟进日历' } },
          { path: 'map', name: 'CustomerMap', component: () => import('@/views/customer/CustomerMap.vue'), meta: { title: '客户地图' } },
          { path: ':id', name: 'CustomerDetail', component: () => import('@/views/customer/Detail.vue'), meta: { title: '客户详情', hidden: true }, props: true }
        ]
      },
      // ---- 销售管理 (P0 界面) ----
      {
        path: 'sales',
        name: 'Sales',
        redirect: '/sales/leads',
        alias: '/sales',
        meta: { title: '销售管理', icon: 'Money' },
        children: [
          { path: 'leads', name: 'SalesLeads', component: () => import('@/views/sales/Leads.vue'), meta: { title: '线索池' } },
          { path: 'leads/board', name: 'SalesLeadsBoard', component: () => import('@/views/sales/LeadsBoard.vue'), meta: { title: '线索看板' } },
          { path: 'opps', name: 'SalesOpps', component: () => import('@/views/sales/Opps.vue'), meta: { title: '商机池' } },
          { path: 'opps/board', name: 'SalesOppsBoard', component: () => import('@/views/sales/OppsBoard.vue'), meta: { title: '商机看板' } },
          { path: 'opps/:id/quote', name: 'SalesQuotes', component: () => import('@/views/sales/Quotes.vue'), meta: { title: '报价单' } },
          { path: 'referrers', name: 'SalesReferrers', component: () => import('@/views/sales/Referrers.vue'), meta: { title: '推荐人' } },
          { path: 'settlements', name: 'SalesSettlements', component: () => import('@/views/sales/Settlements.vue'), meta: { title: '居间费结算' } },
          // 对外报价看板 (V0.4.2) - 移到销售管理下
          { path: 'external-quote', name: 'SalesExternalQuote', component: () => import('@/views/external-quote/index.vue'), meta: { title: '对外报价看板' } }
        ]
      },
      // ---- 招标中心 (V0.6.0) — 独立顶级菜单, 与销售/采购并列 ----
      {
        path: 'business/tender',
        name: 'BusinessTender',
        redirect: '/business/tender/list',
        meta: { title: '招标中心', icon: 'Trophy' },
        children: [
          { path: 'list', name: 'TenderList', component: () => import('@/views/business/tender/index.vue'), meta: { title: '招标项目' } },
          { path: 'detail/:id', name: 'TenderDetail', component: () => import('@/views/business/tender/Detail.vue'), meta: { title: '招标详情', hidden: true }, props: true }
        ]
      },
      // ---- 项目管理 — 合同/钱/质保期全流程 ----
      {
        path: 'project',
        name: 'Project',
        redirect: '/project/list',
        meta: { title: '项目管理', icon: 'Files' },
        children: [
          { path: '', redirect: '/project/list' },
          { path: 'pool', name: 'ProjectPool', component: () => import('@/views/project/Pool.vue'), meta: { title: '项目池' } },
          { path: 'list', name: 'ProjectList', component: () => import('@/views/project/index.vue'), meta: { title: '项目列表', permission: 'project.view' } },
          { path: 'board', name: 'ProjectBoard', component: () => import('@/views/project/Board.vue'), meta: { title: '项目看板' } },
          { path: 'calendar', name: 'ProjectCalendar', component: () => import('@/views/project/Calendar.vue'), meta: { title: '付款日历' } },
          { path: 'create', name: 'ProjectCreate', component: () => import('@/views/project/Create.vue'), meta: { title: '创建项目' } },
          { path: 'detail/:id', name: 'ProjectDetail', component: () => import('@/views/project/Detail.vue'), meta: { title: '项目详情', hidden: true }, props: true },
          { path: 'gantt/:id', name: 'ProjectGantt', component: () => import('@/views/project/Gantt.vue'), meta: { title: '施工甘特图' }, props: true },
          // 总览看板已在顶级路由 (/project-overview)
          // ---- V0.4.5 质保期管理 (合同后续义务, 归项目管理) ----
          { path: 'warranty/list', name: 'WarrantyList', component: () => import('@/views/warranty/Index.vue'), meta: { title: '质保期列表', permission: 'warranty.view' } },
          { path: 'warranty/create', name: 'WarrantyCreate', component: () => import('@/views/warranty/Create.vue'), meta: { title: '新建质保期', hidden: true } },
          { path: 'warranty/detail/:id', name: 'WarrantyDetail', component: () => import('@/views/warranty/Detail.vue'), meta: { title: '质保期详情', hidden: true }, props: true },
          { path: 'warranty/expiring', name: 'WarrantyExpiring', component: () => import('@/views/warranty/Expiring.vue'), meta: { title: '即将到期' } },
          { path: 'warranty/service-order', name: 'WarrantyServiceOrderList', component: () => import('@/views/warranty/ServiceOrder.vue'), meta: { title: '服务工单' } },
          { path: 'warranty/service-order/detail/:id', name: 'WarrantyServiceOrderDetail', component: () => import('@/views/warranty/ServiceOrderDetail.vue'), meta: { title: '工单详情', hidden: true }, props: true },
          { path: 'warranty/deposit', name: 'WarrantyDepositList', component: () => import('@/views/warranty/Deposit.vue'), meta: { title: '质保金' } },
          { path: 'warranty/deposit/detail/:id', name: 'WarrantyDepositDetail', component: () => import('@/views/warranty/DepositDetail.vue'), meta: { title: '质保金详情', hidden: true }, props: true }
        ]
      },
      // 兼容老路径: /process/* → /construction/process/* (C 方案: 工序归施工)
      { path: 'process', redirect: '/construction/process/templates' },
      { path: 'process/templates', redirect: '/construction/process/templates' },
      { path: 'process/instances', redirect: '/construction/process/instances' },
      { path: 'process/inspections', redirect: '/construction/process/inspections' },
      { path: 'process/instances/detail/:id', redirect: '/construction/process/instances/detail/:id' },
      { path: 'project/process/templates', redirect: '/construction/process/templates' },
      { path: 'project/process/instances', redirect: '/construction/process/instances' },
      { path: 'project/process/inspections', redirect: '/construction/process/inspections' },
      { path: 'project/process/instances/detail/:id', redirect: '/construction/process/instances/detail/:id' },
      // 兼容老路径: /external-quote → /sales/external-quote
      { path: 'external-quote', redirect: '/sales/external-quote' },
      // ---- 采购管理 (v0.3.10) - 放在「施工管理」后面 ----
      {
        path: 'purchase',
        name: 'Purchase',
        redirect: '/purchase/requirement',
        alias: '/purchase',
        meta: { title: '采购管理', icon: 'ShoppingCart' },
        children: [
          { path: 'requirement', name: 'PurchaseRequirement', component: () => import('@/views/purchase/Requirement.vue'), meta: { title: '采购需求' } },
          { path: 'plan', name: 'PurchasePlan', component: () => import('@/views/purchase/Plan.vue'), meta: { title: '采购计划' } },
          { path: 'approval', name: 'PurchaseApproval', component: () => import('@/views/purchase/Approval.vue'), meta: { title: '采购审批' } },
          { path: 'payment-request', name: 'PurchasePaymentRequest', component: () => import('@/views/purchase/PaymentRequest.vue'), meta: { title: '付款申请' } },
          { path: 'payment', name: 'PurchasePayment', component: () => import('@/views/purchase/Payment.vue'), meta: { title: '财务付款' } },
          { path: 'contract', name: 'PurchaseContract', component: () => import('@/views/purchase/Contract.vue'), meta: { title: '采购合同' } },
          { path: 'shipment', name: 'PurchaseShipment', component: () => import('@/views/purchase/Shipment.vue'), meta: { title: '供应商发货' } },
          { path: 'logistics', name: 'PurchaseLogistics', component: () => import('@/views/purchase/Logistics.vue'), meta: { title: '物流跟踪' } }
        ]
      },
      // ---- 施工管理 (V0.4.3) — 施工团队/开工单/日志/发包 ----
      {
        path: 'construction',
        name: 'Construction',
        redirect: '/construction/team',
        alias: '/construction',
        meta: { title: '施工管理', icon: 'Tools' },
        children: [
          // 施工团队
          { path: 'team',         name: 'ConstructionTeam',         component: () => import('@/views/construction/team/index.vue'),          meta: { title: '施工团队' } },
          { path: 'team/:id',     name: 'ConstructionTeamDetail',  component: () => import('@/views/construction/team/Detail.vue'),        meta: { title: '团队详情', hidden: true }, props: true },
          // 开工单
          { path: 'commencement', name: 'ConstructionCommencement', component: () => import('@/views/construction/commencement/index.vue'), meta: { title: '开工单' } },
          { path: 'commencement/:id', name: 'ConstructionCommencementDetail', component: () => import('@/views/construction/commencement/Detail.vue'), meta: { title: '开工详情', hidden: true }, props: true },
          // 施工日志
          { path: 'log',          name: 'ConstructionLog',         component: () => import('@/views/construction/log/index.vue'),         meta: { title: '施工日志' } },
          { path: 'log/daily',    name: 'ConstructionLogDaily',     component: () => import('@/views/construction/log/DailyReport.vue'),   meta: { title: '每日上报' } },
          // 整改工单
          { path: 'rectification', name: 'ConstructionRectification', component: () => import('@/views/construction/rectification/index.vue'), meta: { title: '整改工单' } },
          { path: 'rectification/:id', name: 'ConstructionRectificationDetail', component: () => import('@/views/construction/rectification/Detail.vue'), meta: { title: '整改详情', hidden: true }, props: true },
          // 工序字典
          { path: 'work-process', name: 'ConstructionWorkProcess',  component: () => import('@/views/construction/work-process/index.vue'), meta: { title: '工序字典' } },
          // 施工发包
          { path: 'external-work',     name: 'ConstructionExternalWork',        component: () => import('@/views/construction/external-work/index.vue'), meta: { title: '施工发包' } },
          { path: 'external-work/:id', name: 'ConstructionExternalWorkDetail', component: () => import('@/views/construction/external-work/Detail.vue'),  meta: { title: '发包详情', hidden: true }, props: true },
          // 外部供应商投标（无 auth 要求,放 MainLayout 内但不影响登录态)
          { path: 'external-work/bid/:id', name: 'ConstructionBidForm', component: () => import('@/views/construction/external-work/BidForm.vue'), meta: { title: '投标申请', hidden: true }, props: true },
          // ---- 工序管理 (C 方案: 现场活, 归施工) ----
          { path: 'process/templates', name: 'ConstructionProcessTemplates', component: () => import('@/views/process/TemplateList.vue'), meta: { title: '工序模板' } },
          { path: 'process/instances', name: 'ConstructionProcessInstances', component: () => import('@/views/process/InstanceList.vue'), meta: { title: '工序实例' } },
          { path: 'process/inspections', name: 'ConstructionProcessInspections', component: () => import('@/views/process/InspectionList.vue'), meta: { title: '验收记录' } },
          { path: 'process/instances/detail/:id', name: 'ConstructionProcessInstanceDetail', component: () => import('@/views/process/InstanceDetail.vue'), meta: { title: '工序详情', hidden: true }, props: true }
        ]
      },
      // ---- 维修中心 (V0.5.5 改名: 售后服务 → 维修中心) ----
      {
        path: 'maintenance',
        name: 'Maintenance',
        redirect: '/maintenance/work-orders',
        alias: '/maintenance',
        meta: { title: '维修中心', icon: 'SetUp' },
        children: [
          { path: 'work-orders', name: 'MaintenanceWorkOrders', component: () => import('@/views/maintenance/WorkOrderList.vue'), meta: { title: '维修工单' } },
          { path: 'work-orders/:id', name: 'MaintenanceWorkOrderDetail', component: () => import('@/views/maintenance/WorkOrderDetail.vue'), meta: { title: '工单详情', hidden: true }, props: true },
          { path: 'work-orders/create', name: 'MaintenanceWorkOrderCreate', component: () => import('@/views/maintenance/WorkOrderCreate.vue'), meta: { title: '创建工单', hidden: true } },
          { path: 'repairs', name: 'MaintenanceRepairs', component: () => import('@/views/maintenance/RepairList.vue'), meta: { title: '返修管理' } },
          { path: 'repairs/:id', name: 'MaintenanceRepairDetail', component: () => import('@/views/maintenance/RepairDetail.vue'), meta: { title: '返修详情', hidden: true }, props: true },
          { path: 'repairs/create', name: 'MaintenanceRepairCreate', component: () => import('@/views/maintenance/RepairCreate.vue'), meta: { title: '新建返修', hidden: true } },
          { path: 'stats', name: 'MaintenanceStats', component: () => import('@/views/maintenance/Stats.vue'), meta: { title: '维修统计' } },
          { path: 'kanban', name: 'MaintenanceKanban', component: () => import('@/views/maintenance/Kanban.vue'), meta: { title: '维修看板' } },
          // V0.5.7 块3 — 返修进度查询 (内嵌给财务/管理员查看)
          { path: 'portal-repair', name: 'MaintenancePortalRepair', component: () => import('@/views/portal/Repair.vue'), meta: { title: '返修进度查询' } }
        ]
      },
      // ---- 公开直链 /portal/repair (外部客户用, 不进菜单) ----
      {
        path: 'portal/repair',
        name: 'PortalRepair',
        component: () => import('@/views/portal/Repair.vue'),
        meta: { title: '返修进度查询', public: true, noAuth: true, hidden: true },
      },
      // ---- 公开直链 /portal/tender (供应商投标, 不进菜单) ----
      {
        path: 'portal/tender',
        name: 'PortalTender',
        component: () => import('@/views/portal/tender/Index.vue'),
        meta: { title: '招标中心 · 供应商门户', public: true, noAuth: true, hidden: true },
      },
      {
        path: 'portal/tender/:token',
        name: 'PortalTenderBid',
        component: () => import('@/views/portal/tender/BidForm.vue'),
        meta: { title: '在线投标', public: true, noAuth: true, hidden: true },
      },
      // ---- 旧 service 路径重定向到 maintenance (V0.5.5 兼容期) ----
      {
        path: 'service',
        redirect: '/maintenance/work-orders',
        meta: { hidden: true }
      },
      // ---- 报销管理 ----
      {
        path: 'expense',
        name: 'Expense',
        redirect: '/expense/list',
        alias: '/expense',
        meta: { title: '报销管理', icon: 'Money' },
        children: [
          { path: 'list', name: 'ExpenseList', component: () => import('@/views/expense/index.vue'), meta: { title: '报销列表' } },
          { path: 'apply', name: 'ExpenseApply', component: () => import('@/views/expense/Apply.vue'), meta: { title: '申请报销' } },
          { path: 'approval', name: 'ExpenseApproval', component: () => import('@/views/expense/Approval.vue'), meta: { title: '审批管理' } }
        ]
      },
      // ---- 车辆管理 ----
      {
        path: 'vehicle',
        name: 'Vehicle',
        redirect: '/vehicle/fleet',
        alias: '/vehicle',
        meta: { title: '车辆管理', icon: 'Van' },
        children: [
          { path: 'fleet', name: 'VehicleFleet', component: () => import('@/views/vehicle/index.vue'), meta: { title: '车辆档案' } },
          { path: 'apply', name: 'VehicleApply', component: () => import('@/views/vehicle/Apply.vue'), meta: { title: '用车申请' } },
          { path: 'dispatch', name: 'VehicleDispatch', component: () => import('@/views/vehicle/Dispatch.vue'), meta: { title: '调度管理' } },
          { path: 'insurance', name: 'VehicleInsurance', component: () => import('@/views/vehicle/Insurance.vue'), meta: { title: '保险记录' } },
          { path: 'maintenance', name: 'VehicleMaintenance', component: () => import('@/views/vehicle/Maintenance.vue'), meta: { title: '保养记录' } },
          { path: 'fuel-card', name: 'VehicleFuelCard', component: () => import('@/views/vehicle/FuelCard.vue'), meta: { title: '油卡管理' } }
        ]
      },
      // ---- 库存管理 (P1) ----
      {
        path: 'inventory',
        name: 'Inventory',
        redirect: '',
        alias: '/inventory',
        meta: { title: '库存管理', icon: 'Box' },
        children: [
          { path: '', name: 'InventoryStock', component: () => import('@/views/inventory/index.vue'), meta: { title: '库存总览' } },
          { path: 'inout', name: 'InventoryInOut', component: () => import('@/views/inventory/InOut.vue'), meta: { title: '出入库明细' } },
          { path: 'inbound-order', name: 'InventoryInboundOrder', component: () => import('@/views/inventory/InboundOrder.vue'), meta: { title: '入库单' } },
          { path: 'outbound-order', name: 'InventoryOutboundOrder', component: () => import('@/views/inventory/OutboundOrder.vue'), meta: { title: '出库单' } },
          { path: 'material-request', name: 'InventoryMaterialRequest', component: () => import('@/views/inventory/MaterialRequest.vue'), meta: { title: '领料单' } },
          { path: 'material-return', name: 'InventoryMaterialReturn', component: () => import('@/views/inventory/MaterialReturn.vue'), meta: { title: '领料归还单' } }
        ]
      },
      // ---- 财务管理 (P1) ----
      {
        path: 'finance',
        name: 'Finance',
        redirect: '/finance/overview',
        alias: '/finance',
        meta: { title: '财务管理', icon: 'Wallet' },
        children: [
          { path: 'overview', name: 'FinanceOverview', component: () => import('@/views/finance/index.vue'), meta: { title: '财务概览' } },
          { path: 'receipt', name: 'FinanceReceipt', component: () => import('@/views/finance/Receipt.vue'), meta: { title: '收款单' } },
          { path: 'payment', name: 'FinancePayment', component: () => import('@/views/finance/Payment.vue'), meta: { title: '付款单' } },
          { path: 'receivable', name: 'FinanceReceivable', component: () => import('@/views/finance/Receivable.vue'), meta: { title: '应收账款' } },
          { path: 'payable', name: 'FinancePayable', component: () => import('@/views/finance/Payable.vue'), meta: { title: '应付账款' } },
          { path: 'supplier-ledger', name: 'FinanceSupplierLedger', component: () => import('@/views/finance/supplier-ledger.vue'), meta: { title: '供应商总账' } },
          { path: 'customer-ledger', name: 'FinanceCustomerLedger', component: () => import('@/views/finance/customer-ledger.vue'), meta: { title: '客户总账' } },
          // V0.5.7 块4 — 维修成本报表
          { path: 'repair-cost', name: 'FinanceRepairCost', component: () => import('@/views/finance/RepairCostReport.vue'), meta: { title: '售后成本报表' } }
        ]
      },
      // ---- 供应商管理 (V0.4.2) ----
      {
        path: 'supplier',
        name: 'Supplier',
        redirect: '/supplier/list',
        alias: '/supplier',
        meta: { title: '供应商管理', icon: 'OfficeBuilding' },
        children: [
          { path: 'list', name: 'SupplierList', component: () => import('@/views/supplier/index.vue'), meta: { title: '供应商列表' } },
          { path: ':id', name: 'SupplierDetail', component: () => import('@/views/supplier/Detail.vue'), meta: { title: '供应商详情', hidden: true }, props: true }
        ]
      },
      // ---- 对外报价 (V0.4.2) - 已移到「销售管理」下, 保留 /external-quote 兼容路径 ----
      // ---- 工序管理 (V1.1) - 已移到「施工管理」下, 保留 /process/* 兼容路径 ----
      // ---- 审批中心 (v0.3.10) - 3 模块分类 ----
      {
        path: 'approval',
        name: 'Approval',
        redirect: '/approval/finance',
        alias: '/approval',
        meta: { title: '审批中心', icon: 'CircleCheck' },
        children: [
          { path: 'finance', name: 'ApprovalFinance', component: () => import('@/views/approval/finance/Index.vue'), meta: { title: '财务审批' } },
          { path: 'operation', name: 'ApprovalOperation', component: () => import('@/views/approval/operation/Index.vue'), meta: { title: '运营审批' } },
          { path: 'project', name: 'ApprovalProject', component: () => import('@/views/approval/project/Index.vue'), meta: { title: '项目审批' } }
        ]
      },
      // ---- 公司网盘 (P1) ----
      {
        path: 'disk',
        name: 'Disk',
        component: () => import('@/views/disk/index.vue'),
        meta: { title: '公司网盘', icon: 'FolderOpened' }
      },
      // ---- 知识库 (P1) ----
      {
        path: 'knowledge',
        name: 'Knowledge',
        redirect: '/knowledge/list',
        alias: '/knowledge',
        meta: { title: '知识库', icon: 'Reading' },
        children: [
          { path: 'list', name: 'KnowledgeList', component: () => import('@/views/knowledge/index.vue'), meta: { title: '知识列表' } }
        ]
      },
      // ---- 数据大屏 (P2) ----
      {
        path: 'screen',
        name: 'Screen',
        component: () => import('@/views/screen/index.vue'),
        meta: { title: '数据大屏', icon: 'DataAnalysis' }
      },
      // ---- 消息中心 ----
      {
        path: 'message',
        name: 'Message',
        redirect: '/message/list',
        alias: '/message',
        meta: { title: '消息中心', icon: 'Bell' },
        children: [
          { path: 'list', name: 'MessageList', component: () => import('@/views/message/index.vue'), meta: { title: '消息列表' } }
        ]
      },
      // ---- 系统设置 ----
      {
        path: 'settings',
        name: 'Settings',
        redirect: '/settings/organization',
        alias: '/settings',
        meta: { title: '系统设置', icon: 'Setting' },
        children: [
          { path: 'profile', name: 'SettingsProfile', component: () => import('@/views/settings/Profile.vue'), meta: { title: '个人信息', hidden: true } },
          { path: 'password', name: 'SettingsPassword', component: () => import('@/views/settings/Password.vue'), meta: { title: '修改密码', hidden: true } },
          { path: 'my-permissions', name: 'SettingsMyPermissions', component: () => import('@/views/settings/MyPermissions.vue'), meta: { title: '我的权限' } },
          { path: 'organization', name: 'SettingsOrg', component: () => import('@/views/settings/Organization.vue'), meta: { title: '组织权限' } },
          { path: 'role', name: 'SettingsRole', component: () => import('@/views/settings/role/Index.vue'), meta: { title: '角色管理', permission: 'system.role' } },
          { path: 'role/matrix', name: 'SettingsRoleMatrix', component: () => import('@/views/settings/role/Matrix.vue'), meta: { title: '权限矩阵', permission: 'system.role' } },
          { path: 'user', name: 'SettingsUser', component: () => import('@/views/settings/user/Index.vue'), meta: { title: '用户管理', permission: 'system.role' } },
          { path: 'field-mask', name: 'SettingsFieldMask', component: () => import('@/views/settings/FieldMask.vue'), meta: { title: '字段脱敏', permission: 'system.role' } },
          { path: 'permission-log', name: 'SettingsPermissionLog', component: () => import('@/views/settings/PermissionLog.vue'), meta: { title: '权限变更历史', permission: 'system.role' } },
          { path: 'approval', name: 'SettingsApproval', component: () => import('@/views/settings/approval/Index.vue'), meta: { title: '审批引擎' } },
          { path: 'log', name: 'SettingsLog', component: () => import('@/views/settings/log/Index.vue'), meta: { title: '系统日志' } },
          { path: 'backup', name: 'SettingsBackup', component: () => import('@/views/settings/Backup.vue'), meta: { title: '数据管理' } },
          // V0.5.7 块A — 系统初始化向导
          { path: 'wizard', name: 'SettingsWizard', component: () => import('@/views/settings/SetupWizard.vue'), meta: { title: '系统初始化' } },
          // V0.5.7 块B — 数据字典中心
          { path: 'dict', name: 'SettingsDict', component: () => import('@/views/settings/SystemDict.vue'), meta: { title: '数据字典' } },
          // V0.5.7 块C — 系统监控面板
          { path: 'monitor', name: 'SettingsMonitor', component: () => import('@/views/settings/SystemMonitor.vue'), meta: { title: '系统监控' } }
        ]
      }
    ]
  },
  // 错误页（独立 layout,不走 MainLayout）
  {
    path: '/error/404',
    name: 'Error404',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', requiresAuth: false }
  },
  {
    path: '/error/500',
    name: 'Error500',
    component: () => import('@/views/error/500.vue'),
    meta: { title: '服务异常', requiresAuth: false }
  },
  {
    path: '/error/network',
    name: 'ErrorNetwork',
    component: () => import('@/views/error/NetworkError.vue'),
    meta: { title: '网络断开', requiresAuth: false }
  },
  // 法律页（不需登录）
  {
    path: '/legal/agreement',
    name: 'LegalAgreement',
    component: () => import('@/views/legal/Agreement.vue'),
    meta: { title: '用户服务协议', requiresAuth: false }
  },
  {
    path: '/legal/privacy',
    name: 'LegalPrivacy',
    component: () => import('@/views/legal/Privacy.vue'),
    meta: { title: '隐私政策', requiresAuth: false }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '403 权限不足' }
  },
  // 404 兜底（必须在最后）
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 白名单：不需要登录就能访问的页面
const WHITE_LIST = [
  '/login',
  '/error/404',
  '/error/500',
  '/error/network',
  '/legal/agreement',
  '/legal/privacy',
  '/portal/repair',  // V0.5.7 块3 — 客户公开查询
  '/portal/tender',  // V0.6.0 — 供应商招标门户首页
  // /portal/tender/:token — 公开投标页, 路径级白名单(用 to.matched[0]?.path 通配)见 beforeEach
]

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  // 用 systemConfigStore 拿动态系统名；如果未加载（登录页/初次进入），用兜底
  try {
    const { useSystemConfigStore } = await import('@/stores/systemConfig')
    const store = useSystemConfigStore()
    const sysName = store.sysConfig.systemName || 'OA 办公系统'
    document.title = to.meta.title ? `${to.meta.title} - ${sysName}` : sysName
  } catch {
    document.title = to.meta.title ? `${to.meta.title} - OA 办公系统` : 'OA 办公系统'
  }

  const token = getToken()
  // 白名单匹配: 精确路径 + 前缀通配(noAuth 路由用, 任意 token 后路径)
  const isWhiteList = WHITE_LIST.includes(to.path)
    || to.meta?.requiresAuth === false
    || to.meta?.noAuth === true
    || to.path.startsWith('/portal/tender/')  // V0.6.0 供应商投标详情页免登录

  // 白名单页面直接放行
  if (isWhiteList) {
    // 已登录用户访问 /login → 直接跳到首页（避免来回跳转）
    if (to.path === '/login' && token) {
      next('/')
      return
    }
    // 离开业务页面 → 停止闲置计时
    stopIdleMonitor()
    next()
    return
  }

  // ⚠️ 关键修复：兜底防御 — 修复 localStorage token/userInfo 不一致问题
  // 场景：单独 removeToken() 后,userInfo 残留,守卫会误判为已登录
  if (!token) {
    // 清理任何残留的 userInfo,保证状态一致
    try {
      const { clearAuth } = await import('@/utils/auth')
      clearAuth()
    } catch { /* 忽略 */ }
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 有 token — 必须**先验证 token 在后端真的有效**,再放行
  // 避免: token 过期 → 守卫通过 → 进入 dashboard → 多个组件并发请求触发一堆 401 弹框
  const userStore = useUserStore()
  try {
    if (!userStore.userInfo) {
      await userStore.getUserInfoAction()
    }
  } catch {
    // token 失效 → 清空一切 + 跳 login
    stopIdleMonitor()
    try { userStore.logout() } catch { /* 忽略 */ }
    try {
      const { clearAuth } = await import('@/utils/auth')
      clearAuth()
    } catch { /* 忽略 */ }
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 业务页面验证通过 → 启动/重置闲置计时(30分钟)
  startIdleMonitor()

  next()
})

router.afterEach(() => {
  NProgress.done()
})

// Handle chunk loading failures (e.g. network issues after deployment)
router.onError((error, to) => {
  if (error.message.includes('Failed to fetch dynamically imported module') || error.message.includes('Importing a module script failed')) {
    ElMessage.error('页面加载失败，正在刷新...')
    window.location.href = to.fullPath
  }
})

export default router
