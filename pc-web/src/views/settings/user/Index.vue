<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">用户管理</span>
      <div class="header-actions">
        <el-tag type="info" size="large">共 {{ total }} 人</el-tag>
        <el-tag type="warning" size="large" v-if="expiringCount > 0" style="margin-left: 8px;">
          <el-icon><Warning /></el-icon>
          {{ expiringCount }} 个临时角色即将过期
        </el-tag>
      </div>
    </div>

    <div class="content-card">
      <div class="filter-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索用户名 / 姓名 / 邮箱"
          clearable
          style="width: 280px"
          :prefix-icon="Search"
          @input="debouncedSearch"
        />
        <el-select v-model="filterRole" placeholder="按角色筛选" clearable style="width: 160px" @change="fetchUsers">
          <el-option v-for="r in roleOptions" :key="r" :label="r" :value="r" />
        </el-select>
        <el-select v-model="filterType" placeholder="角色类型" clearable style="width: 140px" @change="fetchUsers">
          <el-option label="全部" value="" />
          <el-option label="含临时" value="has_temporary" />
          <el-option label="仅永久" value="permanent_only" />
        </el-select>
        <el-button @click="fetchUsers" :icon="Refresh">刷新</el-button>
      </div>

      <el-table :data="filteredUsers" border stripe style="width: 100%;" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="32" style="background: #409EFF; color: white;">
                {{ (row.name || row.username || '?').charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ row.name || row.username }}</div>
                <div class="user-username">@{{ row.username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="当前角色" min-width="240">
          <template #default="{ row }">
            <template v-if="row.roles?.length">
              <el-tag
                v-for="r in row.roles"
                :key="r"
                :type="roleColor(r)"
                size="small"
                effect="dark"
                style="margin-right: 4px;"
              >
                {{ r }}
              </el-tag>
            </template>
            <span v-else class="text-muted">无</span>
          </template>
        </el-table-column>
        <el-table-column label="临时角色" min-width="200">
          <template #default="{ row }">
            <template v-if="row.temporaryRoles?.length">
              <el-tooltip
                v-for="(tr, idx) in row.temporaryRoles"
                :key="idx"
                placement="top"
              >
                <template #content>
                  <div>到期: {{ tr.expires_at_text }}</div>
                  <div>剩余: {{ tr.days_left }} 天</div>
                  <div v-if="tr.reason">理由: {{ tr.reason }}</div>
                </template>
                <el-tag
                  :type="tr.days_left <= 3 ? 'danger' : (tr.days_left <= 7 ? 'warning' : 'success')"
                  size="small"
                  effect="plain"
                  style="margin-right: 4px;"
                >
                  <el-icon><Clock /></el-icon>
                  {{ tr.role }} · {{ tr.days_left }}天
                </el-tag>
              </el-tooltip>
            </template>
            <span v-else class="text-muted">无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :icon="Setting" @click="handleEditRoles(row)">
              分配角色
            </el-button>
            <el-button link type="warning" size="small" :icon="Clock" @click="handleGrantTemporary(row)">
              临时授权
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="perPage"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchUsers"
          @size-change="fetchUsers"
        />
      </div>
    </div>

    <!-- 分配永久角色 dialog -->
    <el-dialog v-model="dialogVisible" :title="`为「${editingUser?.username}」分配永久角色`" width="520px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <el-input :value="editingUser?.name || editingUser?.username" disabled />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-checkbox-group v-model="selectedRoles">
            <el-checkbox v-for="r in roleOptions" :key="r" :label="r" :value="r">
              <el-tag :type="roleColor(r)" size="small" effect="dark">{{ r }}</el-tag>
              <span class="role-desc">{{ roleDesc(r) }}</span>
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-alert
          v-if="!selectedRoles.length"
          type="warning"
          :closable="false"
          title="至少选一个角色, 否则该用户登录后将无任何权限"
        />
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRoles" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 临时授权 dialog (V0.5.3) -->
    <el-dialog v-model="tempDialogVisible" :title="`为「${editingUser?.username}」分配临时角色`" width="720px" @open="loadUserAssignments">
      <el-form label-width="90px">
        <el-form-item label="用户">
          <el-input :value="editingUser?.name || editingUser?.username" disabled />
        </el-form-item>

        <!-- 当前角色列表 (含过期状态) -->
        <el-form-item label="当前授权" v-if="currentAssignments.length">
          <div class="assignment-list">
            <div
              v-for="(a, idx) in currentAssignments"
              :key="idx"
              class="assignment-item"
              :class="`status-${a.status}`"
            >
              <el-tag :type="roleColor(a.name)" size="small" effect="dark">{{ a.name }}</el-tag>
              <span class="assignment-status">
                <template v-if="a.status === 'permanent'">
                  <el-tag type="info" size="small">永久</el-tag>
                </template>
                <template v-else-if="a.status === 'temporary'">
                  <el-tag type="warning" size="small">临时</el-tag>
                  <span class="muted">到期 {{ a.expires_at_text }} · 余 {{ a.days_left }} 天</span>
                </template>
                <template v-else>
                  <el-tag type="danger" size="small">已过期</el-tag>
                </template>
              </span>
              <span v-if="a.reason" class="assignment-reason">{{ a.reason }}</span>
            </div>
          </div>
          <div class="hint">⚠️ 临时角色有期限；分配会**替换**该用户所有当前临时角色</div>
        </el-form-item>

        <!-- 临时角色表单 -->
        <el-form-item label="临时角色" required>
          <div class="temp-roles">
            <div
              v-for="(entry, idx) in tempRoles"
              :key="idx"
              class="temp-row"
            >
              <el-select v-model="entry.role" placeholder="选角色" style="width: 160px">
                <el-option v-for="r in roleOptions" :key="r" :label="r" :value="r" />
              </el-select>
              <el-date-picker
                v-model="entry.expires_at"
                type="datetime"
                placeholder="选择过期时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DD HH:mm:ss"
                :disabled-date="(d: Date) => d.getTime() < Date.now() - 86400000"
                style="width: 220px"
              />
              <el-input
                v-model="entry.reason"
                placeholder="理由（如：项目借调 7 天）"
                maxlength="200"
                show-word-limit
                style="flex: 1"
              />
              <el-button
                type="danger"
                link
                :icon="Delete"
                @click="removeTempRow(idx)"
                v-if="tempRoles.length > 1"
              />
            </div>
            <el-button :icon="Plus" link type="primary" @click="addTempRow">+ 添加临时角色</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tempDialogVisible = false">取消</el-button>
        <el-button type="warning" :icon="Clock" @click="saveTemporary" :loading="tempSaving">分配临时角色</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Setting, Clock, Delete, Plus, Warning } from '@element-plus/icons-vue'
import { get, put, post } from '@/utils/request'

// 4 核心角色
const roleOptions = ['admin', 'finance', 'manager', 'user']

const roleColor = (r: string) => {
  return { admin: 'danger', finance: 'warning', manager: 'primary', user: 'info' }[r] || ''
}
const roleDesc = (r: string) => {
  return {
    admin:   '系统最高权限',
    finance: '财务（继承 user）',
    manager: '项目经理/部门经理（继承 user）',
    user:    '普通员工',
  }[r] || ''
}

const keyword = ref('')
const filterRole = ref('')
const filterType = ref('')
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const users = ref<any[]>([])
const loading = ref(false)
const expiringCount = ref(0)

// ================= 永久角色 dialog =================
const dialogVisible = ref(false)
const editingUser = ref<any>(null)
const selectedRoles = ref<string[]>([])
const saving = ref(false)

// ================= 临时角色 dialog (V0.5.3) =================
const tempDialogVisible = ref(false)
const tempSaving = ref(false)
const currentAssignments = ref<any[]>([])
interface TempRoleEntry { role: string; expires_at: string; reason: string }
const tempRoles = ref<TempRoleEntry[]>([
  { role: '', expires_at: '', reason: '' },
])

// 客户端过滤 (基于后端返回的 augmented data)
const filteredUsers = computed(() => {
  let arr = users.value
  if (filterRole.value) {
    arr = arr.filter(u => (u.roles || []).includes(filterRole.value))
  }
  if (filterType.value === 'has_temporary') {
    arr = arr.filter(u => (u.temporaryRoles || []).length > 0)
  } else if (filterType.value === 'permanent_only') {
    arr = arr.filter(u => !(u.temporaryRoles || []).length)
  }
  return arr
})

let debounceTimer: any = null
const debouncedSearch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    fetchUsers()
  }, 300)
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res: any = await get('/users', { keyword: keyword.value, per_page: perPage.value, page: page.value })
    const data = res.data || res
    const list = data.data || []

    // 并发拉每个用户的 assignments (V0.5.3)
    const augmented = await Promise.all(list.map(async (u: any) => {
      try {
        const detail: any = await get(`/users/${u.id}/roles`)
        const assignments = detail.data?.assignments || []
        return {
          ...u,
          temporaryRoles: assignments
            .filter((a: any) => a.status === 'temporary')
            .map((a: any) => ({
              role: a.name,
              expires_at: a.expires_at,
              expires_at_text: a.expires_at ? new Date(a.expires_at).toLocaleString('zh-CN') : '',
              days_left: a.days_left,
              reason: a.reason,
            })),
        }
      } catch {
        return { ...u, temporaryRoles: [] }
      }
    }))

    users.value = augmented
    total.value = data.total || 0
    expiringCount.value = augmented.reduce(
      (sum, u) => sum + (u.temporaryRoles || []).filter((tr: any) => tr.days_left <= 7).length,
      0
    )
  } catch (e: any) {
    ElMessage.error('加载用户失败: ' + (e?.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleEditRoles = (row: any) => {
  editingUser.value = row
  selectedRoles.value = [...(row.roles || [])]
  dialogVisible.value = true
}

const saveRoles = async () => {
  if (!editingUser.value) return
  saving.value = true
  try {
    await put(`/users/${editingUser.value.id}/roles`, { roles: selectedRoles.value })
    ElMessage.success('角色已更新')
    dialogVisible.value = false
    await fetchUsers()
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// ================= V0.5.3 临时授权 =================
const handleGrantTemporary = (row: any) => {
  editingUser.value = row
  tempDialogVisible.value = true
}

const loadUserAssignments = async () => {
  if (!editingUser.value) return
  try {
    const res: any = await get(`/users/${editingUser.value.id}/roles`)
    currentAssignments.value = res.data?.assignments || []
  } catch (e: any) {
    ElMessage.error('加载角色失败')
    currentAssignments.value = []
  }
  // 初始化一个空行
  if (!tempRoles.value[0].role) {
    tempRoles.value = [{ role: 'user', expires_at: '', reason: '' }]
  }
}

const addTempRow = () => {
  tempRoles.value.push({ role: '', expires_at: '', reason: '' })
}

const removeTempRow = (idx: number) => {
  tempRoles.value.splice(idx, 1)
}

const saveTemporary = async () => {
  if (!editingUser.value) return

  // 校验
  const valid = tempRoles.value.filter(r => r.role && r.expires_at)
  if (valid.length === 0) {
    ElMessage.warning('请至少填写一个有效的临时角色（角色+过期时间）')
    return
  }

  tempSaving.value = true
  try {
    await post(`/users/${editingUser.value.id}/roles/temporary`, {
      assignments: valid.map(r => ({
        role: r.role,
        expires_at: r.expires_at,
        reason: r.reason || undefined,
      })),
    })
    ElMessage.success(`已分配 ${valid.length} 个临时角色`)
    tempDialogVisible.value = false
    // 重置表单
    tempRoles.value = [{ role: '', expires_at: '', reason: '' }]
    await fetchUsers()
  } catch (e: any) {
    ElMessage.error('分配失败: ' + (e?.message || '未知错误'))
  } finally {
    tempSaving.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-title { font-size: 20px; font-weight: 600; }
.header-actions { display: flex; align-items: center; }
.content-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-info { display: flex; flex-direction: column; }
.user-name { font-weight: 500; }
.user-username { font-size: 12px; color: #909399; }
.text-muted { color: #c0c4cc; font-size: 12px; }
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.role-desc {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

// V0.5.3 临时授权 dialog 样式
.assignment-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background: #f8f9fb;
  border-radius: 6px;
}
.assignment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
  &.status-expired { opacity: 0.55; }
}
.assignment-status {
  display: flex;
  align-items: center;
  gap: 6px;
  .muted { color: #909399; font-size: 12px; }
}
.assignment-reason {
  font-size: 12px;
  color: #606266;
  font-style: italic;
  margin-left: auto;
}
.hint {
  margin-top: 6px;
  font-size: 12px;
  color: #e6a23c;
}
.temp-roles {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}
.temp-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
