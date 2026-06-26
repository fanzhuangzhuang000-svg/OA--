<template>
  <el-dialog
    v-model="visible"
    title="新建工序实例"
    width="560px"
    destroy-on-close
  >
    <el-form
      :model="form"
      :rules="rules"
      ref="formRef"
      label-width="100px"
    >
      <el-form-item label="所属项目" prop="project_id">
        <el-select
          v-model="form.project_id"
          placeholder="请选择项目"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="p in projectOptions"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="工序模板" prop="template_id">
        <el-select
          v-model="form.template_id"
          placeholder="请选择工序模板"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="t in templateOptions"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="负责人" prop="assignee_id">
        <el-select
          v-model="form.assignee_id"
          placeholder="请选择负责人"
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
      <el-form-item label="计划开始" prop="planned_start">
        <el-date-picker
          v-model="form.planned_start"
          type="date"
          placeholder="选择开始日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="计划结束" prop="planned_end">
        <el-date-picker
          v-model="form.planned_end"
          type="date"
          placeholder="选择结束日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="emit('submit')">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProjectOption, UserOption, TemplateOption } from './types'

// v0.3.19 抽自 process/InstanceList.vue:209-250 + 577-612
const props = defineProps<{
  modelValue: boolean
  loading: boolean
  form: {
    project_id: number | null
    template_id: number | null
    assignee_id: number | null
    planned_start: string
    planned_end: string
  }
  rules: Record<string, any>
  projectOptions: ProjectOption[]
  userOptions: UserOption[]
  templateOptions: TemplateOption[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'submit'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
</script>
