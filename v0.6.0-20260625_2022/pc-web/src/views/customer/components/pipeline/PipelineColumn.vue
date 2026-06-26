<template>
  <div
    class="pipeline-col glass"
    :class="{
      'col-active': dragOver,
      'col-lost': column.stage === 'lost',
    }"
    @dragover.prevent="emit('dragover', $event, column.stage)"
    @dragenter.prevent="emit('dragenter', $event, column.stage)"
    @dragleave="emit('dragleave', column.stage)"
    @drop.prevent="emit('drop', $event, column.stage)"
  >
    <div class="col-header" :style="{ borderTopColor: column.color }">
      <div class="col-title">
        <span class="col-dot" :style="{ background: column.color }"></span>
        <span class="col-name">{{ column.label }}</span>
        <span class="col-count">{{ column.count }}</span>
      </div>
      <div class="col-total" :style="{ color: column.color }">
        ¥ {{ formatAmount(column.total) }}
      </div>
    </div>

    <div class="col-body">
      <PipelineCard
        v-for="card in column.cards"
        :key="card.id"
        :card="card"
        :from-stage="column.stage"
        :dragging="draggingId === card.id"
        @dragstart="emit('dragstart', $event, card, column.stage)"
        @dragend="emit('dragend')"
        @click="(c) => emit('view', c)"
      />

      <div v-if="column.cards.length === 0" class="col-empty">
        拖入客户到这一阶段
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import PipelineCard from './PipelineCard.vue'
import type { PipelineColumn, PipelineCard as Card, PipelineStage } from './types'
import { formatAmount } from './types'

// v0.3.25 抽自 customer/Pipeline.vue:78-160
defineProps<{
  column: PipelineColumn
  dragOver: boolean
  draggingId: number | null
}>()

const emit = defineEmits<{
  (e: 'dragstart', ev: DragEvent, card: Card, from: PipelineStage): void
  (e: 'dragend'): void
  (e: 'dragover', ev: DragEvent, stage: PipelineStage): void
  (e: 'dragenter', ev: DragEvent, stage: PipelineStage): void
  (e: 'dragleave', stage: PipelineStage): void
  (e: 'drop', ev: DragEvent, stage: PipelineStage): void
  (e: 'view', card: Card): void
}>()
</script>

<style lang="scss" scoped>
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 16px rgba(12, 68, 124, 0.06);
  border-radius: 12px;
}
.pipeline-col {
  flex: 1 0 240px;
  max-width: 280px;
  display: flex;
  flex-direction: column;
  border-top: 3px solid #0C447C;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.85);
  align-self: stretch;
}
.pipeline-col.col-active {
  border-color: #1D9E75;
  box-shadow: 0 0 0 2px rgba(29, 158, 117, 0.4), 0 8px 24px rgba(12, 68, 124, 0.14);
  background: rgba(232, 248, 241, 0.9);
}
.pipeline-col.col-lost {
  opacity: 0.7;
  background: rgba(241, 245, 249, 0.85);
  border-top-color: #A32D2D !important;
}
.col-header {
  padding: 12px 14px 10px;
  border-bottom: 1px dashed #E5EAF1;
}
.col-title {
  display: flex;
  align-items: center;
  gap: 8px;
}
.col-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.col-name {
  font-weight: 600;
  font-size: 14px;
  color: #0F172A;
}
.col-count {
  background: #E0E7EF;
  color: #475569;
  font-size: 12px;
  padding: 1px 8px;
  border-radius: 10px;
  margin-left: auto;
}
.col-total {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
}
.col-body {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.col-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
  font-size: 12px;
  border: 1px dashed #E5EAF1;
  border-radius: 8px;
  padding: 24px 8px;
}

@media (max-width: 1200px) {
  .pipeline-col { flex: 1 0 220px; }
}
</style>
