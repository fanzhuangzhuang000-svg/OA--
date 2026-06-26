<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    :title="isEdit ? '编辑日志' : '新增施工日志'"
    width="820px"
    :close-on-click-modal="false"
    @open="handleOpen"
  >
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="日期" prop="date">
            <el-date-picker
              v-model="formData.date"
              type="date"
              value-format="YYYY-MM-DD"
              :disabled="isEdit"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="天气" prop="weather">
            <el-select v-model="formData.weather" placeholder="请选择" style="width: 100%">
              <el-option v-for="w in weatherOptions" :key="w" :label="w" :value="w" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="开工单" prop="commencement_id">
            <el-select
              v-model="formData.commencement_id"
              placeholder="请选择开工单"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="o in commencementOptions"
                :key="o.id"
                :label="`${o.code} - ${o.project?.name || o.team?.name || ''}`"
                :value="o.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="工序" prop="process_id">
            <el-select
              v-model="formData.process_id"
              placeholder="请选择工序"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="p in processOptions"
                :key="p.id"
                :label="`${p.name}${p.code ? ' (' + p.code + ')' : ''}`"
                :value="p.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="工人数量" prop="worker_count">
            <el-input-number v-model="formData.worker_count" :min="1" :step="1" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="工时" prop="work_hours">
            <el-input-number v-model="formData.work_hours" :min="0" :step="1" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="进度" prop="progress">
            <el-input-number v-model="formData.progress" :min="0" :max="100" :step="5" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="问题与风险" prop="issues">
        <el-input
          v-model="formData.issues"
          type="textarea"
          :rows="3"
          maxlength="1000"
          show-word-limit
          placeholder="今日遇到的问题 / 风险 / 需要协调的事项（可选）"
        />
      </el-form-item>

      <el-form-item label="照片">
        <el-input v-model="formData.photos" placeholder="照片 URL，多个用逗号分隔（可选）" />
      </el-form-item>

      <el-form-item label="备注">
        <el-input v-model="formData.remark" type="textarea" :rows="2" maxlength="500" show-word-limit />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave('draft')">保存草稿</el-button>
      <el-button type="success" :loading="saving" @click="handleSave('submit')" v-if="!isEdit">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  commencementOptions: any[]
  processOptions: any[]
  editing?: any
  defaultDate?: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'save', payload: any, action: 'draft' | 'submit'): void
}>()

const formRef = ref()
const saving = ref(false)
const isEdit = computed(() => !!props.editing?.id)

const weatherOptions = ['晴', '多云', '阴', '小雨', '中雨', '大雨', '雪', '雾', '大风']

const formData = reactive({
  date: '',
  weather: '晴',
  commencement_id: null as number | null,
  process_id: null as number | null,
  worker_count: 1,
  work_hours: 0,
  progress: 0,
  issues: '',
  photos: '',
  remark: '',
})

const formRules = {
  date:        [{ required: true, message: '请选择日期', trigger: 'change' }],
  weather:     [{ required: true, message: '请选择天气', trigger: 'change' }],
  commencement_id: [{ required: true, message: '请选择开工单', trigger: 'change' }],
  worker_count:[{ required: true, message: '请填写工人数量', trigger: 'blur' }],
  work_hours:  [{ required: true, message: '请填写工时', trigger: 'blur' }],
  progress:    [{ required: true, message: '请填写进度', trigger: 'blur' }],
}

const resetForm = () => {
  formData.date = props.defaultDate || new Date().toISOString().slice(0, 10)
  formData.weather = '晴'
  formData.commencement_id = null
  formData.process_id = null
  formData.worker_count = 1
  formData.work_hours = 0
  formData.progress = 0
  formData.issues = ''
  formData.photos = ''
  formData.remark = ''
}

const fillFromEditing = (row: any) => {
  if (!row) { resetForm(); return }
  formData.date = row.date || ''
  formData.weather = row.weather || '晴'
  formData.commencement_id = row.commencement_id || null
  formData.process_id = row.process_id || null
  formData.worker_count = Number(row.worker_count || 1)
  formData.work_hours = Number(row.work_hours || 0)
  formData.progress = Number(row.progress || 0)
  formData.issues = row.issues || ''
  formData.photos = Array.isArray(row.photos) ? row.photos.join(',') : (row.photos || '')
  formData.remark = row.remark || ''
}

const handleOpen = () => {
  if (props.editing) fillFromEditing(props.editing)
  else resetForm()
}

const handleSave = async (action: 'draft' | 'submit') => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    emit('save', {
      date: formData.date,
      weather: formData.weather,
      commencement_id: formData.commencement_id,
      process_id: formData.process_id,
      worker_count: Number(formData.worker_count || 1),
      work_hours: Number(formData.work_hours || 0),
      progress: Number(formData.progress || 0),
      issues: formData.issues,
      photos: formData.photos,
      remark: formData.remark,
    }, action)
  } finally {
    saving.value = false
  }
}
</script>
