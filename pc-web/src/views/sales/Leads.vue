<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">线索池</span>
      <div class="header-actions">
        <el-button :icon="DataLine" plain @click="$router.push('/sales/leads/board')">
          看板视图
        </el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新建线索</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="客户名称">
          <el-input
            v-model="searchForm.keyword"
            placeholder="模糊搜索客户"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="s in STATUS_OPTIONS"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select
            v-model="searchForm.source"
            placeholder="全部来源"
            clearable
            style="width: 140px"
          >
            <el-option
              v-for="s in sourceOptions"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="content-card">
      <div class="stats-row">
        <div
          v-for="s in statCards"
          :key="s.label"
          class="stat-card"
          :style="{ borderColor: s.color }"
        >
          <div class="stat-icon" :style="{ background: s.color + '15', color: s.color }">
            <el-icon :size="20"><component :is="s.icon" /></el-icon>
          </div>
          <div>
            <div class="stat-value" :style="{ color: s.color }">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
      </div>

      <el-table
        :data="pagedList"
        stripe
        border
        v-loading="loading"
        :header-cell-style="{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }"
      >
        <el-table-column prop="lead_no" label="线索编号" width="160" fixed>
          <template #default="{ row }">
            <span class="link-text" @click="handleView(row)">{{ row.lead_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="联系人" width="120">
          <template #default="{ row }">
            <div>{{ row.contact_name || '-' }}</div>
            <div class="sub-text">{{ row.contact_title || '' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="contact_phone" label="联系电话" width="140" />
        <el-table-column label="来源" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="sourceTagType(row.source)" effect="light" size="small">
              {{ sourceLabel(row.source, sourceOptions) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="ratingTagType(row.rating)" effect="dark" size="small">
              {{ row.rating }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimated_amount" label="预计金额" width="120" align="right">
          <template #default="{ row }">¥ {{ formatMoney(row.estimated_amount) }}</template>
        </el-table-column>
        <el-table-column label="跟进人" width="100">
          <template #default="{ row }">{{ row.owner?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="下次跟进" width="120" align="center">
          <template #default="{ row }">{{ formatDate(row.follow_up_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="plain" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="warning" @click="handleEdit(row)">编辑</el-button>
            <template v-if="row.status !== 'converted'">
              <el-button
                link
                type="success"
                :disabled="!['qualified', 'proposal', 'negotiating'].includes(row.status)"
                @click="handleConvert(row)"
              >
                转商机
              </el-button>
              <el-button link type="danger" @click="handleDiscard(row)">丢弃</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </div>

    <LeadDialog
      v-model:visible="showFormDialog"
      :mode="formMode"
      :submitting="submitting"
      :source-options="sourceOptions"
      :user-options="userOptions"
      :target="formTarget"
      @save="handleSave"
    />

    <DiscardDialog
      v-model:visible="showDiscardDialog"
      :submitting="submitting"
      :target="discardTarget"
      @confirm="confirmDiscard"
    />

    <ConvertLeadDialog
      v-model:visible="showConvertDialog"
      :submitting="submitting"
      :target="convertTarget"
      :user-options="userOptions"
      @confirm="confirmConvert"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search, Refresh, DataLine, Phone, Aim, Star, Promotion, Document, ChatLineRound, TrophyBase, Delete } from '@element-plus/icons-vue'
import {
  getLeads, getLeadSourceOptions, createLead, updateLead, convertLeadToOpp,
} from '@/api/sales'
import { getEmployeeList } from '@/api/employee'
import LeadDialog, { type LeadFormData } from './components/LeadDialog.vue'
import DiscardDialog, { type DiscardFormData } from './components/DiscardDialog.vue'
import ConvertLeadDialog, { type ConvertFormData } from './components/ConvertLeadDialog.vue'
import {
  STATUS_OPTIONS, statusLabel, statusTagType, ratingTagType, sourceLabel, sourceTagType,
  formatMoney, formatDate,
} from './leadTypes'

const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const list = ref<any[]>([])

const searchForm = reactive({ keyword: '', status: '', source: '' })

const sourceOptions = ref<any[]>([])
const userOptions = ref<any[]>([])

const statCards = computed(() => [
  { label: '新线索', value: list.value.filter((l) => l.status === 'new').length, icon: Star, color: '#0C447C' },
  { label: '跟进中', value: list.value.filter((l) => ['contacting', 'contacted'].includes(l.status)).length, icon: Phone, color: '#534AB7' },
  { label: '方案报价', value: list.value.filter((l) => l.status === 'proposal').length, icon: Document, color: '#BA7517' },
  { label: '谈判中', value: list.value.filter((l) => l.status === 'negotiating').length, icon: ChatLineRound, color: '#BA7517' },
  { label: '已转商机', value: list.value.filter((l) => l.status === 'converted').length, icon: TrophyBase, color: '#1D9E75' },
  { label: '已丢弃', value: list.value.filter((l) => l.status === 'discarded').length, icon: Delete, color: '#A32D2D' },
  { label: '本月预计金额', value: '¥ ' + formatMoney(list.value.reduce((s, l) => s + Number(l.estimated_amount || 0), 0)), icon: Promotion, color: '#BA7517' },
])

const pagedList = computed(() => list.value)

const loadList = async () => {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, per_page: pageSize.value }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.source) params.source = searchForm.source
    const r: any = await getLeads(params)
    const d = r || {}
    list.value = d.data || []
    total.value = d.total || 0
  } catch (e) {
    /* toast */
  } finally {
    loading.value = false
  }
}

const loadSourceOptions = async () => {
  try {
    const r: any = await getLeadSourceOptions()
    if (r && r.length > 0) {
      sourceOptions.value = r
    } else {
      sourceOptions.value = [
        { value: 'online', label: '网络推广' },
        { value: 'phone', label: '电话陌拜' },
        { value: 'exhibition', label: '展会活动' },
        { value: 'referral', label: '老客户转介' },
        { value: 'other', label: '其他' },
      ]
    }
  } catch (e) {
    sourceOptions.value = [
      { value: 'online', label: '网络推广' },
      { value: 'phone', label: '电话陌拜' },
      { value: 'exhibition', label: '展会活动' },
      { value: 'referral', label: '老客户转介' },
      { value: 'other', label: '其他' },
    ]
  }
}

const loadUsers = async () => {
  try {
    const r: any = await getEmployeeList({ per_page: 200 })
    userOptions.value = r?.data || []
  } catch (e) {
    userOptions.value = []
  }
}

const handleSearch = () => { page.value = 1; loadList() }
const handleReset = () => { searchForm.keyword = ''; searchForm.status = ''; searchForm.source = ''; page.value = 1; loadList() }
const handleView = (row: any) => router.push(`/sales/leads/${row.id}`)

// 新建/编辑
const showFormDialog = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const formTarget = ref<any>(null)

const handleAdd = () => {
  formMode.value = 'create'
  formTarget.value = { id: 0 }
  showFormDialog.value = true
}

const handleEdit = (row: any) => {
  if (row.status === 'converted') {
    ElMessage.warning('已转商机的线索不可编辑')
    return
  }
  formMode.value = 'edit'
  formTarget.value = row
  showFormDialog.value = true
}

const handleSave = async (data: LeadFormData, mode: 'create' | 'edit') => {
  submitting.value = true
  try {
    const payload: any = { ...data }
    delete payload.id
    if (mode === 'create') {
      await createLead(payload)
      ElMessage.success('线索创建成功')
    } else {
      await updateLead(data.id, payload)
      ElMessage.success('线索已更新')
    }
    showFormDialog.value = false
    page.value = 1
    await loadList()
  } catch (e) {
    /* toast */
  } finally {
    submitting.value = false
  }
}

// 丢弃
const showDiscardDialog = ref(false)
const discardTarget = ref<any>(null)

const handleDiscard = (row: any) => {
  discardTarget.value = row
  showDiscardDialog.value = true
}

const confirmDiscard = async (data: DiscardFormData) => {
  submitting.value = true
  try {
    await updateLead(discardTarget.value.id, {
      status: 'discarded',
      discard_reason: data.reason,
      notes: data.notes || discardTarget.value.notes,
    })
    ElMessage.success('已标记为丢弃')
    showDiscardDialog.value = false
    await loadList()
  } catch (e) {
    /* toast */
  } finally {
    submitting.value = false
  }
}

// 转商机
const showConvertDialog = ref(false)
const convertTarget = ref<any>(null)

const handleConvert = (row: any) => {
  if (!['qualified', 'proposal', 'negotiating'].includes(row.status)) {
    ElMessage.warning('仅「合格 / 方案报价 / 谈判中」状态的线索可转商机')
    return
  }
  convertTarget.value = row
  showConvertDialog.value = true
}

const confirmConvert = async (data: ConvertFormData) => {
  submitting.value = true
  try {
    const r: any = await convertLeadToOpp(convertTarget.value.id, data)
    const opp = r?.data || r
    ElMessage.success(`已转商机：${opp?.name || data.name}`)
    showConvertDialog.value = false
    await loadList()
  } catch (e) {
    /* toast */
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadSourceOptions(); loadUsers(); loadList()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .page-title { font-size: 18px; font-weight: 600; color: #0C447C; border-left: 4px solid #0C447C; padding-left: 10px; }
  .header-actions { display: flex; gap: 8px; }
}
.filter-bar { background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); }
.content-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04); }
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
.stat-card {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  background: #fff; border: 1px solid #ebeef5; border-left: 4px solid;
  border-radius: 6px; transition: all 0.2s;
  &:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .stat-value { font-size: 20px; font-weight: 700; line-height: 1.2; }
  .stat-label { font-size: 12px; color: #909399; margin-top: 2px; }
}
.sub-text { font-size: 11px; color: #909399; }
.link-text { color: #0C447C; cursor: pointer; font-weight: 500; &:hover { text-decoration: underline; } }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
