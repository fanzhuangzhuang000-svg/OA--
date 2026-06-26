<template>
  <el-dialog
    :model-value="visible"
    title="转商机"
    width="1500px"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-form :model="formData" label-width="100px">
      <el-form-item label="商机名称" required>
        <el-input v-model="formData.name" placeholder="如：XX 银行监控改造" />
      </el-form-item>
      <el-form-item label="预计金额" required>
        <el-input-number
          v-model="formData.estimated_amount"
          :min="0"
          :step="1000"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="预计签约日">
        <el-date-picker
          v-model="formData.expected_sign_date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="售前工程师" required>
        <el-select
          v-model="formData.presale_id"
          placeholder="请选择"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="u in userOptions"
            :key="u.id"
            :label="u.name"
            :value="u.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="formData.notes" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleConfirm">
        确认转商机
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

export interface ConvertFormData {
  name: string
  estimated_amount: number
  expected_sign_date: string
  presale_id: number | null
  notes: string
}

const props = defineProps<{
  visible: boolean
  submitting: boolean
  target: any | null
  userOptions: { id: number; name: string }[]
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'confirm', data: ConvertFormData): void
}>()

const formData = reactive<ConvertFormData>({
  name: '',
  estimated_amount: 0,
  expected_sign_date: '',
  presale_id: null,
  notes: '',
})

watch(
  () => props.target,
  (row) => {
    if (!row) return
    Object.assign(formData, {
      name: row.customer_name || '',
      estimated_amount: Number(row.estimated_amount || 0),
      expected_sign_date: '',
      presale_id: null,
      notes: '',
    })
  },
  { immediate: true },
)

const handleConfirm = () => {
  if (!formData.name || !formData.estimated_amount || !formData.presale_id) {
    ElMessage.warning('请填写商机名称、预计金额、售前工程师')
    return
  }
  emit('confirm', { ...formData })
}
</script>
