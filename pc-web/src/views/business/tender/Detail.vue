<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <div class="page-title-wrap">
        <el-button :icon="ArrowLeft" link @click="goBack">返回</el-button>
        <span class="page-title">{{ detail?.name || '招标项目详情' }}</span>
        <el-tag v-if="detail" size="small" :type="statusTag(detail.status)" effect="light">
          {{ detail.status_label || detail.status }}
        </el-tag>
      </div>
      <div class="header-actions">
        <el-button v-if="canEdit" type="primary" plain @click="onEdit">编辑</el-button>
        <el-button v-if="canPublish" type="success" @click="onPublish">发布</el-button>
        <el-button v-if="canEvaluate" type="primary" @click="showEvaluate = true">评标打分</el-button>
        <el-button v-if="canAward" type="success" @click="showAward = true">定标</el-button>
        <el-button v-if="canClose" @click="onClose">关闭</el-button>
        <el-button v-if="canCancel" type="danger" plain @click="onCancel">取消</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="detail-tabs" v-if="detail">
      <!-- Tab 1: 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="编号">{{ detail.code }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ typeLabel(detail.type) }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ detail.creator?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="关联项目">{{ detail.project?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截标时间">{{ fmt(detail.deadline) }}</el-descriptions-item>
          <el-descriptions-item label="开标时间">{{ fmt(detail.open_at) }}</el-descriptions-item>
          <el-descriptions-item label="发布时间">{{ fmt(detail.publish_at) }}</el-descriptions-item>
          <el-descriptions-item label="中标时间">{{ fmt(detail.awarded_at) }}</el-descriptions-item>
          <el-descriptions-item label="中标供应商">{{ detail.awardedSupplier?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="公开链接" :span="3">
            <el-input v-if="publicUrl" :model-value="publicUrl" readonly>
              <template #append>
                <el-button :icon="CopyDocument" @click="copyUrl">复制</el-button>
              </template>
            </el-input>
            <span v-else class="muted">未发布</span>
          </el-descriptions-item>
          <el-descriptions-item label="说明" :span="3">{{ detail.description || '-' }}</el-descriptions-item>
        </el-descriptions>

        <h4 class="block-title">必购清单</h4>
        <el-table :data="detail.required_items || []" border size="small" empty-text="无必购项">
          <el-table-column prop="name" label="物料/服务" min-width="200" />
          <el-table-column prop="spec" label="规格" width="160" />
          <el-table-column prop="qty" label="数量" width="100" align="right" />
          <el-table-column prop="unit" label="单位" width="80" />
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 投标 -->
      <el-tab-pane :label="`投标 (${bids.length})`" name="bids">
        <div class="bids-actions" v-if="bids.length > 0">
          <el-button type="primary" :icon="Histogram" @click="showCompare = true">横向比价</el-button>
        </div>
        <el-table :data="bids" v-loading="loadingBids" border stripe>
          <el-table-column type="index" label="#" width="60" />
          <el-table-column label="投标编号" prop="code" width="160" />
          <el-table-column label="供应商" min-width="160">
            <template #default="{ row }">{{ row.supplier?.name }}</template>
          </el-table-column>
          <el-table-column label="总金额" width="140" align="right">
            <template #default="{ row }">¥ {{ Number(row.total_amount || 0).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="交货期(天)" width="100" align="center">
            <template #default="{ row }">{{ row.lead_time_days ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="综合得分" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.total_score != null" :type="row.status === 'awarded' ? 'success' : 'primary'" effect="dark">
                {{ row.total_score }}
              </el-tag>
              <span v-else class="muted">未评分</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="bidStatusTag(row.status)" effect="light">{{ row.status_label || row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="提交时间" width="160">
            <template #default="{ row }">{{ fmt(row.submitted_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewBid(row)">查看</el-button>
              <el-button v-if="canAward && row.status !== 'awarded'" link type="success" @click="quickAward(row)">定标</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 3: 附件 -->
      <el-tab-pane label="附件" name="attachments">
        <el-upload :http-request="onUpload" :show-file-list="false" :before-upload="beforeUpload" accept="*/*">
          <el-button type="primary" :icon="Upload">上传招标文件</el-button>
        </el-upload>
        <el-table :data="attachments" border size="small" style="margin-top:12px" empty-text="暂无附件">
          <el-table-column prop="file_name" label="文件名" min-width="220" show-overflow-tooltip />
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column prop="visibility" label="可见性" width="100" />
          <el-table-column label="大小" width="100">
            <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openFile(row)">预览</el-button>
              <el-button link type="danger" @click="onDeleteAtt(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 子对话框 -->
    <BidCompareDialog v-model:visible="showCompare" :bids="bids" :required-items="detail?.required_items" />
    <EvaluateDialog
      v-model:visible="showEvaluate"
      :tender-id="Number(id)"
      :bids="bids"
      :score-config="detail?.score_config"
      @saved="loadAll"
    />
    <AwardDialog
      v-model:visible="showAward"
      :tender-id="Number(id)"
      :bids="bids"
      :default-bid-id="defaultAwardBidId"
      @awarded="onAwarded"
    />
    <BidDetailDialog v-model:visible="showBidDetail" :bid="currentBid" />

    <EditTenderDialog
      v-model:visible="showEdit"
      :tender="detail"
      @saved="loadAll"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, CopyDocument, Histogram, Upload, Plus } from '@element-plus/icons-vue'
import { tender } from '@/api/tender'
import type { TenderProject, TenderBid, TenderAttachment } from '@/api/tender'
import BidCompareDialog from './components/BidCompareDialog.vue'
import EvaluateDialog from './components/EvaluateDialog.vue'
import AwardDialog from './components/AwardDialog.vue'
import BidDetailDialog from './components/BidDetailDialog.vue'
import EditTenderDialog from './components/EditTenderDialog.vue'

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id as string)

const detail = ref<TenderProject | null>(null)
const bids = ref<TenderBid[]>([])
const attachments = ref<TenderAttachment[]>([])
const loading = ref(false)
const loadingBids = ref(false)
const activeTab = ref('basic')

const showCompare = ref(false)
const showEvaluate = ref(false)
const showAward = ref(false)
const showBidDetail = ref(false)
const showEdit = ref(false)
const currentBid = ref<TenderBid | null>(null)
const defaultAwardBidId = ref<number | undefined>()

const publicUrl = computed(() => {
  if (!detail.value?.public_token) return ''
  return `${window.location.origin}/portal/tender/${detail.value.public_token}`
})

// 状态机权限
const canEdit = computed(() => detail.value?.status === 'draft')
const canPublish = computed(() => detail.value?.status === 'draft')
const canEvaluate = computed(() => ['bidding', 'evaluating'].includes(detail.value?.status || ''))
const canAward = computed(() => ['bidding', 'evaluating'].includes(detail.value?.status || ''))
const canClose = computed(() => ['bidding', 'evaluating', 'awarded'].includes(detail.value?.status || ''))
const canCancel = computed(() => ['draft', 'bidding', 'evaluating'].includes(detail.value?.status || ''))

const typeLabel = (t?: string) => t === 'tender' ? '招标' : t === 'rfq' ? '询价' : t === 'negotiation' ? '议价' : '-'
const statusTag = (s: string) => (({
  draft: 'info', bidding: 'warning', evaluating: 'primary', awarded: 'success', closed: '', cancelled: 'danger',
} as Record<string, '' | 'success' | 'warning' | 'info' | 'primary' | 'danger'>)[s] || '')
const bidStatusTag = (s: string) => (({
  draft: 'info', submitted: 'primary', shortlisted: 'warning', awarded: 'success', rejected: 'danger', withdrawn: 'info',
} as Record<string, '' | 'success' | 'warning' | 'info' | 'primary' | 'danger'>)[s] || '')
const fmt = (s?: string) => s ? s.replace('T', ' ').slice(0, 16) : '-'
const formatSize = (b?: number) => b ? (b / 1024).toFixed(1) + ' KB' : '-'

const loadDetail = async () => {
  loading.value = true
  try {
    const res: any = await tender.get(Number(id.value))
    detail.value = res
  } finally { loading.value = false }
}

const loadBids = async () => {
  loadingBids.value = true
  try {
    const res: any = await tender.listBids(Number(id.value))
    bids.value = Array.isArray(res) ? res : (res?.data ?? [])
  } finally { loadingBids.value = false }
}

const loadAttachments = async () => {
  const res: any = await tender.listAttachments(Number(id.value))
  attachments.value = Array.isArray(res) ? res : (res?.data ?? [])
}

const loadAll = async () => { await Promise.all([loadDetail(), loadBids(), loadAttachments()]) }

const goBack = () => router.push({ name: 'BusinessTender' })

const copyUrl = async () => {
  if (!publicUrl.value) return
  try {
    await navigator.clipboard.writeText(publicUrl.value)
    ElMessage.success('公开链接已复制, 可发送给受邀供应商')
  } catch { ElMessage.warning('复制失败, 请手动选取') }
}

const openFile = (att: TenderAttachment) => {
  if (att.url) window.open(att.url, '_blank')
}

const beforeUpload = (file: File) => {
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件超过 50MB')
    return false
  }
  return true
}

const onUpload = async (opt: any) => {
  const fd = new FormData()
  fd.append('file', opt.file)
  fd.append('category', 'tender_doc')
  fd.append('visibility', 'public')
  try {
    await tender.uploadAttachment(Number(id.value), fd)
    ElMessage.success('已上传')
    await loadAttachments()
  } catch (e: any) {
    ElMessage.error(e?.message || '上传失败')
  }
}

const onDeleteAtt = async (att: TenderAttachment) => {
  try { await ElMessageBox.confirm(`确认删除「${att.file_name}」?`, '删除确认', { type: 'warning' }) } catch { return }
  await tender.deleteAttachment(Number(id.value), att.id)
  ElMessage.success('已删除')
  await loadAttachments()
}

const onEdit = () => { showEdit.value = true }
const onPublish = async () => {
  try { await ElMessageBox.confirm('发布后不可回退到草稿, 确认?', '发布确认', { type: 'success' }) } catch { return }
  await tender.publish(Number(id.value))
  ElMessage.success('已发布')
  await loadAll()
}
const onClose = async () => {
  try { await ElMessageBox.confirm('关闭后供应商无法继续投标, 确认?', '关闭确认', { type: 'warning' }) } catch { return }
  await tender.close(Number(id.value))
  ElMessage.success('已关闭')
  await loadAll()
}
const onCancel = async () => {
  try { await ElMessageBox.confirm('取消后不可恢复, 确认?', '取消确认', { type: 'warning' }) } catch { return }
  await tender.cancel(Number(id.value))
  ElMessage.success('已取消')
  await loadAll()
}

const viewBid = (b: TenderBid) => { currentBid.value = b; showBidDetail.value = true }
const quickAward = (b: TenderBid) => { defaultAwardBidId.value = b.id; showAward.value = true }
const onAwarded = async () => { showAward.value = false; await loadAll() }

onMounted(loadAll)
</script>

<style scoped lang="scss">
.page-container { padding: 16px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.page-title-wrap { display: flex; align-items: center; gap: 10px; }
.page-title { font-size: 18px; font-weight: 600; }
.header-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.muted { color: #999; }
.bids-actions { margin-bottom: 12px; }
.block-title { margin: 16px 0 8px; font-size: 14px; font-weight: 600; }
</style>
