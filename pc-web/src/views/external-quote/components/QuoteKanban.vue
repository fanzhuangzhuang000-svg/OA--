<template>
  <div class="board">
    <div
      v-for="col in columns"
      :key="col.key"
      class="board-col"
    >
      <div class="col-header" :style="{ borderTopColor: col.color }">
        <span>{{ col.label }}</span>
        <el-tag size="small">{{ col.items.length }}</el-tag>
      </div>
      <div class="col-body">
        <div
          v-for="item in col.items"
          :key="item.id"
          class="board-card"
          @click="$emit('view', item)"
        >
          <div class="card-title">{{ item.title }}</div>
          <div class="card-meta">
            <el-tag size="small" effect="plain">{{ item.code }}</el-tag>
            <span v-if="item.project" class="meta-item">📁 {{ item.project.name }}</span>
          </div>
          <div class="card-meta">
            <span class="meta-item">⏰ 截止: {{ item.deadline || '不限' }}</span>
            <span class="meta-item">📊 报价: {{ item.quotes_count || 0 }}</span>
          </div>
          <div v-if="item.awardedSupplier" class="card-meta">
            <el-tag type="success" size="small">🏆 {{ item.awardedSupplier.name }}</el-tag>
          </div>
        </div>
        <el-empty v-if="!col.items.length" :image-size="60" description="无数据" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ExternalQuoteRequest } from '@/api/external-quote'

const props = defineProps<{
  data: ExternalQuoteRequest[]
}>()

defineEmits<{ view: [row: ExternalQuoteRequest] }>()

const STATUS_META: Record<string, { label: string; color: string }> = {
  open:      { label: '征集中', color: '#0C447C' },
  closed:    { label: '已截止', color: '#909399' },
  awarded:   { label: '已定标', color: '#67c23a' },
  cancelled: { label: '已取消', color: '#f56c6c' },
}

const columns = computed(() => {
  const cols = Object.entries(STATUS_META).map(([key, meta]) => ({
    key, label: meta.label, color: meta.color, items: [] as ExternalQuoteRequest[],
  }))
  for (const item of props.data) {
    const c = cols.find(x => x.key === item.status)
    if (c) c.items.push(item)
  }
  return cols
})
</script>

<style lang="scss" scoped>
.board {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.board-col {
  flex: 0 0 300px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 220px);
}
.col-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px;
  background: #fff;
  border-top: 3px solid #0C447C;
  border-radius: 8px 8px 0 0;
  font-weight: 600;
}
.col-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.board-card {
  background: #fff;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.2s;
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }
}
.card-title {
  font-weight: 600;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-meta {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.meta-item { color: #666; font-size: 12px; }
</style>
