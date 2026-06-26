<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    title="上传文件"
    width="500px"
    :close-on-click-modal="false"
    :show-close="false"
  >
    <div v-for="f in queue" :key="f.name" style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
        <span>{{ f.name }}</span>
        <span :style="{ color: f.status==='error' ? '#A32D2D' : f.status==='done' ? '#1D9E75' : '#0C447C' }">
          {{ f.status === 'done' ? '完成' : f.status === 'error' ? (f.error || '失败') : f.progress + '%' }}
        </span>
      </div>
      <el-progress
        :percentage="f.progress"
        :status="f.status === 'done' ? 'success' : f.status === 'error' ? 'exception' : undefined"
      />
    </div>
    <template #footer>
      <el-button
        v-if="allDone"
        type="primary"
        @click="emit('close')"
      >关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ visible: boolean; queue: any[] }>()
const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'close'): void
}>()
const allDone = computed(() => props.queue.every(f => f.status === 'done' || f.status === 'error'))
</script>
