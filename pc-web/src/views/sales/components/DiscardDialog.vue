<template>
  <el-dialog
    :model-value="visible"
    title="丢弃线索"
    width="1500px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-form :model="formData" label-width="80px">
      <el-form-item label="客户">
        <span>{{ target?.customer_name || target?.lead_no }}</span>
      </el-form-item>
      <el-form-item label="丢弃原因" required>
        <el-select v-model="formData.reason" placeholder="请选择原因" style="width: 100%">
          <el-option
            v-for="r in DISCARD_REASONS"
            :key="r.value"
            :label="r.label"
            :value="r.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="formData.notes" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="danger" :loading="submitting" @click="handleConfirm">
        确认丢弃
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DISCARD_REASONS } from '../leadTypes'

export interface DiscardFormData {
  reason: string
  notes: string
}

const props = defineProps<{
  visible: boolean
  submitting: boolean
  target: any | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'confirm', data: DiscardFormData): void
}>()

const formData = reactive<DiscardFormData>({ reason: '', notes: '' })

watch(
  () => props.target,
  () => {
    formData.reason = ''
    formData.notes = ''
  },
  { immediate: true },
)

const handleConfirm = () => {
  if (!formData.reason) {
    ElMessage.warning('请选择丢弃原因')
    return
  }
  emit('confirm', { ...formData })
}
</script>
