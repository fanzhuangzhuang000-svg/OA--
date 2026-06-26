<template>
  <div class="content-card">
    <div class="table-header">
      <span class="table-title">验收记录列表</span>
      <span class="table-meta">共 {{ total }} 条</span>
    </div>

    <el-table
      v-loading="loading"
      :data="list"
      stripe
      border
      style="width: 100%"
      :row-style="{ height: '50px' }"
      :cell-style="{ padding: '0 8px' }"
      :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
    >
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="project_name" label="项目名" min-width="180" show-overflow-tooltip />
      <el-table-column prop="template_name" label="工序名" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.template_name">{{ row.template_name }}</span>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="inspector_name" label="验收人" min-width="100" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.inspector_name">{{ row.inspector_name }}</span>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="验收时间" min-width="160">
        <template #default="{ row }">
          <span>{{ formatDate(row.inspected_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="结果" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="resultTagType(row.result)" effect="dark" size="small">
            {{ resultLabel(row.result) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="comment" label="备注" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.comment">{{ row.comment }}</span>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="defects" label="整改项" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.defects" class="defect-text">{{ row.defects }}</span>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            size="small"
            :disabled="!row.process_instance_id"
            @click="emit('view', row)"
          >
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrap">
      <el-pagination
        :current-page="page"
        :page-size="perPage"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="(p: number) => emit('pageChange', p)"
        @size-change="(s: number) => emit('sizeChange', s)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Inspection } from './types'
import { formatDate, resultLabel, resultTagType } from './types'

// v0.3.25 抽自 process/InspectionList.vue:118-200
defineProps<{
  list: Inspection[]
  loading: boolean
  total: number
  page: number
  perPage: number
}>()

const emit = defineEmits<{
  (e: 'view', row: Inspection): void
  (e: 'pageChange', p: number): void
  (e: 'sizeChange', s: number): void
}>()
</script>

<style lang="scss" scoped>
.content-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.table-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  border-left: 3px solid #0C447C;
  padding-left: 8px;
}
.table-meta {
  font-size: 12px;
  color: #909399;
}
.muted { color: #c0c4cc; }
.defect-text { color: #A32D2D; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
