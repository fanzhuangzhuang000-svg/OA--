<template>
  <div class="page-container">
    <div class="page-header">
      <el-button :icon="ArrowLeft" plain @click="goBack">返回</el-button>
      <span class="page-title" style="margin-left: 16px">服务工单详情</span>
      <div class="header-actions">
        <el-button v-if="detail?.status === 'assigned' && detail?.technician_id" type="primary" :icon="VideoPlay" @click="startOrder">开始服务</el-button>
        <el-button v-if="detail?.status === 'in_progress'" type="success" :icon="CircleCheck" @click="showCompleteDialog">完工</el-button>
        <el-button v-if="['pending', 'assigned'].includes(detail?.status)" type="danger" :icon="CircleClose" @click="showCancelDialog">取消</el-button>
      </div>
    </div>

    <div v-loading="loading" v-if="detail">
      <el-card shadow="hover" style="margin-bottom: 16px">
        <template #header>
          <div style="display: flex; align-items: center; gap: 12px">
            <span style="font-size: 18px; font-weight: 600">{{ detail.order_no }}</span>
            <el-tag :type="statusTagType(detail.status)" effect="plain">{{ statusLabel(detail.status) }}</el-tag>
            <el-tag effect="plain">{{ typeLabel(detail.service_type) }}</el-tag>
            <el-tag :type="priorityTagType(detail.priority)" effect="plain">{{ priorityLabel(detail.priority) }}</el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="标题" :span="3">{{ detail.title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="关联质保期" :span="3">
            <el-link v-if="detail.warranty" type="primary" :underline="false" @click="goWarranty(detail.warranty)">
              {{ detail.warranty.warranty_no }}
            </el-link>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联项目">
            {{ detail.warranty?.project?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="客户">
            {{ detail.warranty?.customer?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="设备">
            {{ detail.warranty?.device?.device_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="预约日期">{{ detail.scheduled_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="实际开始">{{ detail.started_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="完工日期">{{ detail.completed_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="技工">
            {{ detail.technician?.name || '未指派' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系姓名">{{ detail.contact_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ detail.contact_phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="服务地址" :span="3">{{ detail.address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="故障描述" :span="3">{{ detail.fault_description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="处理结果" :span="3" v-if="detail.result_notes">{{ detail.result_notes }}</el-descriptions-item>
          <el-descriptions-item label="客户评分" v-if="detail.rating">
            <el-rate v-model="detail.rating" disabled />
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 完工 dialog -->
    <el-dialog v-model="completeDialog.visible" title="完工确认" width="500px">
      <el-form :model="completeDialog.form" label-width="100px">
        <el-form-item label="处理结果" required>
          <el-input v-model="completeDialog.form.result_notes" type="textarea" :rows="4" placeholder="请详细描述处理过程和结果" />
        </el-form-item>
        <el-form-item label="服务费">
          <el-input-number v-model="completeDialog.form.fee" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="配件费">
          <el-input-number v-model="completeDialog.form.parts_cost" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="客户评分">
          <el-rate v-model="completeDialog.form.rating" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="completeDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitComplete">确认完工</el-button>
      </template>
    </el-dialog>

    <!-- 取消 dialog -->
    <el-dialog v-model="cancelDialog.visible" title="取消工单" width="400px">
      <el-form :model="cancelDialog.form" label-width="80px">
        <el-form-item label="原因" required>
          <el-input v-model="cancelDialog.form.reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelDialog.visible = false">不取消</el-button>
        <el-button type="danger" @click="submitCancel">确认取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, VideoPlay, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { warrantyOrderApi } from '@/api/warranty'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref<any>(null)

const id = computed(() => Number(route.params.id))

const statusLabel = (s: string) => ({ pending: '待派工', assigned: '已派工', in_progress: '进行中', completed: '已完成', cancelled: '已取消' } as any)[s] || s
const typeLabel = (t: string) => ({ inspect: '巡检', repair: '维修', clean: '清洁', calibrate: '校准', replace: '更换' } as any)[t] || t
const priorityLabel = (p: string) => ({ low: '低', normal: '中', high: '高', urgent: '紧急' } as any)[p] || p
const statusTagType = (s: string) => ({ pending: 'info', assigned: 'warning', in_progress: 'primary', completed: 'success', cancelled: 'danger' } as any)[s] || 'info'
const priorityTagType = (p: string) => ({ low: 'info', normal: '', high: 'warning', urgent: 'danger' } as any)[p] || ''

async function loadDetail() {
  loading.value = true
  try {
    const res: any = await warrantyOrderApi.show(id.value)
    detail.value = res.data || res
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e.message || 'unknown'))
  } finally {
    loading.value = false
  }
}

function goBack() { router.push('/project/warranty/service-order') }
function goWarranty(w: any) { router.push(`/project/warranty/detail/${w.id}`) }

async function startOrder() {
  try {
    await warrantyOrderApi.start(id.value, {})
    ElMessage.success('已开始服务')
    loadDetail()
  } catch (e: any) {
    ElMessage.error('开始失败: ' + (e.message || 'unknown'))
  }
}

const completeDialog = reactive({
  visible: false,
  form: { result_notes: '', fee: 0, parts_cost: 0, rating: 5 },
})

function showCompleteDialog() {
  completeDialog.form = { result_notes: '', fee: 0, parts_cost: 0, rating: 5 }
  completeDialog.visible = true
}

async function submitComplete() {
  if (!completeDialog.form.result_notes) {
    ElMessage.warning('请填写处理结果')
    return
  }
  try {
    await warrantyOrderApi.complete(id.value, completeDialog.form)
    ElMessage.success('已完工')
    completeDialog.visible = false
    loadDetail()
  } catch (e: any) {
    ElMessage.error('完工失败: ' + (e.message || 'unknown'))
  }
}

const cancelDialog = reactive({ visible: false, form: { reason: '' } })
function showCancelDialog() {
  cancelDialog.form = { reason: '' }
  cancelDialog.visible = true
}

async function submitCancel() {
  if (!cancelDialog.form.reason) {
    ElMessage.warning('请填写原因')
    return
  }
  try {
    await warrantyOrderApi.cancel(id.value, { reason: cancelDialog.form.reason })
    ElMessage.success('已取消')
    cancelDialog.visible = false
    loadDetail()
  } catch (e: any) {
    ElMessage.error('取消失败: ' + (e.message || 'unknown'))
  }
}

onMounted(loadDetail)
</script>
