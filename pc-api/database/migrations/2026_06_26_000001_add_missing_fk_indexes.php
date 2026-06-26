<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

/**
 * V0.6.1 — 全局外键索引补全 + 高频查询字段索引
 *
 * 审计范围: 所有 database/migrations/*.php
 * 审计方法: 逐一检查 foreignId() / unsignedBigInteger()->foreign() 列是否有对应索引
 *
 * PostgreSQL 特性: FK 约束不自动创建引用列索引，必须手动添加。
 * 缺少索引的 FK 列在 JOIN / WHERE 时会导致 Seq Scan，严重影响性能。
 *
 * ---- 已有索引的 FK (跳过) ----
 *  repair_orders:        project_id ✅, customer_id ✅, source_id ✅, received_by ✅
 *  work_orders:          customer_id ✅, project_id ✅, assigned_to ✅, converted_repair_id ✅
 *  expense_claims:       user_id ✅, project_id ✅, approver_id ✅
 *  stock_records:        inventory_item_id ✅, warehouse_id ✅, operator_id ✅
 *  inventory_items:      category_id ✅, warehouse_id ✅
 *  purchase_requirements: project_id ✅ (line 34)
 *  purchase_plans:       project_id ✅ (line 34)
 *  project_budgets:      project_id ✅ (composite idx_pb_project)
 *  project_actual_costs: project_id ✅ (composite idx_pac_project)
 *  project_budget_items: budget_id ✅ (composite idx_pbi_budget)
 *
 * ---- 本次新增 ----
 *  A) follow_up_records — customer_id, user_id
 *  B) customers — assigned_user_id, category(客户等级)
 *  C) work_orders — priority (单独索引), service_type
 *  D) purchase_contracts — plan_id, project_id, supplier_id, signer_id
 *  E) purchase_payment_requests — contract_id, supplier_id, applicant_id, approver_id
 *  F) purchase_payments — payment_request_id, contract_id, supplier_id, operator_id
 *  G) purchase_shipments — contract_id, supplier_id
 *  H) purchase_approvals — applicant_id, approver_id
 *  I) purchase_plans — requirement_id, submitter_id, approver_id
 *  J) purchase_requirements — reviewed_by
 *  K) tender_projects — project_id, rfq_id, created_by, awarded_supplier_id
 *  L) tender_bids — submitter_user_id
 *  M) tender_bid_items — tender_bid_id
 *  N) tender_attachments — tender_bid_id, uploaded_by_user_id, uploaded_by_supplier_id
 *
 * 注意: customers.level 列在当前 schema 中不存在（客户等级通过 category 枚举字段实现），
 *       故改为对 customers.category 建索引。
 */
return new class extends Migration
{
    public function up(): void
    {
        // ================================================================
        // A) follow_up_records: 客户跟进记录 (高频按客户 / 跟进人查询)
        // ================================================================
        $this->addIndex('follow_up_records', 'follow_up_records_customer_id_index',
            'CREATE INDEX follow_up_records_customer_id_index ON follow_up_records (customer_id)');
        $this->addIndex('follow_up_records', 'follow_up_records_user_id_index',
            'CREATE INDEX follow_up_records_user_id_index ON follow_up_records (user_id)');

        // ================================================================
        // B) customers: 客户主表
        // ================================================================
        // assigned_user_id — FK to users, 按负责人筛选客户列表
        $this->addIndex('customers', 'customers_assigned_user_id_index',
            'CREATE INDEX customers_assigned_user_id_index ON customers (assigned_user_id)');
        // category — 客户等级 (vip/normal/potential), 高频筛选字段
        $this->addIndex('customers', 'customers_category_index',
            'CREATE INDEX customers_category_index ON customers (category)');
        // status — 客户状态
        $this->addIndex('customers', 'customers_status_index',
            'CREATE INDEX customers_status_index ON customers (status)');

        // ================================================================
        // C) work_orders: 工单 (priority 单独索引 + service_type)
        // ================================================================
        // priority — 已有复合索引 wo_status_pri_idx，但单独按优先级查询需要独立索引
        $this->addIndex('work_orders', 'work_orders_priority_index',
            'CREATE INDEX work_orders_priority_index ON work_orders (priority)');
        // service_type — 上门/到店/远程
        $this->addIndex('work_orders', 'work_orders_service_type_index',
            'CREATE INDEX work_orders_service_type_index ON work_orders (service_type)');

        // ================================================================
        // D) purchase_contracts: 采购合同
        // ================================================================
        $this->addIndex('purchase_contracts', 'purchase_contracts_plan_id_index',
            'CREATE INDEX purchase_contracts_plan_id_index ON purchase_contracts (plan_id)');
        $this->addIndex('purchase_contracts', 'purchase_contracts_project_id_index',
            'CREATE INDEX purchase_contracts_project_id_index ON purchase_contracts (project_id)');
        // supplier_id 已在复合索引 [status, supplier_id] 的前缀中，但单独查询仍需独立索引
        $this->addIndex('purchase_contracts', 'purchase_contracts_supplier_id_index',
            'CREATE INDEX purchase_contracts_supplier_id_index ON purchase_contracts (supplier_id)');
        $this->addIndex('purchase_contracts', 'purchase_contracts_signer_id_index',
            'CREATE INDEX purchase_contracts_signer_id_index ON purchase_contracts (signer_id)');

        // ================================================================
        // E) purchase_payment_requests: 付款申请
        // ================================================================
        $this->addIndex('purchase_payment_requests', 'ppr_contract_id_index',
            'CREATE INDEX ppr_contract_id_index ON purchase_payment_requests (contract_id)');
        $this->addIndex('purchase_payment_requests', 'ppr_supplier_id_index',
            'CREATE INDEX ppr_supplier_id_index ON purchase_payment_requests (supplier_id)');
        $this->addIndex('purchase_payment_requests', 'ppr_applicant_id_index',
            'CREATE INDEX ppr_applicant_id_index ON purchase_payment_requests (applicant_id)');
        $this->addIndex('purchase_payment_requests', 'ppr_approver_id_index',
            'CREATE INDEX ppr_approver_id_index ON purchase_payment_requests (approver_id)');

        // ================================================================
        // F) purchase_payments: 付款记录
        // ================================================================
        $this->addIndex('purchase_payments', 'purchase_payments_payment_request_id_index',
            'CREATE INDEX purchase_payments_payment_request_id_index ON purchase_payments (payment_request_id)');
        $this->addIndex('purchase_payments', 'purchase_payments_contract_id_index',
            'CREATE INDEX purchase_payments_contract_id_index ON purchase_payments (contract_id)');
        $this->addIndex('purchase_payments', 'purchase_payments_supplier_id_index',
            'CREATE INDEX purchase_payments_supplier_id_index ON purchase_payments (supplier_id)');
        $this->addIndex('purchase_payments', 'purchase_payments_operator_id_index',
            'CREATE INDEX purchase_payments_operator_id_index ON purchase_payments (operator_id)');

        // ================================================================
        // G) purchase_shipments: 发货单
        // ================================================================
        $this->addIndex('purchase_shipments', 'purchase_shipments_contract_id_index',
            'CREATE INDEX purchase_shipments_contract_id_index ON purchase_shipments (contract_id)');
        $this->addIndex('purchase_shipments', 'purchase_shipments_supplier_id_index',
            'CREATE INDEX purchase_shipments_supplier_id_index ON purchase_shipments (supplier_id)');

        // ================================================================
        // H) purchase_approvals: 采购审批
        // ================================================================
        $this->addIndex('purchase_approvals', 'purchase_approvals_applicant_id_index',
            'CREATE INDEX purchase_approvals_applicant_id_index ON purchase_approvals (applicant_id)');
        $this->addIndex('purchase_approvals', 'purchase_approvals_approver_id_index',
            'CREATE INDEX purchase_approvals_approver_id_index ON purchase_approvals (approver_id)');

        // ================================================================
        // I) purchase_plans: 采购计划 (requirement_id, submitter_id, approver_id)
        // ================================================================
        $this->addIndex('purchase_plans', 'purchase_plans_requirement_id_index',
            'CREATE INDEX purchase_plans_requirement_id_index ON purchase_plans (requirement_id)');
        $this->addIndex('purchase_plans', 'purchase_plans_submitter_id_index',
            'CREATE INDEX purchase_plans_submitter_id_index ON purchase_plans (submitter_id)');
        $this->addIndex('purchase_plans', 'purchase_plans_approver_id_index',
            'CREATE INDEX purchase_plans_approver_id_index ON purchase_plans (approver_id)');

        // ================================================================
        // J) purchase_requirements: 采购需求 (reviewed_by)
        // ================================================================
        $this->addIndex('purchase_requirements', 'purchase_requirements_reviewed_by_index',
            'CREATE INDEX purchase_requirements_reviewed_by_index ON purchase_requirements (reviewed_by)');

        // ================================================================
        // K) tender_projects: 招标项目
        // ================================================================
        $this->addIndex('tender_projects', 'tender_projects_project_id_index',
            'CREATE INDEX tender_projects_project_id_index ON tender_projects (project_id)');
        $this->addIndex('tender_projects', 'tender_projects_rfq_id_index',
            'CREATE INDEX tender_projects_rfq_id_index ON tender_projects (rfq_id)');
        $this->addIndex('tender_projects', 'tender_projects_created_by_index',
            'CREATE INDEX tender_projects_created_by_index ON tender_projects (created_by)');
        $this->addIndex('tender_projects', 'tender_projects_awarded_supplier_id_index',
            'CREATE INDEX tender_projects_awarded_supplier_id_index ON tender_projects (awarded_supplier_id)');

        // ================================================================
        // L) tender_bids: 投标 (submitter_user_id)
        // ================================================================
        // tender_project_id + supplier_id 已被 UNIQUE 约束索引覆盖
        $this->addIndex('tender_bids', 'tender_bids_submitter_user_id_index',
            'CREATE INDEX tender_bids_submitter_user_id_index ON tender_bids (submitter_user_id)');

        // ================================================================
        // M) tender_bid_items: 投标明细
        // ================================================================
        $this->addIndex('tender_bid_items', 'tender_bid_items_tender_bid_id_index',
            'CREATE INDEX tender_bid_items_tender_bid_id_index ON tender_bid_items (tender_bid_id)');

        // ================================================================
        // N) tender_attachments: 招标附件
        // ================================================================
        // tender_project_id 已被复合索引 [tender_project_id, category] 的前缀覆盖
        $this->addIndex('tender_attachments', 'tender_attachments_tender_bid_id_index',
            'CREATE INDEX tender_attachments_tender_bid_id_index ON tender_attachments (tender_bid_id)');
        $this->addIndex('tender_attachments', 'tender_attachments_uploaded_by_user_id_index',
            'CREATE INDEX tender_attachments_uploaded_by_user_id_index ON tender_attachments (uploaded_by_user_id)');
        $this->addIndex('tender_attachments', 'tender_attachments_uploaded_by_supplier_id_index',
            'CREATE INDEX tender_attachments_uploaded_by_supplier_id_index ON tender_attachments (uploaded_by_supplier_id)');
    }

    public function down(): void
    {
        $indexes = [
            // A
            'follow_up_records_customer_id_index',
            'follow_up_records_user_id_index',
            // B
            'customers_assigned_user_id_index',
            'customers_category_index',
            'customers_status_index',
            // C
            'work_orders_priority_index',
            'work_orders_service_type_index',
            // D
            'purchase_contracts_plan_id_index',
            'purchase_contracts_project_id_index',
            'purchase_contracts_supplier_id_index',
            'purchase_contracts_signer_id_index',
            // E
            'ppr_contract_id_index',
            'ppr_supplier_id_index',
            'ppr_applicant_id_index',
            'ppr_approver_id_index',
            // F
            'purchase_payments_payment_request_id_index',
            'purchase_payments_contract_id_index',
            'purchase_payments_supplier_id_index',
            'purchase_payments_operator_id_index',
            // G
            'purchase_shipments_contract_id_index',
            'purchase_shipments_supplier_id_index',
            // H
            'purchase_approvals_applicant_id_index',
            'purchase_approvals_approver_id_index',
            // I
            'purchase_plans_requirement_id_index',
            'purchase_plans_submitter_id_index',
            'purchase_plans_approver_id_index',
            // J
            'purchase_requirements_reviewed_by_index',
            // K
            'tender_projects_project_id_index',
            'tender_projects_rfq_id_index',
            'tender_projects_created_by_index',
            'tender_projects_awarded_supplier_id_index',
            // L
            'tender_bids_submitter_user_id_index',
            // M
            'tender_bid_items_tender_bid_id_index',
            // N
            'tender_attachments_tender_bid_id_index',
            'tender_attachments_uploaded_by_user_id_index',
            'tender_attachments_uploaded_by_supplier_id_index',
        ];

        foreach ($indexes as $idx) {
            DB::statement("DROP INDEX IF EXISTS {$idx}");
        }
    }

    /**
     * 幂等添加索引: 先检查 pg_indexes，不存在才创建
     */
    private function addIndex(string $table, string $indexName, string $sql): void
    {
        $exists = DB::selectOne(
            "SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = ? AND indexname = ?",
            [$table, $indexName]
        );
        if ($exists === null) {
            DB::statement($sql);
        }
    }
};
