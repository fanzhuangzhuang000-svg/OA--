<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="新建报价请求"
    width="820px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="项目" prop="project_id">
        <el-input-number v-model="form.project_id" :min="0" />
      </el-form-item>
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" maxlength="200" show-word-limit />
      </el-form-item>
      <el-form-item label="截止时间" prop="deadline">
        <el-date-picker v-model="form.deadline" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
      </el-form-item>

      <el-form-item label="需求清单" prop="required_items">
        <div style="width:100%">
          <div style="display:flex;gap:8px;margin-bottom:8px">
            <el-button size="small" :icon="Plus" @click="addItem">手动添加</el-button>
            <el-button size="small" type="primary" :icon="Goods" @click="showPicker = true">从产品库选择</el-button>
            <span style="color:#909399;font-size:12px;align-self:center">
              支持手动添加 / 从产品库 ({{ form.required_items.length }} 条)
            </span>
          </div>
          <el-table :data="form.required_items" border size="small">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column label="名称" width="180">
              <template #default="{ row }">
                <el-input v-model="row.name" size="small" placeholder="必填" />
              </template>
            </el-table-column>
            <el-table-column label="规格" width="160">
              <template #default="{ row }">
                <el-input v-model="row.spec" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="{ row }">
                <el-input-number v-model="row.qty" :min="0" :precision="2" size="small" controls-position="right" style="width:100%" />
              </template>
            </el-table-column>
            <el-table-column label="单位" width="80">
              <template #default="{ row }">
                <el-input v-model="row.unit" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="来源" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row._source === 'product_picker'" type="success" size="small">产品库</el-tag>
                <el-tag v-else type="info" size="small">手动</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ $index }">
                <el-button size="small" link type="danger" @click="form.required_items.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form-item>

      <el-form-item label="附件">
        <div style="width:100%">
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :before-upload="beforeUpload"
            :on-success="onUploadSuccess"
            :on-error="onUploadError"
            name="file"
            accept="*"
          >
            <el-button size="small" type="primary" :icon="Upload" :loading="uploading">上传附件</el-button>
            <span style="color:#909399;font-size:12px;margin-left:12px">
              招标文件/图纸/技术规格 (≤50MB, 已上传 {{ form.required_files?.length || 0 }} 个)
            </span>
          </el-upload>
          <div v-if="form.required_files?.length" class="file-list">
            <div v-for="f in form.required_files" :key="f.id" class="file-item">
              <el-icon><Document /></el-icon>
              <a :href="f.url" target="_blank" class="file-name">{{ f.name }}</a>
              <span class="file-size">({{ formatSize(f.size) }})</span>
              <el-button size="small" link type="danger" @click="removeFile(f.id)">删除</el-button>
            </div>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="说明">
        <el-input v-model="form.description" type="textarea" :rows="3" maxlength="2000" show-word-limit />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">提交</el-button>
    </template>

    <!-- 产品库 picker -->
    <ProductPickerDialog
      v-model:visible="showPicker"
      :existing-items="form.required_items"
      @pick="onPicked"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { Plus, Upload, Goods, Document } from '@element-plus/icons-vue'
import { externalQuote } from '@/api/external-quote'
import { getToken } from '@/utils/auth'
import ProductPickerDialog from './ProductPickerDialog.vue'

const props = defineProps<{ visible: boolean }>()
const emit = defineEmits<{
  'update:visible': [v: boolean]
  saved: []
}>()

const formRef = ref<FormInstance>()
const submitting = ref(false)
const uploading = ref(false)
const showPicker = ref(false)

const form = ref({
  project_id: undefined as number | undefined,
  title: '',
  deadline: '',
  required_items: [] as any[],
  required_files: [] as any[],
  description: '',
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  required_items: [{ required: true, type: 'array', min: 1, message: '至少 1 条' }],
}

// 附件上传 URL
const uploadUrl = computed(() => '/api/external-quotes/upload-attachment')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${getToken()}`,
}))

const beforeUpload = (file: File) => {
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('附件大小不能超过 50MB')
    return false
  }
  uploading.value = true
  return true
}
const onUploadSuccess = (res: any) => {
  uploading.value = false
  if (res?.code === 0) {
    const f = res.data
    form.value.required_files.push({
      id: f.id?.toString() || uniqId(),
      name: f.original_name || f.name,
      path: f.path,
      url: `/storage/${f.path}`,
      size: f.size,
      mime: f.mime_type,
      uploaded_at: new Date().toISOString(),
    })
    ElMessage.success('已上传')
  } else {
    ElMessage.error(res?.message || '上传失败')
  }
}
const onUploadError = () => {
  uploading.value = false
  ElMessage.error('上传失败')
}
function uniqId() { return 'f_' + Math.random().toString(36).slice(2, 10) }

const removeFile = (id: string) => {
  form.value.required_files = form.value.required_files.filter((f) => f.id !== id)
}

const formatSize = (s: number) => {
  if (s < 1024) return `${s} B`
  if (s < 1024 * 1024) return `${(s / 1024).toFixed(1)} KB`
  return `${(s / 1024 / 1024).toFixed(2)} MB`
}

const addItem = () => {
  form.value.required_items.push({ name: '', spec: '', qty: 1, unit: '件', _source: 'manual' })
}

const onPicked = (items: any[]) => {
  form.value.required_items.push(...items)
}

watch(() => props.visible, (v) => {
  if (v) {
    form.value = {
      project_id: undefined, title: '', deadline: '',
      required_items: [{ name: '', spec: '', qty: 1, unit: '件', _source: 'manual' }],
      required_files: [],
      description: '',
    }
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    await externalQuote.createRequest({
      project_id: form.value.project_id,
      title: form.value.title,
      required_items: form.value.required_items.map((i) => ({
        product_id: i.product_id,
        code: i.code,
        name: i.name,
        spec: i.spec,
        qty: i.qty,
        unit: i.unit,
      })),
      required_files: form.value.required_files,
      deadline: form.value.deadline || undefined,
      description: form.value.description,
    })
    ElMessage.success('报价请求已创建')
    emit('update:visible', false)
    emit('saved')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.file-list {
  margin-top: 8px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: #fafbfc;
  padding: 4px 0;
}
.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
}
.file-item:not(:last-child) { border-bottom: 1px solid #ebeef5; }
.file-name {
  color: #409eff;
  text-decoration: none;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-name:hover { text-decoration: underline; }
.file-size { color: #909399; font-size: 12px; }
</style>
