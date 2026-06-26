<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    :title="isEdit ? '编辑开工单' : '新建开工单'"
    width="900px"
    :close-on-click-modal="false"
    @open="handleOpen"
  >
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="所属项目" prop="project_id">
            <el-select
              v-model="formData.project_id"
              placeholder="请选择项目"
              filterable
              :disabled="isEdit"
              style="width: 100%"
            >
              <el-option
                v-for="p in projectOptions"
                :key="p.id"
                :label="`${p.code ? p.code + ' - ' : ''}${p.name || ''}`"
                :value="p.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="施工团队" prop="team_id">
            <el-select
              v-model="formData.team_id"
              placeholder="请选择团队"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="t in teamOptions"
                :key="t.id"
                :label="`${t.name}${t.leader ? ' (' + t.leader.name + ')' : ''}`"
                :value="t.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="计划开工" prop="planned_start">
            <el-date-picker
              v-model="formData.planned_start"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计划完工" prop="planned_end">
            <el-date-picker
              v-model="formData.planned_end"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="工时预估" prop="estimated_hours">
            <el-input-number v-model="formData.estimated_hours" :min="0" :step="8" style="width: 100%" />
            <span class="form-tip">人时</span>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="工人数量" prop="worker_count">
            <el-input-number v-model="formData.worker_count" :min="1" :step="1" style="width: 100%" />
            <span class="form-tip">人</span>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="施工内容" prop="work_scope">
        <el-input
          v-model="formData.work_scope"
          type="textarea"
          :rows="4"
          maxlength="1000"
          show-word-limit
          placeholder="简述本次开工的施工范围与主要工序"
        />
      </el-form-item>

      <el-form-item label="备注">
        <el-input v-model="formData.remark" type="textarea" :rows="2" maxlength="500" show-word-limit />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  projectOptions: any[]
  teamOptions: any[]
  editing?: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'save', payload: any): void
}>()

const formRef = ref()
const saving = ref(false)
const isEdit = computed(() => !!props.editing?.id)

const formData = reactive({
  project_id: null as number | null,
  team_id: null as number | null,
  planned_start: '',
  planned_end: '',
  estimated_hours: 0,
  worker_count: 1,
  work_scope: '',
  remark: '',
})

const formRules = {
  project_id:    [{ required: true, message: '请选择项目', trigger: 'change' }],
  team_id:       [{ required: true, message: '请选择团队', trigger: 'change' }],
  planned_start: [{ required: true, message: '请选择开工日期', trigger: 'change' }],
  planned_end:   [{ required: true, message: '请选择完工日期', trigger: 'change' }],
  work_scope:    [{ required: true, message: '请填写施工内容', trigger: 'blur' }],
}

const resetForm = () => {
  formData.project_id = null
  formData.team_id = null
  formData.planned_start = ''
  formData.planned_end = ''
  formData.estimated_hours = 0
  formData.worker_count = 1
  formData.work_scope = ''
  formData.remark = ''
}

const fillFromEditing = (row: any) => {
  if (!row) { resetForm(); return }
  formData.project_id = row.project_id || null
  formData.team_id = row.team_id || null
  formData.planned_start = row.planned_start || ''
  formData.planned_end = row.planned_end || ''
  formData.estimated_hours = Number(row.estimated_hours || 0)
  formData.worker_count = Number(row.worker_count || 1)
  formData.work_scope = row.work_scope || ''
  formData.remark = row.remark || ''
}

const handleOpen = () => {
  if (props.editing) fillFromEditing(props.editing)
  else resetForm()
}

const handleSave = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    emit('save', {
      project_id: formData.project_id,
      team_id: formData.team_id,
      planned_start: formData.planned_start,
      planned_end: formData.planned_end,
      estimated_hours: Number(formData.estimated_hours || 0),
      worker_count: Number(formData.worker_count || 1),
      work_scope: formData.work_scope,
      remark: formData.remark,
    })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.form-tip { color: #909399; font-size: 12px; margin-left: 8px; }
</style>
