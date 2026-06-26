<template>
  <div class="page-container">
    <div class="breadcrumb-bar">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item>
          <span class="crumb-link" @click="goProcessList">工序管理</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          <span class="crumb-link" @click="goProject(instance.project_id)">
            {{ instance.project?.name || instance.project_name || '项目' }}
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item>
          工序 #{{ instance.id || route.params.id }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-header">
      <div class="title-area">
        <el-button :icon="ArrowLeft" text @click="goBack">返回</el-button>
        <span class="page-title">{{ instance.name || instance.template_name || '加载中...' }}</span>
        <span v-if="instance.code" class="code-text">{{ instance.code }}</span>
        <el-tag :type="statusTagType(instance.status)" effect="dark" size="default">
          {{ statusLabel(instance.status) }}
        </el-tag>
        <el-tag v-if="instance.industry" effect="plain" size="default" type="info">
          {{ industryLabel(instance.industry) }}
        </el-tag>
        <el-tag v-if="instance.is_overdue" effect="dark" size="default" type="danger">
          已超期
        </el-tag>
      </div>
      <div class="header-actions">
        <el-button
          v-if="instance.status === 'pending'"
          type="primary"
          :icon="VideoPlay"
          :loading="actionLoading.start"
          @click="handleStart"
        >开始施工</el-button>
        <el-button
          v-if="instance.status === 'in_progress'"
          type="success"
          :icon="CircleCheck"
          :loading="actionLoading.complete"
          @click="handleComplete"
        >标记完成</el-button>
        <el-button :icon="Edit" @click="openEditDialog">编辑</el-button>
        <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
        <el-button type="danger" :icon="Delete" :loading="actionLoading.delete" @click="handleDelete">
          删除
        </el-button>
      </div>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated />

    <template v-else>
      <InstanceInfoCard :instance="instance" @view-project="goProject" />

      <ProgressCard :instance="instance" :inspection-list="inspectionList" />

      <InspectionTable
        :inspection-list="inspectionList"
        @add="openInspectionDialog"
        @delete="handleDeleteInspection"
      />

      <el-card class="info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><InfoFilled /></el-icon>备注 & 元数据
            </span>
          </div>
        </template>
        <el-collapse v-model="metaCollapse">
          <el-collapse-item title="创建 / 更新时间" name="meta">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(instance.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="更新时间">
                {{ formatDateTime(instance.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="验收时间">
                {{ instance.accepted_at ? formatDateTime(instance.accepted_at) : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="验收人">
                {{ instance.acceptedByUser?.name || instance.accepted_by || '-' }}
              </el-descriptions-item>
              <el-descriptions-item v-if="instance.parent" label="上级工序" :span="2">
                {{ instance.parent.name }} ({{ instance.parent.code }})
              </el-descriptions-item>
              <el-descriptions-item
                v-if="instance.children && instance.children.length"
                label="下级工序"
                :span="2"
              >
                <el-tag
                  v-for="c in instance.children"
                  :key="c.id"
                  size="small"
                  effect="plain"
                  style="margin-right: 6px"
                >
                  {{ c.name }} ({{ c.status }})
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </template>

    <InspectionDialog
      v-model:visible="inspectionDialog.visible"
      :submitting="inspectionDialog.loading"
      @submit="submitInspection"
    />

    <EditInstanceDialog
      v-model:visible="editDialog.visible"
      :submitting="editDialog.loading"
      :target="instance"
      :user-options="userOptions"
      @submit="submitEdit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Refresh, Edit, Delete, CircleCheck, VideoPlay, InfoFilled,
} from '@element-plus/icons-vue'
import { processApi, getUserList } from '@/api/modules'
import ProgressCard from './components/ProgressCard.vue'
import InspectionTable from './components/InspectionTable.vue'
import InspectionDialog from './components/InspectionDialog.vue'
import EditInstanceDialog, { type InstanceEditForm } from './components/EditInstanceDialog.vue'
import InstanceInfoCard from './components/instance-detail/InstanceInfoCard.vue'
import { statusLabel, statusTagType, industryLabel, formatDateTime, type ProcessInstance, type Inspection } from './types'

// v0.3.25 拆 InstanceDetail.vue 582→200 (-66%)
// 子组件: InstanceInfoCard (顶头 4 卡 1 个) + 复用 ProgressCard/InspectionTable/InspectionDialog/EditInstanceDialog

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const metaCollapse = ref<string[]>(['meta'])

const instance = ref<ProcessInstance>({} as ProcessInstance)
const inspectionList = ref<Inspection[]>([])
const userOptions = ref<{ id: number; name: string }[]>([])

const actionLoading = reactive({
  start: false, complete: false, delete: false,
})

// ===== 加载数据 =====
const loadInstance = async (): Promise<void> => {
  const id = route.params.id
  if (!id) { ElMessage.error('缺少工序 ID'); return }
  try {
    const res: any = await processApi.instanceDetail(Number(id))
    const data = res?.data ?? res ?? {}
    instance.value = data
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '加载工序详情失败')
    instance.value = {} as ProcessInstance
  }
}

const loadInspections = async (): Promise<void> => {
  const id = route.params.id
  if (!id) return
  try {
    const res: any = await processApi.inspectionList({ process_instance_id: Number(id), per_page: 200 })
    const payload = res?.data ?? res ?? {}
    const items = Array.isArray(payload.data) ? payload.data : (Array.isArray(payload) ? payload : [])
    inspectionList.value = items
  } catch (e) { /* 静默 */ }
}

const loadUsers = async (): Promise<void> => {
  try {
    const res: any = await getUserList({ page: 1, per_page: 200 })
    const payload = res?.data ?? res ?? {}
    userOptions.value = Array.isArray(payload.data) ? payload.data : (Array.isArray(payload) ? payload : [])
  } catch (e) { userOptions.value = [] }
}

const loadAll = async (): Promise<void> => {
  loading.value = true
  try {
    await loadInstance()
    if (!instance.value.inspections || !instance.value.inspections.length) {
      await loadInspections()
    } else {
      inspectionList.value = instance.value.inspections
    }
  } finally {
    loading.value = false
  }
}

// ===== 操作 =====
const goBack = () => router.push('/construction/process/instances')
const goProcessList = () => router.push('/construction/process/instances')
const goProject = (projectId?: number | null) => {
  if (!projectId) return
  router.push(`/project/detail/${projectId}`)
}

const handleStart = async () => {
  if (!instance.value.id) return
  actionLoading.start = true
  try {
    await processApi.instanceProgress(instance.value.id, {
      progress: instance.value.progress ?? 0,
      status: 'in_progress',
      remark: '开始施工',
    })
    ElMessage.success('已开始施工')
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '操作失败')
  } finally { actionLoading.start = false }
}

const handleComplete = async () => {
  if (!instance.value.id) return
  try {
    await ElMessageBox.confirm(
      `确认将「${instance.value.name || instance.value.template_name || '#' + instance.value.id}」标记为已完成？`,
      '标记完成', { confirmButtonText: '确认完成', cancelButtonText: '取消', type: 'warning' }
    )
  } catch { return }
  actionLoading.complete = true
  try {
    await processApi.instanceProgress(instance.value.id, {
      progress: 100, status: 'completed', remark: '施工完成',
    })
    ElMessage.success('已标记为完成')
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '操作失败')
  } finally { actionLoading.complete = false }
}

const handleDelete = async () => {
  if (!instance.value.id) return
  try {
    await ElMessageBox.confirm(
      `确认删除工序实例 #${instance.value.id}？此操作不可恢复。`,
      '删除工序', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch { return }
  actionLoading.delete = true
  try {
    await processApi.instanceDelete(instance.value.id)
    ElMessage.success('已删除')
    router.push('/construction/process/instances')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '删除失败')
  } finally { actionLoading.delete = false }
}

const inspectionDialog = reactive({ visible: false, loading: false })
const openInspectionDialog = () => { inspectionDialog.visible = true; inspectionDialog.loading = false }

const submitInspection = async ({ payload }: { backendResult: string; payload: Record<string, unknown> }) => {
  inspectionDialog.loading = true
  try {
    const id = instance.value.id
    await processApi.inspectionCreate({ ...payload, process_instance_id: id })
    ElMessage.success('验收记录已添加')
    inspectionDialog.visible = false
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '提交失败')
  } finally { inspectionDialog.loading = false }
}

const handleDeleteInspection = async (row: Inspection) => {
  try {
    await ElMessageBox.confirm(`确认删除验收记录 #${row.id}？`, '删除验收', { type: 'warning' })
  } catch { return }
  try {
    await processApi.inspectionDelete(row.id)
    ElMessage.success('已删除')
    await loadInspections()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '删除失败')
  }
}

const editDialog = reactive({ visible: false, loading: false })
const openEditDialog = () => { editDialog.visible = true; editDialog.loading = false }

const submitEdit = async (form: InstanceEditForm) => {
  editDialog.loading = true
  try {
    await processApi.instanceUpdate(instance.value.id, form)
    ElMessage.success('已保存')
    editDialog.visible = false
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally { editDialog.loading = false }
}

onMounted(async () => {
  await Promise.all([loadUsers(), loadAll()])
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.breadcrumb-bar { background: #fff; padding: 8px 16px; border-radius: 8px; margin-bottom: 12px; }
.crumb-link { cursor: pointer; color: #0C447C; &:hover { text-decoration: underline; } }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .title-area { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; }
  .code-text { font-family: monospace; color: #909399; font-size: 13px; }
  .header-actions { display: flex; gap: 8px; }
}
.info-card {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.card-header { display: flex; align-items: center; gap: 8px; }
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}
.card-meta { font-size: 12px; color: #909399; }
</style>
