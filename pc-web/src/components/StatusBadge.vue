<!--
  StatusBadge - 状态标签组件
  用法: <StatusBadge :status="'approved'" />
-->
<template>
  <span :class="['status-badge', `status-${status}`]">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    status: 'pending' | 'approved' | 'rejected' | 'draft'
  }>(),
  {
    status: 'draft',
  },
)

const statusMap: Record<string, string> = {
  pending: '待审批',
  approved: '已通过',
  rejected: '已拒绝',
  draft: '草稿',
}

const label = computed(() => statusMap[props.status] || props.status)
</script>

<style lang="scss" scoped>
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 18px;
}
.status-pending {
  background: #fdf6ec;
  color: #e6a23c;
}
.status-approved {
  background: #f0f9eb;
  color: #67c23a;
}
.status-rejected {
  background: #fef0f0;
  color: #f56c6c;
}
.status-draft {
  background: #f4f4f5;
  color: #909399;
}
</style>
