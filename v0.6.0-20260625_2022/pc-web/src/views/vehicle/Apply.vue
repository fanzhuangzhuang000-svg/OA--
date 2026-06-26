<template>
  <div class="page-container">
    <div class="page-header">
      <h2>用车申请</h2>
    </div>
    <div class="content-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 720px">
        <el-form-item label="用车日期" prop="usage_date">
          <el-date-picker v-model="form.usage_date" type="date" placeholder="选择用车日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="form.start_time" placeholder="开始时间" style="width: 100%" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="form.end_time" placeholder="结束时间" style="width: 100%" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="目的地" prop="destination">
          <el-input v-model="form.destination" placeholder="请输入目的地" />
        </el-form-item>
        <el-form-item label="用车事由" prop="purpose">
          <el-input v-model="form.purpose" type="textarea" :rows="3" placeholder="请详细说明用车事由" />
        </el-form-item>
        <el-form-item label="乘车人数" prop="passengers">
          <el-input-number v-model="form.passengers" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="是否自驾" prop="self_drive">
          <el-radio-group v-model="form.self_drive">
            <el-radio :value="false">否（需要司机）</el-radio>
            <el-radio :value="true">是（自驾）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交申请</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { post } from '@/utils/request'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  usage_date: '',
  start_time: '',
  end_time: '',
  destination: '',
  purpose: '',
  passengers: 1,
  self_drive: false,
})

const rules = {
  usage_date: [{ required: true, message: '请选择用车日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  destination: [{ required: true, message: '请输入目的地', trigger: 'blur' }],
  purpose: [{ required: true, message: '请输入用车事由', trigger: 'blur' }],
  passengers: [{ required: true, message: '请输入乘车人数', trigger: 'blur' }],
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    await post('/vehicles/usage', form)
    ElMessage.success('用车申请已提交，等待审批')
    router.push('/vehicle/dispatch')
  } catch (e: any) {
    ElMessage.error(e?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => { router.push('/vehicle') }
</script>

<style lang="scss" scoped>
.page-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.page-header { margin-bottom: 16px; h2 { font-size: 20px; color: #0C447C; margin: 0; } }
.content-card { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
</style>
