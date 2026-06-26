<template>
  <div class="page-container">
    <div class="page-header">
      <div class="title-area">
        <span class="page-title">线索看板</span>
        <el-tag effect="light" type="info">{{ list.length }} 条线索</el-tag>
      </div>
      <div class="header-actions">
        <el-button :icon="List" @click="$router.push('/sales/leads')">列表视图</el-button>
      </div>
    </div>

    <div class="board-wrapper">
      <div class="board-canvas">
        <div v-for="col in columns" :key="col.value" class="board-column" :class="{ 'is-drop-target': dragOverCol === col.value }" @dragover.prevent="onDragOver(col.value, $event)" @dragleave="onDragLeave(col.value)" @drop="onDrop(col.value)">
          <div class="column-header" :style="{ background: col.bg, color: col.color }">
            <span class="col-name">{{ col.label }}</span>
            <span class="col-count">{{ grouped[col.value]?.length || 0 }}</span>
          </div>
          <div class="column-body">
            <div v-for="l in grouped[col.value] || []" :key="l.id" class="lead-card" :draggable="true" @dragstart="onDragStart(l)" @dragend="onDragEnd">
              <div class="card-head">
                <span class="lead-no">{{ l.lead_no }}</span>
                <el-tag :type="ratingTagType(l.rating)" effect="dark" size="small">{{ l.rating }}</el-tag>
              </div>
              <div class="card-name">{{ l.customer_name || l.contact_name || '-' }}</div>
              <div class="card-contact">
                <el-icon :size="12"><Phone /></el-icon>
                {{ l.contact_name || '-' }} · {{ l.contact_phone || '-' }}
              </div>
              <div class="card-meta">
                <span class="card-source" :class="'src-' + l.source">
                  <el-icon :size="11"><component :is="sourceIcon(l.source)" /></el-icon>
                  {{ sourceLabel(l.source) }}
                </span>
                <span class="card-amount">¥ {{ formatMoney(l.estimated_amount) }}</span>
              </div>
              <div class="card-foot">
                <span class="card-owner">
                  <el-icon :size="11"><User /></el-icon>
                  {{ l.owner?.name || '未分配' }}
                </span>
                <span v-if="l.follow_up_at" class="card-next">
                  <el-icon :size="11"><Clock /></el-icon>
                  {{ formatDate(l.follow_up_at) }}
                </span>
              </div>
            </div>
            <el-empty v-if="!grouped[col.value]?.length" :image-size="50" description="拖入线索" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { List, Phone, User, Clock, Promotion, ChatLineRound, Present, Share } from '@element-plus/icons-vue'
import { getLeads, updateLeadStatus } from '@/api/sales'

const list = ref<any[]>([])
const draggingId = ref<number | null>(null)
const dragOverCol = ref<string | null>(null)

// 看板 7 段列名 → DB 真实 status 值
// v0.5.8 修复：proposal/negotiating 是独立状态，不再合并到 qualified
// 兼容历史脏数据：DB 里可能是 5 段老值，contacting/converted/discarded
const STATUS_REVERSE: Record<string, string> = {
  new: 'new',
  contacted: 'contacted', contacting: 'contacted',
  qualified: 'qualified',
  proposal: 'proposal',
  negotiating: 'negotiating',
  won: 'converted', converted: 'converted',
  lost: 'discarded', discarded: 'discarded',
}

const columns = [
  { value: 'new', label: '新线索', bg: 'rgba(12, 68, 124, 0.1)', color: '#0C447C' },
  { value: 'contacted', label: '跟进中', bg: 'rgba(83, 74, 183, 0.1)', color: '#534AB7' },
  { value: 'qualified', label: '合格', bg: 'rgba(29, 158, 117, 0.1)', color: '#1D9E75' },
  { value: 'proposal', label: '方案报价', bg: 'rgba(186, 117, 23, 0.1)', color: '#BA7517' },
  { value: 'negotiating', label: '谈判中', bg: 'rgba(83, 74, 183, 0.15)', color: '#534AB7' },
  { value: 'won', label: '成交', bg: 'rgba(29, 158, 117, 0.2)', color: '#1D9E75' },
  { value: 'lost', label: '战败', bg: 'rgba(163, 45, 45, 0.1)', color: '#A32D2D' }
]

const sourceOptions = [
  { value: 'online', label: '网络', icon: Promotion },
  { value: 'phone', label: '电话', icon: Phone },
  { value: 'exhibition', label: '展会', icon: Present },
  { value: 'referral', label: '转介', icon: Share },
  { value: 'other', label: '其他', icon: ChatLineRound }
]

const grouped = computed(() => {
  const g: Record<string, any[]> = {}
  for (const c of columns) g[c.value] = []
  for (const l of list.value) {
    const col = STATUS_REVERSE[l.status] || l.status
    if (g[col]) g[col].push(l)
  }
  return g
})

const loadList = async () => {
  try {
    const r: any = await getLeads({ per_page: 200 })
    const d = r || {}
    const items = d.data || d
    list.value = Array.isArray(items) ? items : []
  } catch (e) {
    /* toast already shown */
  }
}

const onDragStart = (l: any) => { draggingId.value = l.id; event?.stopPropagation() }
const onDragEnd = () => { draggingId.value = null; dragOverCol.value = null }
const onDragOver = (col: string, e: DragEvent) => { e.preventDefault(); dragOverCol.value = col }
const onDragLeave = (col: string) => { if (dragOverCol.value === col) dragOverCol.value = null }
const onDrop = async (newBoardStatus: string) => {
  const id = draggingId.value
  if (!id) return
  const lead = list.value.find(l => l.id === id)
  // 跟看板列名比,而不是 DB 5 段值
  if (!lead || STATUS_REVERSE[lead.status] === newBoardStatus) { draggingId.value = null; dragOverCol.value = null; return }
  // converted 状态不可拖入（只可由「转商机」按钮触发）
  if (newBoardStatus === 'won') {
    ElMessage.warning('「已转商机」状态需通过「转商机」按钮触发，不可拖入')
    draggingId.value = null; dragOverCol.value = null
    return
  }
  // 战败 走二次确认
  if (newBoardStatus === 'lost') {
    try {
      await ElMessageBox.confirm(`确认标记线索「${lead.customer_name || lead.lead_no}」为战败？`, '提示', { type: 'warning' })
    } catch {
      draggingId.value = null; dragOverCol.value = null
      return
    }
  }
  const oldBoard = STATUS_REVERSE[lead.status] || lead.status
  // 乐观更新：直接落 7 段真实值（与后端 boardMap 行为一致）
  lead.status = newBoardStatus === 'won' ? 'converted'
    : newBoardStatus === 'lost' ? 'discarded'
    : newBoardStatus
  draggingId.value = null; dragOverCol.value = null
  try {
    // 后端 sales.ts 里的 updateLeadStatus 会自动做 boardMap 归一化
    await updateLeadStatus(id, newBoardStatus)
    ElMessage.success(`已移至「${columns.find(c => c.value === newBoardStatus)?.label}」`)
  } catch (e) {
    lead.status = oldBoard === lead.status ? lead.status : oldBoard
    /* toast already shown */
  }
}

const formatMoney = (n: number) => Number(n || 0).toLocaleString('zh-CN', { maximumFractionDigits: 0 })
const formatDate = (d: string) => d ? d.slice(0, 10) : '-'
const sourceLabel = (s: string) => sourceOptions.find(o => o.value === s)?.label || s || '-'
const sourceIcon = (s: string) => sourceOptions.find(o => o.value === s)?.icon || ChatLineRound
const ratingTagType = (r: string): any => ({ A: 'success', B: 'primary', C: 'info', D: 'danger' } as any)[r] || 'info'

onMounted(() => { loadList() })
</script>

<style lang="scss" scoped>
.page-container {
  padding: 16px; background: #f5f7fa;
  height: calc(100vh - 60px);
  display: flex; flex-direction: column; overflow: hidden;
}
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 14px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); flex-shrink: 0;
  .title-area { display: flex; align-items: center; gap: 10px; }
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
}
.board-wrapper {
  flex: 1; overflow-x: auto; overflow-y: hidden;
  background: #fff; border-radius: 8px; padding: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.board-canvas { display: flex; gap: 10px; height: 100%; min-width: max-content; }
.board-column {
  width: 220px; flex-shrink: 0; display: flex; flex-direction: column;
  background: #f5f7fa; border-radius: 6px;
  transition: all 0.2s; border: 2px solid transparent;
  &.is-drop-target { border-color: #0C447C; background: rgba(12, 68, 124, 0.05); }
  .column-header {
    padding: 8px 12px; border-radius: 6px 6px 0 0;
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; font-weight: 600;
    .col-count { background: rgba(255,255,255,0.6); padding: 1px 8px; border-radius: 10px; font-size: 11px; }
  }
  .column-body { flex: 1; overflow-y: auto; padding: 6px; display: flex; flex-direction: column; gap: 6px; }
}
.lead-card {
  background: #fff; border-radius: 4px; padding: 8px 10px; cursor: grab;
  border: 1px solid #ebeef5; transition: all 0.2s; user-select: none;
  &:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-1px); }
  &:active { cursor: grabbing; }
  .card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .lead-no { font-size: 11px; color: #909399; font-family: 'Consolas', monospace; }
  .card-name { font-size: 13px; font-weight: 600; color: #303133; margin-bottom: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .card-contact { font-size: 11px; color: #606266; display: flex; align-items: center; gap: 3px; margin-bottom: 6px; }
  .card-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .card-source { display: flex; align-items: center; gap: 2px; font-size: 11px; padding: 1px 6px; border-radius: 3px; }
  .card-amount { font-size: 12px; font-weight: 600; color: #BA7517; }
  .card-foot { display: flex; justify-content: space-between; font-size: 11px; color: #909399; }
  .card-owner, .card-next { display: flex; align-items: center; gap: 2px; }
  .src-online { background: rgba(12, 68, 124, 0.1); color: #0C447C; }
  .src-phone { background: rgba(83, 74, 183, 0.1); color: #534AB7; }
  .src-exhibition { background: rgba(186, 117, 23, 0.1); color: #BA7517; }
  .src-referral { background: rgba(163, 45, 45, 0.1); color: #A32D2D; }
  .src-other { background: rgba(96, 98, 102, 0.1); color: #606266; }
}
</style>
