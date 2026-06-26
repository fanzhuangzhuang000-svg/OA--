<template>
  <el-dialog
    v-model="visible"
    :title="mode === 'create' ? '新建采购需求' : '编辑采购需求'"
    width="720px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      :model="localForm"
      :rules="rules"
      ref="formRef"
      label-width="100px"
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="关联项目" prop="project_id">
            <el-select
              v-model="localForm.project_id"
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
        </el-col>
        <el-col :span="12">
          <el-form-item label="需求日期" prop="need_date">
            <el-date-picker
              v-model="localForm.need_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="localForm.priority" placeholder="请选择" style="width: 100%">
              <el-option
                v-for="p in PRIORITY_OPTIONS"
                :key="p.value"
                :label="p.label"
                :value="p.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="发起人" prop="creator">
            <el-input v-model="localForm.creator" placeholder="请输入发起人" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">需求物资（可添加多种）</el-divider>

      <div v-for="(item, idx) in localForm.materials" :key="idx" class="material-row">
        <el-row :gutter="8">
          <el-col :span="9">
            <el-form-item
              :prop="`materials.${idx}.name`"
              :rules="{ required: true, message: '请输入物资名称', trigger: 'blur' }"
              label-width="0"
            >
              <el-input v-model="item.name" placeholder="物资名称（如：海康 4K 摄像头）" />
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item :prop="`materials.${idx}.spec`" label-width="0">
              <el-input v-model="item.spec" placeholder="规格（可选）" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item
              :prop="`materials.${idx}.quantity`"
              :rules="{ required: true, message: '请输入数量', trigger: 'blur' }"
              label-width="0"
            >
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :step="1"
                style="width: 100%"
                placeholder="数量"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item :prop="`materials.${idx}.unit`" label-width="0">
              <el-input v-model="item.unit" placeholder="单位" />
            </el-form-item>
          </el-col>
          <el-col :span="2">
            <el-button
              type="danger"
              link
              :icon="Delete"
              :disabled="localForm.materials.length === 1"
              @click="emit('removeMaterial', idx)"
              style="margin-top: 4px"
            />
          </el-col>
        </el-row>
      </div>

      <el-form-item label-width="0">
        <el-button :icon="Plus" plain type="primary" @click="emit('addMaterial')">添加物资</el-button>
        <span class="form-hint">如需采购多种物资，可点击添加</span>
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="localForm.remark"
          type="textarea"
          :rows="3"
          placeholder="采购需求备注（如：施工进度原因、特殊要求等）"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="emit('submit')">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { RequirementForm, ProjectOption, FormMode } from './types'
import { PRIORITY_OPTIONS } from './types'

// v0.3.23 抽自 purchase/Requirement.vue:131-240
const props = defineProps<{
  modelValue: boolean
  mode: FormMode
  form: RequirementForm
  loading: boolean
  projectOptions: ProjectOption[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'submit'): void
  (e: 'addMaterial'): void
  (e: 'removeMaterial', idx: number): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

// 子组件维护 form 副本（避免直接改 prop，绕开 Vue 3 v-model 限制）
const localForm = reactive<RequirementForm>(JSON.parse(JSON.stringify(props.form)))
watch(() => props.form, (v) => {
  Object.assign(localForm, JSON.parse(JSON.stringify(v)))
}, { deep: true })

const formRef = ref()
defineExpose({ formRef, localForm })

const rules = {
  project_id: [{ required: true, message: '请选择关联项目', trigger: 'change' }],
  need_date: [{ required: true, message: '请选择需求日期', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  creator: [{ required: true, message: '请输入发起人', trigger: 'blur' }],
}
</script>

<style lang="scss" scoped>
.material-row {
  margin-bottom: 8px;
  padding: 8px;
  background: #fafbfc;
  border-radius: 4px;
  &:last-child { margin-bottom: 0; }
}
.form-hint { margin-left: 12px; color: #909399; font-size: 12px; }
</style>
