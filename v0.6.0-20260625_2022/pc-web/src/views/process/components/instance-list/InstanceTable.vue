<template>
  <el-table
    :data="list"
    stripe
    border
    v-loading="loading"
    :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
    :cell-style="{ height: '50px', padding: '4px 0' }"
    style="width: 100%"
  >
    <el-table-column prop="id" label="ID" width="70" align="center">
      <template #default="{ row }">
        <span class="id-text">#{{ row.id }}</span>
      </template>
    </el-table-column>
    <el-table-column label="项目名" min-width="180" show-overflow-tooltip>
      <template #default="{ row }">
        <span class="link-text" @click="emit('viewProject', row)">{{ row.project_name || '-' }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="template_name" label="工序名" min-width="160" show-overflow-tooltip />
    <el-table-column label="负责人" min-width="100">
      <template #default="{ row }">
        <span>{{ row.assignee_name || '-' }}</span>
      </template>
    </el-table-column>
    <el-table-column label="进度" width="180">
      <template #default="{ row }">
        <el-progress
          :percentage="row.progress || 0"
          :color="progressColor(row.progress)"
          :stroke-width="12"
          :format="(p: number) => p + '%'"
        />
      </template>
    </el-table-column>
    <el-table-column label="计划工期" min-width="200">
      <template #default="{ row }">
        <span class="date-text">
          {{ row.planned_start ? row.planned_start.slice(0, 10) : '-' }}
          <span class="date-sep">~</span>
          {{ row.planned_end ? row.planned_end.slice(0, 10) : '-' }}
        </span>
      </template>
    </el-table-column>
    <el-table-column label="实际工期" min-width="200">
      <template #default="{ row }">
        <span class="date-text">
          <template v-if="row.actual_start || row.actual_end">
            {{ row.actual_start ? row.actual_start.slice(0, 10) : '-' }}
            <span class="date-sep">~</span>
            {{ row.actual_end ? row.actual_end.slice(0, 10) : '-' }}
          </template>
          <span v-else class="muted">-</span>
        </span>
      </template>
    </el-table-column>
    <el-table-column label="状态" width="110" align="center">
      <template #default="{ row }">
        <el-tag :type="statusTagType(row.status)" effect="light" size="small">
          <el-icon v-if="row.is_overdue" :size="11" style="vertical-align: -1px; margin-right: 2px"><Warning /></el-icon>
          {{ statusLabel(row.status) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="280" fixed="right" align="center">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="emit('view', row)">详情</el-button>
        <el-button
          v-if="row.status === 'in_progress' || row.status === 'pending' || row.is_overdue"
          link
          type="success"
          size="small"
          @click="emit('accept', row)"
        >接受</el-button>
        <el-button
          v-if="row.status === 'in_progress' || row.status === 'pending'"
          link
          type="danger"
          size="small"
          @click="emit('reject', row)"
        >驳回</el-button>
        <el-button
          v-if="row.status === 'in_progress'"
          link
          type="warning"
          size="small"
          @click="emit('progress', row)"
        >更新进度</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import { Warning } from '@element-plus/icons-vue'
import type { Instance } from './types'
import { progressColor, statusLabel, statusTagType, STATUS_TAG_TYPE_MAP } from './types'

// v0.3.19 抽自 process/InstanceList.vue:50-141
defineProps<{
  list: Instance[]
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'view', row: Instance): void
  (e: 'viewProject', row: Instance): void
  (e: 'accept', row: Instance): void
  (e: 'reject', row: Instance): void
  (e: 'progress', row: Instance): void
}>()
</script>

<style lang="scss" scoped>
.id-text {
  font-family: 'SF Mono', Consolas, monospace;
  color: #0C447C; font-weight: 600;
}
.link-text {
  color: #0C447C; cursor: pointer; font-weight: 500;
  &:hover { text-decoration: underline; }
}
.date-text {
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 12px; color: #606266;
  .date-sep { color: #c0c4cc; margin: 0 4px; }
}
.muted { color: #c0c4cc; }
</style>
