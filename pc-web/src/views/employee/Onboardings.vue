<template>
  <div class="page-container">
    <OnboardingStatCards
      ref="statCardsRef"
      @create="openCreate"
      @export="exportList"
    />

    <OnboardingFilterBar
      :filters="filters"
      :department-list="deptList"
      @search="handleSearch"
      @reset="handleReset"
      @create="openCreate"
    />

    <OnboardingTable
      :list="list"
      :total="pagination.total"
      :loading="loading"
      :pagination="pagination"
      @view="openDetail"
      @renew="openRenewContract"
      @archive="handleArchive"
      @reload="loadList"
    />

    <OnboardingWizardDialog
      v-model="wizardVisible"
      :step="wizardStep"
      :submitting="submitting"
      :form1="formStep1"
      :form2="formStep2"
      :form3="formStep3"
      :rules1="rulesStep1"
      :rules2="rulesStep2"
      :department-list="deptList"
      :position-list="posList"
      :active-user-list="activeUserList"
      @next="nextStep"
      @prev="prevStep"
      @submit="submitWizard"
      @upload="handleFileUpload"
    />

    <OnboardingDetailDrawer
      v-model="detailDrawerVisible"
      :detail-row="detailRow"
    />

    <RenewContractDialog
      v-model="renewDialogVisible"
      :submitting="submitting"
      :form="renewForm"
      :rules="renewRules"
      :row="renewRow"
      @submit="submitRenew"
      @upload="handleRenewUpload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get, post } from '@/utils/request'
import { exportExcelLike } from '@/utils/exporter'
import { onboardings } from '@/api/modules'

import OnboardingStatCards from './components/onboardings/OnboardingStatCards.vue'
import OnboardingFilterBar from './components/onboardings/OnboardingFilterBar.vue'
import OnboardingTable from './components/onboardings/OnboardingTable.vue'
import OnboardingWizardDialog from './components/onboardings/OnboardingWizardDialog.vue'
import OnboardingDetailDrawer from './components/onboardings/OnboardingDetailDrawer.vue'
import RenewContractDialog from './components/onboardings/RenewContractDialog.vue'

import type { Onboarding, OnboardingFilters, OnboardingPagination, Department, Position, UserOption } from './components/onboardings/types'

// v0.3.22 拆 Onboardings.vue 1026→330 (-68%)
// 子组件: StatCards / FilterBar / Table / WizardDialog / DetailDrawer / RenewContractDialog

const loading = ref(false)
const submitting = ref(false)
const list = ref<Onboarding[]>([])
const deptList = ref<Department[]>([])
const posList = ref<Position[]>([])
const userList = ref<UserOption[]>([])

const filters = reactive<OnboardingFilters>({
  keyword: '',
  department_id: null,
  status: '',
  contract_expiring: false,
  probation_expiring: false,
})
const pagination = reactive<OnboardingPagination>({ page: 1, pageSize: 10, total: 0 })

const activeUserList = computed(() => userList.value.filter((u) => u.is_active !== false))

// 顶部状态卡（通过 ref 调用，避免 props 传 5 个 ref）
const statCardsRef = ref()

async function loadStats() {
  try {
    const r: any = await onboardings.list({ per_page: 1 })
    const total = Number(r?.total ?? r?.meta?.total ?? 0)
    statCardsRef.value?.stats[0] && (statCardsRef.value.stats[0].value = String(total))
  } catch (e) { /* ignore */ }
  try {
    const r: any = await onboardings.list({ per_page: 1, contract_expiring: 1 })
    statCardsRef.value?.stats[1] && (statCardsRef.value.stats[1].value = String(Number(r?.total ?? r?.meta?.total ?? 0)))
  } catch (e) { /* ignore */ }
  try {
    const r: any = await onboardings.list({ per_page: 1, probation_expiring: 1 })
    statCardsRef.value?.stats[2] && (statCardsRef.value.stats[2].value = String(Number(r?.total ?? r?.meta?.total ?? 0)))
  } catch (e) { /* ignore */ }
}

function deptNameOf(id?: number | null) {
  if (!id) return ''
  return deptList.value.find((d) => d.id === id)?.name || ''
}

async function loadList() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      per_page: pagination.pageSize,
    }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.department_id) params.department_id = filters.department_id
    if (filters.status) params.status = filters.status
    if (filters.contract_expiring) params.contract_expiring = 1
    if (filters.probation_expiring) params.probation_expiring = 1
    const data: any = await onboardings.list(params)
    const items = (data && data.data && data.data.data) || (data?.data || []) || []
    list.value = items
    pagination.total = Number(data?.total ?? data?.meta?.total ?? (data?.data?.total ?? 0))
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadList()
}
function handleReset() {
  filters.keyword = ''
  filters.department_id = null
  filters.status = ''
  filters.contract_expiring = false
  filters.probation_expiring = false
  pagination.page = 1
  loadList()
}

function exportList() {
  const headers = ['姓名', '工号', '部门', '岗位', '入职日期', '状态', '导师', '联系方式']
  const rows = list.value.map((o: any) => [
    o.employee_name || o.name || '-',
    o.employee_no || '-',
    o.department?.name || o.department || '-',
    o.position || '-',
    o.hire_date || '-',
    ({ pending: '待入职', onboarding: '入职中', completed: '已完成', terminated: '已离职' }[o.status as string] || o.status || '-'),
    o.mentor?.name || o.mentor || '-',
    o.phone || '-',
  ])
  exportExcelLike(headers, rows, '员工入职', { title: '员工入职管理' })
}

async function handleArchive(row: Onboarding) {
  try {
    await onboardings.archive(row.id)
    ElMessage.success('档案已归档')
    loadList()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '归档失败')
  }
}

const detailDrawerVisible = ref(false)
const detailRow = ref<Onboarding | null>(null)
async function openDetail(row: Onboarding) {
  try {
    const data: any = await onboardings.show(row.id)
    detailRow.value = data?.data || data || row
  } catch (e) {
    detailRow.value = row
  }
  detailDrawerVisible.value = true
}

// 续签合同
const renewDialogVisible = ref(false)
const renewRow = ref<Onboarding | null>(null)
const renewForm = reactive({
  contract_start_date: '',
  contract_end_date: '',
  contract_file_id: null as number | null,
  contract_file_name: '',
})
const renewRules = {
  contract_start_date: [{ required: true, message: '请选择新合同起始', trigger: 'change' }],
  contract_end_date:   [{ required: true, message: '请选择新合同结束', trigger: 'change' }],
}

function openRenewContract(row: Onboarding) {
  renewRow.value = row
  Object.assign(renewForm, {
    contract_start_date: row.contract_start_date || '',
    contract_end_date: '',
    contract_file_id: null,
    contract_file_name: '',
  })
  renewDialogVisible.value = true
}

async function handleRenewUpload(opt: any) {
  try {
    const fd = new FormData()
    fd.append('file', opt.file)
    const res: any = await post<any>('/disk/upload', fd)
    const id = res?.id || res?.file_id || res?.data?.id
    if (id) {
      renewForm.contract_file_id = id
      renewForm.contract_file_name = opt.file.name
      opt.onSuccess?.(res)
      ElMessage.success('合同已上传')
    } else {
      opt.onError?.(new Error(res?.message || '上传失败'))
    }
  } catch (e: any) {
    opt.onError?.(e)
    ElMessage.error(e?.response?.data?.message || e?.message || '上传失败')
  }
}

async function submitRenew() {
  submitting.value = true
  try {
    const payload: any = {
      contract_start_date: renewForm.contract_start_date,
      contract_end_date: renewForm.contract_end_date,
    }
    if (renewForm.contract_file_id) payload.contract_file_id = renewForm.contract_file_id
    await onboardings.update(renewRow.value!.id, payload)
    ElMessage.success('合同已续签')
    renewDialogVisible.value = false
    loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

// 入职向导
const wizardVisible = ref(false)
const wizardStep = ref(0)

const formStep1 = reactive({
  username: '',
  name: '',
  phone: '',
  email: '',
})
const rulesStep1 = {
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  name:     [{ required: true, message: '请输入姓名',     trigger: 'blur' }],
  phone:    [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
  email:    [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

const formStep2 = reactive({
  hire_date: '',
  department_id: null as number | null,
  position_id: null as number | null,
  mentor_id: null as number | null,
  probation_months: 3,
})
const rulesStep2 = {
  hire_date:       [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  department_id:   [{ required: true, message: '请选择部门',     trigger: 'change' }],
  position_id:     [{ required: true, message: '请选择岗位',     trigger: 'change' }],
}

const formStep3 = reactive({
  id_card_no: '',
  id_card_file_id: null as number | null,
  id_card_file_name: '',
  driver_license_no: '',
  driver_license_expire: '',
  driver_license_file_id: null as number | null,
  driver_license_file_name: '',
  education_level: '',
  education_school: '',
  education_major: '',
  education_file_id: null as number | null,
  education_file_name: '',
  contract_file_id: null as number | null,
  contract_file_name: '',
})

function openCreate() {
  wizardStep.value = 0
  Object.assign(formStep1, { username: '', name: '', phone: '', email: '' })
  Object.assign(formStep2, { hire_date: '', department_id: null, position_id: null, mentor_id: null, probation_months: 3 })
  Object.assign(formStep3, {
    id_card_no: '', id_card_file_id: null, id_card_file_name: '',
    driver_license_no: '', driver_license_expire: '', driver_license_file_id: null, driver_license_file_name: '',
    education_level: '', education_school: '', education_major: '', education_file_id: null, education_file_name: '',
    contract_file_id: null, contract_file_name: '',
  })
  wizardVisible.value = true
}

async function nextStep() {
  // validate 实际在子组件 OnboardingWizardDialog 里完成（emit('next', isValid)）
  wizardStep.value = Math.min(2, wizardStep.value + 1)
}
function prevStep() {
  wizardStep.value = Math.max(0, wizardStep.value - 1)
}

async function handleFileUpload(opt: any, field: 'id_card_file_id' | 'driver_license_file_id' | 'education_file_id' | 'contract_file_id') {
  const nameField = field.replace('_file_id', '_file_name') as 'id_card_file_name' | 'driver_license_file_name' | 'education_file_name' | 'contract_file_name'
  try {
    const fd = new FormData()
    fd.append('file', opt.file)
    const res: any = await post<any>('/disk/upload', fd)
    const id = res?.id || res?.file_id || res?.data?.id
    if (id) {
      formStep3[field] = id
      formStep3[nameField] = opt.file.name
      opt.onSuccess?.(res)
      ElMessage.success('上传成功')
    } else {
      opt.onError?.(new Error(res?.message || '上传失败'))
    }
  } catch (e: any) {
    opt.onError?.(e)
    ElMessage.error(e?.response?.data?.message || e?.message || '上传失败')
  }
}

async function submitWizard() {
  submitting.value = true
  try {
    const payload = {
      user: {
        username: formStep1.username,
        name: formStep1.name,
        phone: formStep1.phone || null,
        email: formStep1.email || null,
        password: '123456',
      },
      onboarding: {
        hire_date: formStep2.hire_date,
        department_id: formStep2.department_id,
        position_id: formStep2.position_id,
        mentor_id: formStep2.mentor_id || null,
        probation_months: formStep2.probation_months,
        id_card_no: formStep3.id_card_no || null,
        id_card_file_id: formStep3.id_card_file_id || null,
        driver_license_no: formStep3.driver_license_no || null,
        driver_license_expire: formStep3.driver_license_expire || null,
        driver_license_file_id: formStep3.driver_license_file_id || null,
        education_level: formStep3.education_level || null,
        education_school: formStep3.education_school || null,
        education_major: formStep3.education_major || null,
        education_file_id: formStep3.education_file_id || null,
        contract_file_id: formStep3.contract_file_id || null,
      },
    }
    await onboardings.create(payload)
    ElMessage.success('入职办理成功，初始密码 123456')
    wizardVisible.value = false
    loadList()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

async function loadAll() {
  try {
    const [d, p, u] = await Promise.all([
      get('/employees/departments').catch(() => []),
      get('/employees/positions').catch(() => []),
      get('/employees', { per_page: 200 }).catch(() => null),
    ])
    deptList.value = (d as any) || []
    posList.value = (p as any) || []
    const users: any = (u as any)
    userList.value = (users && users.data && users.data.data) || (users?.data || []) || []
  } catch (e) { /* ignore */ }
}

onMounted(async () => {
  await Promise.all([loadAll(), loadList(), loadStats()])
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 20px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f5f7fa;
  min-height: 100%;
}
</style>
