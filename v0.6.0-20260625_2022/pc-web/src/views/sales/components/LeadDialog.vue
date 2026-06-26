<template>
  <el-dialog
    :model-value="visible"
    :title="mode === 'create' ? '新建线索' : '编辑线索'"
    width="1500px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="客户名称" prop="customer_name">
            <el-input v-model="formData.customer_name" placeholder="请输入客户名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系人" prop="contact_name">
            <el-input v-model="formData.contact_name" placeholder="联系人姓名" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="联系人职位">
            <el-input v-model="formData.contact_title" placeholder="如：技术总监" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="contact_phone">
            <el-input v-model="formData.contact_phone" placeholder="手机或座机" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="来源" prop="source">
            <el-select v-model="formData.source" placeholder="请选择" style="width: 100%">
              <el-option
                v-for="s in sourceOptions"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="评级" prop="rating">
            <el-select v-model="formData.rating" placeholder="请选择" style="width: 100%">
              <el-option
                v-for="r in RATING_OPTIONS"
                :key="r.value"
                :label="r.label"
                :value="r.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="预计金额">
            <el-input-number
              v-model="formData.estimated_amount"
              :min="0"
              :step="1000"
              style="width: 100%"
              placeholder="¥"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="跟进人" prop="owner_id">
            <el-select
              v-model="formData.owner_id"
              placeholder="请选择跟进人"
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
        </el-col>
        <el-col :span="12">
          <el-form-item label="下次跟进">
            <el-date-picker
              v-model="formData.follow_up_at"
              type="datetime"
              placeholder="选择日期时间"
              style="width: 100%"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注">
        <el-input v-model="formData.notes" type="textarea" :rows="3" placeholder="线索备注信息" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { FormInstance, FormRules } from 'element-plus'
import { RATING_OPTIONS } from '../leadTypes'

export interface LeadFormData {
  id: number
  customer_name: string
  contact_name: string
  contact_title: string
  contact_phone: string
  source: string
  rating: string
  estimated_amount: number
  owner_id: number | null
  follow_up_at: string
  notes: string
}

const props = defineProps<{
  visible: boolean
  mode: 'create' | 'edit'
  submitting: boolean
  sourceOptions: { value: string; label: string }[]
  userOptions: { id: number; name: string }[]
  target: any | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'save', data: LeadFormData, mode: 'create' | 'edit'): void
}>()

const formRef = ref<FormInstance>()
const formData = reactive<LeadFormData>({
  id: 0,
  customer_name: '',
  contact_name: '',
  contact_title: '',
  contact_phone: '',
  source: 'phone',
  rating: 'C',
  estimated_amount: 0,
  owner_id: null,
  follow_up_at: '',
  notes: '',
})

const formRules: FormRules = {
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  source: [{ required: true, message: '请选择来源', trigger: 'change' }],
  rating: [{ required: true, message: '请选择评级', trigger: 'change' }],
  owner_id: [{ required: true, message: '请选择跟进人', trigger: 'change' }],
}

const resetForm = () => {
  Object.assign(formData, {
    id: 0, customer_name: '', contact_name: '', contact_title: '', contact_phone: '',
    source: 'phone', rating: 'C', estimated_amount: 0, owner_id: null, follow_up_at: '', notes: '',
  })
}

watch(
  () => props.target,
  (row) => {
    if (!row) return
    if (props.mode === 'edit') {
      Object.assign(formData, {
        id: row.id,
        customer_name: row.customer_name || '',
        contact_name: row.contact_name || '',
        contact_title: row.contact_title || '',
        contact_phone: row.contact_phone || '',
        source: row.source || 'phone',
        rating: row.rating || 'C',
        estimated_amount: Number(row.estimated_amount || 0),
        owner_id: row.owner_id || null,
        follow_up_at: row.follow_up_at || '',
        notes: row.notes || '',
      })
    } else {
      resetForm()
    }
  },
  { immediate: true },
)

const handleSave = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  emit('save', { ...formData }, props.mode)
}
</script>
