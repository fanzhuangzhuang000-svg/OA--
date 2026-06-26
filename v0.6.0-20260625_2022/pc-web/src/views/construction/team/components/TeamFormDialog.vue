<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    :title="isEdit ? '编辑团队' : '新建团队'"
    width="720px"
    :close-on-click-modal="false"
    @open="handleOpen"
  >
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="团队名称" prop="name">
            <el-input v-model="formData.name" placeholder="如：第一施工队" maxlength="50" show-word-limit />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="团队类型" prop="type">
            <el-select v-model="formData.type" placeholder="请选择" style="width: 100%">
              <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="负责人" prop="leader_id">
            <el-select
              v-model="formData.leader_id"
              placeholder="请选择"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option v-for="u in userOptions" :key="u.id" :label="u.name" :value="u.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="formData.phone" placeholder="可选" maxlength="20" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="工种" prop="specialty">
            <el-select
              v-model="formData.specialty"
              placeholder="主要工种"
              multiple
              collapse-tags
              collapse-tags-tooltip
              style="width: 100%"
            >
              <el-option v-for="s in specialtyOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="formData.status">
              <el-radio value="active">启用</el-radio>
              <el-radio value="inactive">停用</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="备注">
        <el-input v-model="formData.remark" type="textarea" :rows="3" maxlength="500" show-word-limit />
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
  userOptions: any[]
  editing?: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'save', payload: any): void
}>()

const formRef = ref()
const saving = ref(false)
const isEdit = computed(() => !!props.editing?.id)

const typeOptions = [
  { value: 'internal', label: '自有团队' },
  { value: 'external', label: '外包团队' },
  { value: 'mixed',    label: '混合团队' },
]

const specialtyOptions = [
  '电工', '焊工', '管道工', '架子工', '木工', '瓦工', '油漆工', '设备安装', '弱电', '高空作业',
]

const formData = reactive({
  name: '',
  type: 'internal',
  leader_id: null as number | null,
  phone: '',
  specialty: [] as string[],
  status: 'active',
  remark: '',
})

const formRules = {
  name: [{ required: true, message: '请输入团队名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择团队类型', trigger: 'change' }],
  leader_id: [{ required: true, message: '请选择负责人', trigger: 'change' }],
}

const resetForm = () => {
  formData.name = ''
  formData.type = 'internal'
  formData.leader_id = null
  formData.phone = ''
  formData.specialty = []
  formData.status = 'active'
  formData.remark = ''
}

const fillFromEditing = (row: any) => {
  if (!row) { resetForm(); return }
  formData.name = row.name || ''
  formData.type = row.type || 'internal'
  formData.leader_id = row.leader_id ?? null
  formData.phone = row.phone || ''
  formData.specialty = Array.isArray(row.specialty) ? row.specialty : []
  formData.status = row.status || 'active'
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
      name: formData.name,
      type: formData.type,
      leader_id: formData.leader_id,
      phone: formData.phone,
      specialty: formData.specialty,
      status: formData.status,
      remark: formData.remark,
    })
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}
</script>
