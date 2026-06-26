<template>
  <div
    class="pipeline-card"
    :class="{ 'card-dragging': dragging }"
    draggable="true"
    @dragstart="$emit('dragstart', $event, card, fromStage)"
    @dragend="$emit('dragend')"
    @click="$emit('click', card)"
  >
    <div class="card-row card-row-1">
      <span class="card-name" :title="card.name">{{ card.name }}</span>
      <el-tag v-if="card.industry" size="small" type="info" effect="plain" round>
        {{ card.industry }}
      </el-tag>
    </div>
    <div class="card-row card-row-2">
      <div class="assign-user">
        <el-avatar
          v-if="card.assigned_user"
          :size="20"
          :src="card.assigned_user.avatar || undefined"
        >
          {{ (card.assigned_user.name || '?').slice(0, 1) }}
        </el-avatar>
        <el-avatar v-else :size="20">?</el-avatar>
        <span class="assign-name">{{ card.assigned_user?.name || '未分配' }}</span>
      </div>
      <div class="amount">¥ {{ formatAmount(card.expected_amount) }}</div>
    </div>
    <div class="card-row card-row-3">
      <span class="last-ago">
        <el-icon :size="12"><Clock /></el-icon>
        {{ card.last_follow_ago ? card.last_follow_ago + '前跟进' : '尚无跟进' }}
      </span>
      <span v-if="card.expected_close_date" class="close-date">
        预计 {{ card.expected_close_date }}
      </span>
    </div>
    <div v-if="card.tags && card.tags.length" class="card-tags">
      <el-tag
        v-for="t in card.tags.slice(0, 3)"
        :key="t"
        size="small"
        effect="plain"
        round
      >{{ t }}</el-tag>
      <span v-if="card.tags.length > 3" class="tag-more">+{{ card.tags.length - 3 }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Clock } from '@element-plus/icons-vue'
import type { PipelineCard, PipelineStage } from './types'
import { formatAmount } from './types'

// v0.3.25 抽自 customer/Pipeline.vue:102-159 (单卡)
defineProps<{
  card: PipelineCard
  fromStage: PipelineStage
  dragging: boolean
}>()

defineEmits<{
  (e: 'dragstart', ev: DragEvent, card: PipelineCard, from: PipelineStage): void
  (e: 'dragend'): void
  (e: 'click', card: PipelineCard): void
}>()
</script>

<style lang="scss" scoped>
.pipeline-card {
  background: #fff;
  border: 1px solid #E5EAF1;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: grab;
  transition: all 0.18s;
  user-select: none;
  box-shadow: 0 1px 2px rgba(12, 68, 124, 0.04);
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(12, 68, 124, 0.14);
    border-color: #BFD3E6;
  }
  &:active { cursor: grabbing; }
  &.card-dragging {
    opacity: 0.4;
    transform: scale(0.98);
  }
}
.card-row { display: flex; align-items: center; }
.card-row-1 { gap: 8px; margin-bottom: 6px; }
.card-row-2 { gap: 8px; margin-bottom: 4px; justify-content: space-between; }
.card-row-3 { font-size: 12px; color: #94A3B8; gap: 6px; }
.card-name {
  font-weight: 700;
  color: #0F172A;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.assign-user { display: flex; align-items: center; gap: 6px; }
.assign-name { font-size: 12px; color: #475569; }
.amount { font-weight: 700; color: #1D9E75; font-size: 14px; }
.last-ago, .close-date { display: inline-flex; align-items: center; gap: 3px; }
.card-tags {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.tag-more {
  font-size: 11px;
  color: #94A3B8;
  align-self: center;
}
</style>
