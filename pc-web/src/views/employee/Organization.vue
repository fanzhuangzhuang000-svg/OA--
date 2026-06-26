<template>
  <div class="employee-container">
    <!-- 顶部 Tab 切换 -->
    <div class="tab-bar">
      <div class="tab-bar__left">
        <span class="tab-bar__title">员工管理</span>
      </div>
      <div class="tab-bar__nav">
        <div
          v-for="t in tabs"
          :key="t.key"
          class="tab-bar__item"
          :class="{ 'is-active': activeTab === t.key }"
          @click="activeTab = t.key"
        >
          <el-icon v-if="t.icon" :size="14"><component :is="t.icon" /></el-icon>
          <span>{{ t.label }}</span>
        </div>
      </div>
    </div>

    <!-- Tab 1: 员工列表（左树右表） -->
    <div v-show="activeTab === 'list'" class="tab-panel">
      <div class="employee-toolbar">
        <el-input
          v-model="listFilters.keyword"
          placeholder="搜索姓名/手机/工号"
          clearable
          :prefix-icon="Search"
          style="width: 240px"
          @keyup.enter="handleListSearch"
          @clear="handleListSearch"
        />
        <el-select v-model="listFilters.department_id" placeholder="部门" clearable style="width: 160px" @change="handleListSearch">
          <el-option v-for="d in deptList" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
        <el-select v-model="listFilters.status" placeholder="状态" clearable style="width: 120px" @change="handleListSearch">
          <el-option label="在职" value="active" />
          <el-option label="离职" value="inactive" />
        </el-select>
        <el-button type="primary" @click="handleListSearch">查询</el-button>
        <el-button @click="handleListReset">重置</el-button>
        <span class="toolbar-spacer" />
        <el-button @click="goOnboardings">📋 入职档案</el-button>
        <el-button @click="goResignations">🚪 离职办理</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateEmployee">+ 新建员工</el-button>
      </div>

      <div class="employee-body">
        <div class="employee-body__tree">
          <CategoryTree
            v-model="selectedDeptId"
            :departments="deptList"
            :positions="posList"
            @refresh="onTreeRefresh"
          />
        </div>
        <div class="employee-body__table">
          <el-card class="table-card" shadow="never">
            <template #header>
              <div class="card-header">
                <span class="card-header__bar" />
                <span class="card-header__title">员工列表</span>
                <span class="card-header__count">{{ pagination.total }}</span>
                <span class="card-header__suffix">名员工</span>
              </div>
            </template>
            <EmployeeListTable
              :list="tableData"
              :loading="loading"
              :page="pagination.page"
              :page-size="pagination.pageSize"
              :total="pagination.total"
              @edit="openEditEmployee"
              @delete="handleDeleteEmployee"
              @page-change="(p: number) => { pagination.page = p; loadEmployees() }"
              @size-change="(s: number) => { pagination.pageSize = s; pagination.page = 1; loadEmployees() }"
            />
          </el-card>
        </div>
      </div>
    </div>

    <!-- Tab 2: 组织架构（完整版） -->
    <div v-show="activeTab === 'org'" class="tab-panel org-tab">
      <div class="employee-body">
        <div class="employee-body__tree">
          <CategoryTree
            :departments="deptList"
            :positions="posList"
            :show-actions="true"
            @refresh="onTreeRefresh"
            @edit-dept="openEditDept"
            @edit-pos="openEditPos"
            @delete-dept="handleDeleteDept"
            @delete-pos="handleDeletePos"
          />
        </div>
        <div class="employee-body__table">
          <el-card class="table-card" shadow="never">
            <template #header>
              <div class="card-header">
                <span class="card-header__bar" />
                <span class="card-header__title">{{ detailTitle }}</span>
                <span class="card-header__count" v-if="detailCount > 0">{{ detailCount }}</span>
                <span class="card-header__suffix" v-if="selectedDetailNode">名员工</span>
                <div class="card-header__actions">
                  <el-button size="small" :icon="Plus" @click="openAddDept">新增部门</el-button>
                  <el-button size="small" :icon="Plus" @click="openAddPos">新增岗位</el-button>
                </div>
              </div>
            </template>

            <template v-if="selectedDetailNode && (selectedDetailNode.type === 'dept' || selectedDetailNode.type === 'position')">
              <NodeDetailInfo
                :node="selectedDetailNode"
                :fallback-name="sysConfig.settings.system_name"
                :sub-position-count="subPositionCount"
              />
            </template>
            <template v-else>
              <div class="company-card">
                <el-icon :size="32" color="#0C447C"><OfficeBuilding /></el-icon>
                <div class="company-card__main">
                  <div class="company-card__label">公司名称</div>
                  <div class="company-card__name">{{ sysConfig.settings.system_name || 'OA科技有限公司' }}</div>
                </div>
                <el-button type="primary" link :icon="Edit" @click="openRenameCompany">重命名</el-button>
              </div>
              <div class="company-hint">
                <el-icon :size="14" color="#909399"><InfoFilled /></el-icon>
                <span>鼠标悬停左侧树根节点或双击节点文字可直接重命名，右键公司节点也可重命名。修改会同步到系统设置。</span>
              </div>
            </template>

            <NodeMembersTable
              :node="selectedDetailNode"
              :members="memberList"
              :loading="loadingMembers"
            />
          </el-card>
        </div>
      </div>
    </div>

    <!-- Tab 3/4 占位 -->
    <div v-show="activeTab === 'onboarding'" class="tab-panel placeholder">
      <el-empty description="入职档案模块" />
    </div>
    <div v-show="activeTab === 'resignation'" class="tab-panel placeholder">
      <el-empty description="离职办理模块" />
    </div>

    <!-- 新建/编辑员工对话框 -->
    <EmployeeDialog
      v-model:visible="employeeDialogVisible"
      :submitting="submitting"
      :target="editingEmployee"
      :roles="roles"
      :dept-list="deptList"
      :pos-list="posList"
      :selected-skill-ids="selectedSkillIds"
      :skill-options="skillOptions"
      :loading-skill-options="loadingSkillOptions"
      @submit="submitEmployee"
    />

    <!-- 部门编辑对话框 -->
    <DeptDialog
      v-model:visible="deptDialogVisible"
      :submitting="submitting"
      :target="editingDept"
      :all-dept-options="allDeptOptions"
      :user-list="userList"
      @submit="submitDept"
    />

    <!-- 岗位编辑对话框 -->
    <PositionDialog
      v-model:visible="posDialogVisible"
      :submitting="submitting"
      :target="editingPos"
      :all-dept-options="allDeptOptions"
      @submit="submitPos"
    />

    <!-- 公司名重命名对话框 -->
    <CompanyRenameDialog
      v-model:visible="companyDialogVisible"
      :form="companyForm"
      :submitting="submitting"
      @submit="submitCompanyRename"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, InfoFilled, User, OfficeBuilding, Files, SwitchButton, Edit,
} from '@element-plus/icons-vue'
import { get, post, put, del } from '@/utils/request'
import CompanyRenameDialog from './components/organization-v2/CompanyRenameDialog.vue'
import NodeDetailInfo from './components/organization-v2/NodeDetailInfo.vue'
import NodeMembersTable from './components/organization-v2/NodeMembersTable.vue'
import EmployeeListTable from './components/organization-list/EmployeeListTable.vue'
import { useSystemConfigStore } from '@/stores/systemConfig'
import CategoryTree from './components/CategoryTree.vue'
import EmployeeDialog from './components/EmployeeDialog.vue'
import DeptDialog from './components/DeptDialog.vue'
import PositionDialog from './components/PositionDialog.vue'
import type { EmployeeForm, DeptForm, PositionForm } from './orgTypes'

const router = useRouter()
const route = useRoute()
const sysConfig = useSystemConfigStore()

// ============== Tab 切换 ==============
type TabKey = 'list' | 'org' | 'onboarding' | 'resignation'
const activeTab = ref<TabKey>('list')
const tabs = [
  { key: 'list' as TabKey,        label: '员工列表',   icon: User },
  { key: 'org' as TabKey,         label: '组织架构',   icon: OfficeBuilding },
  { key: 'onboarding' as TabKey,  label: '入职档案',   icon: Files },
  { key: 'resignation' as TabKey, label: '离职办理',   icon: SwitchButton },
]

// 根据路由 meta 决定初始 tab
onMounted(() => {
  if (route.path.includes('/org')) activeTab.value = 'org'
})

function goOnboardings() {
  router.push('/employee/onboardings')
}
function goResignations() {
  router.push('/employee/resignations')
}

// ============== 通用 ==============
const submitting = ref(false)
const deptList = ref<any[]>([])
const posList = ref<any[]>([])
const userList = ref<any[]>([])
const roles = ref<any[]>([])

const allDeptOptions = computed(() => deptList.value.map((d) => ({ id: d.id, name: d.name })))
function deptNameOf(id?: number | null) {
  if (!id) return ''
  return deptList.value.find((d) => d.id === id)?.name || ''
}

// ============== Tab 1: 员工列表 ==============
const selectedDeptId = ref<number | null>(null)
const listFilters = reactive({ keyword: '', department_id: null as number | null, status: '' })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref<any[]>([])
const loading = ref(false)

// 部门树选中 → 同步到筛选条
watch(selectedDeptId, (v) => {
  listFilters.department_id = v
  handleListSearch()
})

async function loadEmployees() {
  loading.value = true
  try {
    const params: any = { page: pagination.page, per_page: pagination.pageSize }
    if (listFilters.keyword)       params.keyword       = listFilters.keyword
    if (listFilters.department_id) params.department_id = listFilters.department_id
    if (listFilters.status)        params.status        = listFilters.status
    const data: any = await get('/employees', params)
    tableData.value = data?.data || data || []
    pagination.total = Number(data?.total ?? data?.meta?.total ?? 0)
  } catch (e) {
    console.warn('[loadEmployees]', e)
  } finally {
    loading.value = false
  }
}

function handleListSearch() {
  pagination.page = 1
  loadEmployees()
}
function handleListReset() {
  listFilters.keyword = ''
  listFilters.department_id = null
  listFilters.status = ''
  selectedDeptId.value = null
  pagination.page = 1
  loadEmployees()
}

function onTreeRefresh(_payload: any) {
  // 树数据变化时刷新（部门/岗位 CRUD 后）
  loadEmployees()
}

// ---- 新建/编辑员工 (dialog 内嵌子组件) ----
const employeeDialogVisible = ref(false)
const editingEmployee = ref<any | null>(null)
const skillOptions = ref<any[]>([])
const selectedSkillIds = ref<(number | string)[]>([])
const loadingSkillOptions = ref(false)

async function loadSkillOptions() {
  loadingSkillOptions.value = true
  try {
    const { data } = await get('/employees/skills')
    skillOptions.value = Array.isArray(data) ? data : data?.data || []
  } catch {
    skillOptions.value = []
  } finally {
    loadingSkillOptions.value = false
  }
}

async function loadEmployeeSkills(userId: number) {
  try {
    const { data } = await get(`/employees/${userId}/skills`)
    selectedSkillIds.value = (Array.isArray(data) ? data : data?.data || []).map((tag: any) => tag.id)
  } catch {
    selectedSkillIds.value = []
  }
}

async function syncEmployeeSkills(userId: number, targetIds: (number | string)[]) {
  const { data } = await get(`/employees/${userId}/skills`)
  const currentIds = new Set((Array.isArray(data) ? data : data?.data || []).map((tag: any) => Number(tag.id)))
  const idsToAttach = targetIds.map((id) => Number(id)).filter((id) => id && !currentIds.has(id))
  const idsToDetach = [...currentIds].filter((id) => !targetIds.some((targetId) => Number(targetId) === id))
  await Promise.all(idsToAttach.map((tagId) => post(`/employees/skills/${tagId}/attach`, { user_id: userId })))
  await Promise.all(idsToDetach.map((tagId) => post(`/employees/skills/${tagId}/detach`, { user_id: userId })))
}

function openCreateEmployee() {
  editingEmployee.value = null
  employeeDialogVisible.value = true
  loadSkillOptions()
  selectedSkillIds.value = []
}

function openEditEmployee(row: any) {
  editingEmployee.value = row
  employeeDialogVisible.value = true
  loadSkillOptions()
  loadEmployeeSkills(row.id)
}

async function submitEmployee({
  form,
  selectedSkillIds: skillIds,
  isEdit,
}: {
  form: EmployeeForm
  selectedSkillIds: number[]
  isEdit: boolean
}) {
  submitting.value = true
  try {
    const payload: any = {
      name: form.name,
      department_id: form.department_id,
      position_id: form.position_id,
      phone: form.phone,
      email: form.email,
      is_active: form.is_active,
    }
    if (form.hire_date) payload.hire_date = form.hire_date
    let res: any = null
    if (isEdit) {
      res = await put(`/employees/${editingEmployee.value.id}`, payload)
      ElMessage.success('员工已更新')
    } else {
      payload.username = form.username
      payload.password = form.password || '123456'
      if (form.role_id) payload.role_id = form.role_id
      res = await post('/employees', payload)
      ElMessage.success('员工已创建，初始密码 ' + (form.password || '123456'))
    }
    const savedId = editingEmployee.value?.id || res?.id || res?.data?.id
    if (savedId && skillIds.length) {
      await syncEmployeeSkills(savedId, skillIds)
    }
    employeeDialogVisible.value = false
    loadEmployees()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeleteEmployee(row: any) {
  try {
    await del(`/employees/${row.id}`)
    ElMessage.success('员工已删除')
    if (tableData.value.length === 1 && pagination.page > 1) pagination.page -= 1
    loadEmployees()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

// ============== Tab 2: 组织架构 ==============
const selectedDetailNode = ref<any | null>(null)
const memberList = ref<any[]>([])
const loadingMembers = ref(false)
const treeFilter = ref('')

const detailTitle = computed(() => {
  if (!selectedDetailNode.value) return '组织详情'
  const n = selectedDetailNode.value
  if (n.type === 'dept') return n.label
  if (n.type === 'position') return n.label
  return '组织详情'
})
const detailCount = computed(() => memberList.value.length)
const subPositionCount = computed(() => {
  if (!selectedDetailNode.value || selectedDetailNode.value.type !== 'dept') return 0
  const deptId = Number(String(selectedDetailNode.value.id).replace('d-', ''))
  return posList.value.filter((p) => p.department_id === deptId).length
})

async function loadDetailMembers(node: any) {
  if (!node) {
    memberList.value = []
    return
  }
  loadingMembers.value = true
  try {
    if (node.type === 'dept') {
      const deptId = Number(String(node.id).replace('d-', ''))
      const list = userList.value.filter((u: any) => u.department_id === deptId)
      memberList.value = list.map((u: any) => ({
        id: u.id, name: u.name, username: u.username,
        position: posList.value.find((p) => p.id === u.position_id)?.name || '--',
        phone: u.phone || '--', is_active: u.is_active,
      }))
    } else if (node.type === 'position') {
      const posId = Number(String(node.id).replace('p-', ''))
      const list = userList.value.filter((u: any) => u.position_id === posId)
      memberList.value = list.map((u: any) => ({
        id: u.id, name: u.name, username: u.username,
        position: posList.value.find((p) => p.id === u.position_id)?.name || '--',
        phone: u.phone || '--', is_active: u.is_active,
      }))
    } else {
      memberList.value = userList.value.map((u: any) => ({
        id: u.id, name: u.name, username: u.username,
        position: posList.value.find((p) => p.id === u.position_id)?.name || '--',
        phone: u.phone || '--', is_active: u.is_active,
      }))
    }
  } finally {
    loadingMembers.value = false
  }
}

function onOrgNodeClick(node: any) {
  selectedDetailNode.value = node
  loadDetailMembers(node)
}

// ---- 部门 CRUD ----
const deptDialogVisible = ref(false)
const editingDept = ref<any | null>(null)

function openAddDept() {
  editingDept.value = null
  deptDialogVisible.value = true
}

function openEditDept(data: any) {
  const deptId = Number(String(data.id).replace('d-', ''))
  const d = deptList.value.find((x) => x.id === deptId)
  if (!d) return
  editingDept.value = d
  deptDialogVisible.value = true
}

async function submitDept({ form, isEdit }: { form: DeptForm; isEdit: boolean }) {
  submitting.value = true
  try {
    const payload: any = {
      name: form.name,
      parent_id: form.parent_id || null,
      manager_id: form.manager_id || null,
      sort_order: form.sort_order,
    }
    if (isEdit) {
      delete payload.parent_id
      await put(`/employees/departments/${editingDept.value.id}`, payload)
      ElMessage.success('部门已更新')
    } else {
      await post('/employees/departments', payload)
      ElMessage.success('部门已创建')
    }
    deptDialogVisible.value = false
    await loadAll()
    if (selectedDetailNode.value) loadDetailMembers(selectedDetailNode.value)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeleteDept(data: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除部门「${data.name}」? 有子部门或员工将无法删除`,
      '确认删除', { type: 'warning' },
    )
  } catch { return }
  try {
    const id = Number(String(data.id).replace('d-', ''))
    await del(`/employees/departments/${id}`)
    ElMessage.success('部门已删除')
    selectedDetailNode.value = null
    memberList.value = []
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

// ---- 岗位 CRUD ----
const posDialogVisible = ref(false)
const editingPos = ref<any | null>(null)

function openAddPos() {
  editingPos.value = null
  posDialogVisible.value = true
}

function openEditPos(data: any) {
  const posId = Number(String(data.id).replace('p-', ''))
  const p = posList.value.find((x) => x.id === posId)
  if (!p) return
  editingPos.value = p
  posDialogVisible.value = true
}

async function submitPos({ form, isEdit }: { form: PositionForm; isEdit: boolean }) {
  submitting.value = true
  try {
    const payload: any = {
      name: form.name,
      department_id: form.department_id,
      level: form.level,
      description: form.description || null,
      sort_order: form.sort_order,
    }
    if (isEdit) {
      await put(`/employees/positions/${editingPos.value.id}`, payload)
      ElMessage.success('岗位已更新')
    } else {
      await post('/employees/positions', payload)
      ElMessage.success('岗位已创建')
    }
    posDialogVisible.value = false
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeletePos(data: any) {
  try {
    await ElMessageBox.confirm(`确定删除岗位「${data.name}」?`, '确认删除', { type: 'warning' })
  } catch { return }
  try {
    const id = Number(String(data.id).replace('p-', ''))
    await del(`/employees/positions/${id}`)
    ElMessage.success('岗位已删除')
    if (selectedDetailNode.value && selectedDetailNode.value.id === data.id) {
      selectedDetailNode.value = null
      memberList.value = []
    }
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

// ---- 公司名重命名 ----
const companyDialogVisible = ref(false)
const companyFormRef = ref()
const companyForm = reactive({ name: '' })

function openRenameCompany() {
  companyForm.name = sysConfig.settings.system_name || ''
  companyDialogVisible.value = true
}

async function submitCompanyRename() {
  const valid = await companyFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const ok = await sysConfig.saveSettings({ system_name: companyForm.name.trim() } as any)
    if (!ok) {
      ElMessage.error('保存失败')
      return
    }
    ElMessage.success('公司名已更新')
    companyDialogVisible.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

// ============== 加载 ==============
async function loadAll() {
  const [d, p, u] = await Promise.all([
    get('/employees/departments'),
    get('/employees/positions'),
    get('/employees', { per_page: 200 }),
  ])
  deptList.value = d || []
  posList.value = p || []
  userList.value = (u && u.data && u.data.data) || []
}

onMounted(async () => {
  try {
    await Promise.all([
      loadAll(),
      loadEmployees(),
      (async () => {
        const r: any = await get('/roles').catch(() => null)
        roles.value = (r && r.data) || []
      })(),
    ])
  } catch (e) {
    /* ignore */
  }
})
</script>

<style lang="scss" scoped>
.employee-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 20px 20px;
  background: #f5f7fa;
  gap: 12px;
  overflow: hidden;
}

.tab-bar {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 4px 16px;
  height: 48px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
  &__title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    padding-right: 16px;
    border-right: 1px solid #ebeef5;
    margin-right: 12px;
  }
  &__nav {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  &__item {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 14px;
    font-size: 14px;
    color: #606266;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    &:hover { color: #0C447C; background: #f0f4fa; }
    &.is-active {
      color: #0C447C;
      background: #f0f4fa;
      font-weight: 600;
    }
  }
}

.tab-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.placeholder {
  align-items: center;
  justify-content: center;
}

.employee-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  .toolbar-spacer { flex: 1; }
}

.employee-body {
  flex: 1;
  display: flex;
  gap: 12px;
  min-height: 0;
  &__tree {
    width: 280px;
    flex-shrink: 0;
    min-height: 0;
  }
  &__table {
    flex: 1;
    min-width: 0;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }
}

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  :deep(.el-card__header) {
    padding: 0 20px;
    height: 48px;
  }
  :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px 20px;
    min-height: 0;
  }
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 48px;
  &__bar {
    width: 3px;
    height: 14px;
    border-radius: 2px;
    background: linear-gradient(180deg, #0C447C 0%, #1D9E75 100%);
  }
  &__title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
  }
  &__count {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 16px;
    font-weight: 700;
    color: #0C447C;
    font-variant-numeric: tabular-nums;
  }
  &__suffix {
    font-size: 13px;
    color: #909399;
  }
  &__actions {
    margin-left: auto;
    display: flex;
    gap: 8px;
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.detail-info {
  margin-bottom: 16px;
  .info-row {
    display: flex;
    padding: 8px 0;
    border-bottom: 1px dashed #ebeef5;
    .info-label { width: 100px; color: #909399; font-size: 14px; }
    .info-value { color: #303133; font-size: 14px; }
  }
}
.detail-divider {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #0C447C;
}
.detail-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #909399;
  p { margin-top: 12px; font-size: 14px; }
}

.company-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, rgba(12, 68, 124, 0.04) 0%, rgba(29, 158, 117, 0.04) 100%);
  border: 1px solid #e6ebf2;
  border-left: 3px solid #0C447C;
  border-radius: 8px;
  &__main {
    flex: 1;
    min-width: 0;
  }
  &__label {
    font-size: 12px;
    color: #909399;
    margin-bottom: 4px;
  }
  &__name {
    font-size: 18px;
    font-weight: 700;
    color: #303133;
    letter-spacing: 0.5px;
  }
}
.company-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  border-radius: 4px;
}

.org-tab .employee-body {
  height: 100%;
}
</style>
