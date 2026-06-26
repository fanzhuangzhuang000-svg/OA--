<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'create' ? '新建工序模板' : '编辑工序模板'"
    width="640px"
    :close-on-click-modal="false"
    @closed="$emit('closed')"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="行业" prop="industry">
        <el-select v-model="form.industry" placeholder="请选择行业" style="width: 100%">
          <el-option
            v-for="(label, key) in INDUSTRY_MAP"
            :key="key"
            :label="label"
            :value="key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="编号" prop="code">
        <el-input v-model="form.code" placeholder="如 GC-001" maxlength="50" show-word-limit />
      </el-form-item>
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入模板名称" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="排序" prop="sort_order">
        <el-input-number v-model="form.sort_order" :min="0" :step="1" style="width: 100%" />
        <span class="form-hint">数字越小排序越靠前</span>
      </el-form-item>
      <el-form-item label="工期" prop="duration_days">
        <el-input-number v-model="form.duration_days" :min="0" :step="1" style="width: 100%" />
        <span class="form-hint">单位:天,0 表示不限定</span>
      </el-form-item>
      <el-form-item label="验收要点" prop="acceptance_points">
        <el-input
          v-model="form.acceptance_points"
          type="textarea"
          :rows="4"
          placeholder="请输入验收要点(多行)"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-switch
          v-model="form.status"
          :active-value="1"
          :inactive-value="0"
          inline-prompt
          active-text="启用"
          inactive-text="停用"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="emit('submit')">
        {{ mode === 'create' ? '创建' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { INDUSTRY_MAP } from './types'

// v0.3.25 抽自 process/TemplateList.vue:170-236
const props = defineProps<{
  modelValue: boolean
  mode: 'create' | 'edit'
  form: any
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'submit'): void
  (e: 'closed'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

// 子组件维护 form 副本
const localForm = reactive(JSON.parse(JSON.stringify(props.form)))
watch(() => props.form, (v) => {
  Object.assign(localForm, JSON.parse(JSON.stringify(v)))
}, { deep: true })
const formRef = ref<FormInstance>()
defineExpose({ formRef, localForm })

const formRules = {
  industry: [{ required: true, message: '请选择行业', trigger: 'change' }],
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  sort_order: [{ required: true, message: '请输入排序', trigger: 'blur' }],
  duration_days: [{ required: true, message: '请输入工期', trigger: 'blur' }],
}
</script>

<style lang="scss" scoped>
.form-hint { margin-left: 12px; color: #909399; font-size: 12px; }
</style>
