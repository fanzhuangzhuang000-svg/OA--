<template>
  <div class="page-container">
    <div v-if="!wo" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中…</span>
    </div>

    <template v-else>
      <!-- 顶部状态条 -->
      <div class="status-bar" :class="`status-${wo.status}`">
        <div class="status-left">
          <el-button :icon="ArrowLeft" @click="$router.back()" circle size="small" />
          <div class="status-info">
            <div class="status-row1">
              <code class="wo-code">{{ wo.code }}</code>
              <el-tag :type="wo.status_color" effect="dark" size="default">{{ wo.status_label }}</el-tag>
              <el-tag :type="wo.priority_color" effect="plain" size="default">{{ wo.priority_label }}</el-tag>
              <el-icon v-if="wo.is_locked" class="locked" :title="'已锁定 (转返修/已取消/已解决)'"><Lock /></el-icon>
            </div>
            <div class="status-row2">
              <span><el-icon><User /></el-icon> {{ wo.customer_name || wo.contact_name || '—' }}</span>
              <span><el-icon><Phone /></el-icon> {{ wo.contact_phone || '—' }}</span>
              <span v-if="wo.assignee_name"><el-icon><Avatar /></el-icon> {{ wo.assignee_name }}</span>
            </div>
          </div>
        </div>
        <div class="status-right">
          <el-button v-if="wo.status === 'pending' && !wo.is_locked" type="primary" :icon="Promotion" @click="onAssign" size="small">派单</el-button>
          <el-button v-if="wo.status === 'assigned' && !wo.is_locked" type="warning" :icon="VideoPlay" @click="onStart" size="small">开始服务</el-button>
          <el-button v-if="wo.status === 'in_progress' && !wo.is_locked" type="success" :icon="CircleCheck" @click="onResolve" size="small">完成</el-button>
          <el-button v-if="wo.status === 'in_progress' && !wo.is_locked" type="danger" :icon="RefreshRight" @click="onConvert" size="small">转返修</el-button>
        </div>
      </div>

      <!-- 转返修成功提示 -->
      <el-alert
        v-if="wo.converted_repair_id"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 12px;"
      >
        <template #title>
          此工单已转为返修单
          <el-link type="primary" @click="$router.push(`/maintenance/repairs/${wo.converted_repair_id}`)">查看返修单</el-link>
        </template>
      </el-alert>

      <!-- Tab 切换 (移动友好) -->
      <div class="content-card">
        <el-tabs v-model="activeTab" class="detail-tabs">
          <!-- Tab 1: 基本信息 -->
          <el-tab-pane label="基本信息" name="basic">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">客户</div>
                <div class="info-value">{{ wo.customer_name || '—' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">项目</div>
                <div class="info-value">{{ wo.project_name || '—' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">联系人</div>
                <div class="info-value">{{ wo.contact_name || '—' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">联系电话</div>
                <div class="info-value">{{ wo.contact_phone || '—' }}</div>
              </div>
              <div class="info-item" v-if="wo.address">
                <div class="info-label">地址</div>
                <div class="info-value">{{ wo.address }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">优先级</div>
                <div class="info-value">
                  <el-tag :type="wo.priority_color" effect="dark">{{ wo.priority_label }}</el-tag>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">服务类型</div>
                <div class="info-value">{{ wo.service_type || '上门' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">创建时间</div>
                <div class="info-value">{{ formatDate(wo.created_at) }}</div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Tab 2: 设备/故障 -->
          <el-tab-pane label="设备 / 故障" name="equipment">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">品牌</div>
                <div class="info-value">{{ wo.equipment_brand || '—' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">型号</div>
                <div class="info-value">{{ wo.equipment_model || '—' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">序列号</div>
                <div class="info-value">
                  <code v-if="wo.serial_no">{{ wo.serial_no }}</code>
                  <span v-else>—</span>
                </div>
              </div>
              <div class="info-item full">
                <div class="info-label">故障描述</div>
                <div class="info-value description">{{ wo.fault_description }}</div>
              </div>
              <div class="info-item" v-if="wo.scheduled_at">
                <div class="info-label">预约时间</div>
                <div class="info-value">{{ formatDate(wo.scheduled_at) }}</div>
              </div>
              <div class="info-item" v-if="wo.started_at">
                <div class="info-label">开始时间</div>
                <div class="info-value">{{ formatDate(wo.started_at) }}</div>
              </div>
              <div class="info-item" v-if="wo.completed_at">
                <div class="info-label">完成时间</div>
                <div class="info-value">{{ formatDate(wo.completed_at) }}</div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Tab 3: 费用 -->
          <el-tab-pane label="费用" name="cost">
            <div v-if="wo.status === 'resolved' || wo.total_cost > 0" class="cost-summary">
              <div class="cost-row">
                <span>服务费</span>
                <span class="amount">¥ {{ wo.service_fee }}</span>
              </div>
              <div class="cost-row">
                <span>配件费</span>
                <span class="amount">¥ {{ wo.parts_cost }}</span>
              </div>
              <div class="cost-row total">
                <span>合计</span>
                <span class="amount">¥ {{ wo.total_cost }}</span>
              </div>
            </div>
            <el-empty v-else description="工单未完成, 暂无费用" />
            <div v-if="wo.result_notes" class="result-notes">
              <div class="info-label">处理结果</div>
              <div class="info-value">{{ wo.result_notes }}</div>
            </div>
          </el-tab-pane>

          <!-- Tab 4: 时间线 -->
          <el-tab-pane label="时间线" name="timeline">
            <el-timeline>
              <el-timeline-item
                v-for="(ev, idx) in timeline"
                :key="idx"
                :type="ev.type"
                :timestamp="ev.time"
                placement="top"
              >
                <div class="timeline-content">
                  <div class="timeline-title">{{ ev.title }}</div>
                  <div class="timeline-desc">{{ ev.desc }}</div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </el-tab-pane>

          <!-- V0.5.7 块2 — 维修过程照片 (7 步进度) -->
          <el-tab-pane label="过程照片" name="photos">
            <StepPhotoUploader
              v-if="wo?.id"
              target-type="work_order"
              :target-id="wo.id"
            />
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 底部固定操作栏 (移动) -->
      <div class="bottom-bar show-mobile">
        <el-button v-if="wo.status === 'pending' && !wo.is_locked" type="primary" @click="onAssign" style="flex:1;">派单</el-button>
        <el-button v-if="wo.status === 'assigned' && !wo.is_locked" type="warning" @click="onStart" style="flex:1;">开始</el-button>
        <el-button v-if="wo.status === 'in_progress' && !wo.is_locked" type="danger" @click="onConvert" style="flex:1;">转返修</el-button>
        <el-button v-if="wo.status === 'in_progress' && !wo.is_locked" type="success" @click="onResolve" style="flex:1;">完成</el-button>
        <el-button v-if="wo.status === 'pending' || wo.status === 'assigned'" @click="onCancel" plain>取消</el-button>
      </div>
    </template>

    <!-- 完成 dialog (V0.5.5.2 A4) -->
    <el-dialog v-model="resolveVisible" title="完成工单" width="560px" :close-on-press-escape="!resolving" :close-on-click-modal="!resolving">
      <el-form :model="resolveForm" label-width="100px">
        <el-form-item label="处理结果" required>
          <el-input v-model="resolveForm.result_notes" type="textarea" :rows="3" placeholder="现场处理结果/已解决的具体问题" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-form-item label="服务费 (¥)">
          <el-input-number v-model="resolveForm.service_fee" :min="0" :precision="2" :step="50" style="width: 100%" />
        </el-form-item>
        <el-form-item label="配件费 (¥)">
          <el-input-number v-model="resolveForm.parts_cost" :min="0" :precision="2" :step="50" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="wo?.service_type === 'on_site'" label="客户签字" required>
          <div class="signature-pad">
            <canvas
              ref="sigCanvas"
              width="400"
              height="120"
              @mousedown="startDraw"
              @mousemove="draw"
              @mouseup="endDraw"
              @mouseleave="endDraw"
            />
            <el-button size="small" @click="clearSignature" style="margin-top: 4px">清空签字</el-button>
          </div>
          <div class="signature-hint">请客户在签字板上签名确认服务完成</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveVisible = false" :disabled="resolving">取消</el-button>
        <el-button type="success" @click="onResolveConfirm" :loading="resolving">完成</el-button>
      </template>
    </el-dialog>

    <!-- 转返修 dialog -->
    <el-dialog v-model="convertVisible" title="转为返修单" width="500px" :close-on-press-escape="!converting" :close-on-click-modal="!converting">
      <el-form :model="convertForm" label-width="100px">
        <el-form-item label="原因" required>
          <el-input v-model="convertForm.reason" type="textarea" :rows="3" placeholder="现场检测, 需要返厂维修的原因" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="维修方式">
          <el-select v-model="convertForm.method_type" placeholder="预估" style="width: 100%">
            <el-option label="🆓 免费（保内）" value="free_warranty" />
            <el-option label="🆓 免费（合同）" value="free_contract" />
            <el-option label="💰 付费（维修）" value="paid_repair" />
            <el-option label="💰 付费（换新）" value="paid_replace" />
            <el-option label="↩️ 退回（不修）" value="returned" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计完成">
          <el-date-picker v-model="convertForm.expected_finish_at" type="datetime" placeholder="预计完成时间" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-alert type="info" :closable="false" title="转返修后, 原工单将锁定, 不可再编辑" />
      </el-form>
      <template #footer>
        <el-button @click="convertVisible = false">取消</el-button>
        <el-button type="danger" @click="onConvertConfirm" :loading="converting">确认转返修</el-button>
      </template>
    </el-dialog>

    <!-- 派单 dialog -->
    <el-dialog v-model="assignVisible" title="派单" width="400px">
      <el-form label-width="80px">
        <el-form-item label="工程师" required>
          <el-select v-model="assignForm.engineer_id" filterable placeholder="选择工程师" style="width: 100%">
            <el-option v-for="u in engineers" :key="u.id" :label="`${u.name} (${u.username})`" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="assignForm.note" type="textarea" :rows="2" maxlength="200" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" @click="onAssignConfirm" :loading="assigning">派单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, User, Phone, Avatar, Lock, Loading, Promotion, VideoPlay, CircleCheck, RefreshRight, Tools, Promotion as _P } from '@element-plus/icons-vue'
import { get, post, put } from '@/utils/request'
import StepPhotoUploader from './components/StepPhotoUploader.vue'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const wo = ref<any>(null)
const activeTab = ref('basic')
const engineers = ref<any[]>([])

// 转返修
const convertVisible = ref(false)
const converting = ref(false)
const convertForm = ref({ reason: '', method_type: '', expected_finish_at: '' })

// 派单
const assignVisible = ref(false)
const assigning = ref(false)
const assignForm = ref({ engineer_id: null as number | null, note: '' })

const timeline = computed(() => {
  if (!wo.value) return []
  const arr: any[] = []
  if (wo.value.created_at) arr.push({ type: 'primary', time: formatDate(wo.value.created_at), title: '工单创建', desc: '接单登记' })
  if (wo.value.scheduled_at) arr.push({ type: 'info', time: formatDate(wo.value.scheduled_at), title: '预约时间', desc: '' })
  if (wo.value.started_at) arr.push({ type: 'warning', time: formatDate(wo.value.started_at), title: '开始服务', desc: `工程师: ${wo.value.assignee_name}` })
  if (wo.value.completed_at) arr.push({ type: 'success', time: formatDate(wo.value.completed_at), title: wo.value.status === 'converted_to_repair' ? '已转返修' : '已完成', desc: wo.value.result_notes || '' })
  return arr
})

const loadData = async () => {
  try {
    const res: any = await get(`/work-orders/${id}`)
    wo.value = res.data
  } catch (e: any) {
    ElMessage.error('加载失败: ' + (e?.message || ''))
  }
}

const loadEngineers = async () => {
  try {
    // 简化为所有 active 用户
    const res: any = await get('/users', { per_page: 100 })
    engineers.value = res.data?.data || []
  } catch { engineers.value = [] }
}

const onAssign = () => { assignForm.value = { engineer_id: null, note: '' }; assignVisible.value = true }
const onAssignConfirm = async () => {
  if (!assignForm.value.engineer_id) return ElMessage.warning('请选工程师')
  assigning.value = true
  try {
    await post(`/work-orders/${id}/assign`, assignForm.value)
    ElMessage.success('已派单')
    assignVisible.value = false
    await loadData()
  } catch (e: any) { ElMessage.error(e?.message || '派单失败') }
  finally { assigning.value = false }
}

const onStart = async () => {
  await ElMessageBox.confirm('开始服务?', '确认', { type: 'info' }).catch(() => null)
  if (!arguments[0]) return  // 用户取消
  try {
    await post(`/work-orders/${id}/start`)
    ElMessage.success('已开始')
    await loadData()
  } catch (e: any) { ElMessage.error(e?.message || '失败') }
}

const resolveVisible = ref(false)
const resolveForm = ref({ result_notes: '', service_fee: 0, parts_cost: 0, customer_signature: '' })
const resolving = ref(false)

const onResolve = () => {
  resolveForm.value = { result_notes: '', service_fee: 0, parts_cost: 0, customer_signature: '' }
  resolveVisible.value = true
  // 等 dialog 渲染完再清 canvas
  setTimeout(() => clearSignature(), 100)
}

const sigCanvas = ref<HTMLCanvasElement | null>(null)
const drawing = ref(false)

const startDraw = (e: MouseEvent) => {
  drawing.value = true
  const ctx = sigCanvas.value?.getContext('2d')
  if (!ctx || !sigCanvas.value) return
  const rect = sigCanvas.value.getBoundingClientRect()
  ctx.beginPath()
  ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top)
}

const draw = (e: MouseEvent) => {
  if (!drawing.value) return
  const ctx = sigCanvas.value?.getContext('2d')
  if (!ctx || !sigCanvas.value) return
  const rect = sigCanvas.value.getBoundingClientRect()
  ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top)
  ctx.stroke()
}

const endDraw = () => { drawing.value = false }

const clearSignature = () => {
  const ctx = sigCanvas.value?.getContext('2d')
  if (ctx && sigCanvas.value) ctx.clearRect(0, 0, sigCanvas.value.width, sigCanvas.value.height)
}

const saveSignature = () => {
  if (!sigCanvas.value) return ''
  return sigCanvas.value.toDataURL('image/png')
}

const onResolveConfirm = async () => {
  if (!resolveForm.value.result_notes) return ElMessage.warning('请填处理结果')
  // 上门服务必须签字
  if (wo.value?.service_type === 'on_site' && !resolveForm.value.customer_signature) {
    return ElMessage.warning('上门服务必须提供客户签字')
  }
  resolving.value = true
  try {
    if (wo.value?.service_type === 'on_site') {
      resolveForm.value.customer_signature = saveSignature()
    }
    await post(`/work-orders/${id}/resolve`, resolveForm.value)
    ElMessage.success('已完成')
    resolveVisible.value = false
    await loadData()
  } catch (e: any) { ElMessage.error(e?.message || '失败') }
  finally { resolving.value = false }
}

const onCancel = async () => {
  const { value } = await ElMessageBox.prompt('请输入取消原因', '取消工单', { inputType: 'textarea' }).catch(() => null)
  if (!value) return
  try {
    await post(`/work-orders/${id}/cancel`, { reason: value })
    ElMessage.success('已取消')
    await loadData()
  } catch (e: any) { ElMessage.error(e?.message || '失败') }
}

const onConvert = async () => {
  try {
    await ElMessageBox.confirm(
      '转为返修后将自动生成返修单, 原工单状态变为「已转返修」且不可再编辑。\n\n请确认此工单需要返厂或退回处理?',
      '⚠️ 二次确认',
      {
        type: 'warning',
        confirmButtonText: '确认转返修',
        cancelButtonText: '再想想',
        confirmButtonClass: 'el-button--danger',
      }
    )
  } catch {
    return
  }
  convertForm.value = { reason: '', method_type: '', expected_finish_at: '' }
  convertVisible.value = true
}

const onConvertConfirm = async () => {
  if (!convertForm.value.reason) return ElMessage.warning('请填原因')
  converting.value = true
  try {
    const res: any = await post(`/work-orders/${id}/convert-to-repair`, convertForm.value)
    // request.ts 已解包 res.data, 所以 res 本身就是 {repair_order: {...}, work_order: {...}} 或后端平铺返回
    const result = res?.data ?? res
    const repairOrder = result?.repair_order || result
    ElMessage.success(`已转为返修单 ${repairOrder?.code || '新'}`)
    convertVisible.value = false
    if (repairOrder?.id) router.push(`/maintenance/repairs/${repairOrder.id}`)
  } catch (e: any) {
    ElMessage.error(e?.message || '转返修失败')
  } finally { converting.value = false }
}

const formatDate = (s: string) => {
  if (!s) return ''
  const d = new Date(s)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

onMounted(() => {
  loadData()
  loadEngineers()
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }

.loading-state {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 60px;
  color: #909399;
}

.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  border-left: 4px solid #409EFF;
  &.status-pending { border-left-color: #909399; }
  &.status-assigned { border-left-color: #409EFF; }
  &.status-in_progress { border-left-color: #E6A23C; }
  &.status-resolved { border-left-color: #67C23A; }
  &.status-cancelled { border-left-color: #909399; }
  &.status-converted_to_repair { border-left-color: #F56C6C; }
}
.status-left { display: flex; align-items: center; gap: 12px; flex: 1; }
.status-info { flex: 1; }
.signature-pad {
  border: 1px solid #DCDFE6; border-radius: 4px; padding: 4px; background: #FAFAFA;
  canvas { background: #fff; cursor: crosshair; display: block; border-radius: 3px; }
}
.signature-hint { font-size: 11px; color: #909399; margin-top: 4px; }
.status-row1 { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.wo-code { font-size: 18px; font-weight: 600; color: #303133; }
.status-row2 {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #606266;
  span { display: flex; align-items: center; gap: 4px; }
}
.status-right { display: flex; gap: 8px; }
.locked { color: #F56C6C; font-size: 16px; }

.content-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  &.full { grid-column: 1 / -1; }
}
.info-label { font-size: 12px; color: #909399; }
.info-value { font-size: 14px; color: #303133; }
.info-value.description {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
}

.cost-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}
.cost-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  border-bottom: 1px solid #ebeef5;
  &.total { font-weight: 600; font-size: 16px; color: #F56C6C; }
  .amount { font-family: 'Courier New', monospace; }
}

.timeline-content { padding: 4px 0; }
.timeline-title { font-weight: 500; }
.timeline-desc { font-size: 12px; color: #606266; margin-top: 2px; }

.bottom-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 12px 16px;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.08);
  z-index: 100;
  gap: 8px;
}

.show-mobile { display: none; }

@media (max-width: 768px) {
  .page-container { padding: 12px; padding-bottom: 80px; }
  .status-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .status-right { display: none; }
  .info-grid { grid-template-columns: 1fr; }
  .show-mobile { display: flex; }
}
</style>
