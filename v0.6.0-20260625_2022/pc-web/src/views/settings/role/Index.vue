<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">角色管理</span>
      <div class="header-actions">
        <el-button :icon="Grid" @click="goMatrix">权限矩阵</el-button>
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增角色</el-button>
      </div>
    </div>

    <div class="content-card">
      <div class="filter-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索角色名称 / 描述"
          clearable
          style="width: 280px"
          :prefix-icon="Search"
          @input="debouncedSearch"
        />
        <el-button @click="fetchRoles" :icon="Refresh">刷新</el-button>
      </div>

      <el-table :data="roles" border stripe style="width: 100%;" v-loading="loading">
        <el-table-column prop="name" label="角色名称" width="180">
          <template #default="{ row }">
            <div class="role-name">
              <el-icon :size="18" :color="row.color"><Avatar /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
        <el-table-column prop="memberCount" label="成员数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.memberCount }}人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permCount" label="权限数" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.permCount > 25 ? 'danger' : row.permCount > 15 ? 'warning' : 'primary'" size="small">{{ row.permCount }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ row.createTime }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :icon="Key" @click="handlePermission(row)">权限配置</el-button>
            <el-button link type="primary" size="small" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm :title="`确定删除「${row.name}」？`" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger" size="small" :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="perPage"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="fetchRoles"
        @size-change="fetchRoles"
      />
    </div>

    <!-- 新增/编辑角色对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="1500px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="请输入角色名称" maxlength="64" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入角色描述" maxlength="255" />
        </el-form-item>
        <el-form-item label="徽章色">
          <el-color-picker v-model="form.color" />
          <span style="margin-left: 8px; font-size: 12px; color: #909399">用于角色标签的展示色</span>
        </el-form-item>
        <el-form-item label="权限">
          <el-tree
            ref="formPermTreeRef"
            :data="permTree"
            show-checkbox
            node-key="name"
            :default-checked-keys="form.permissionNames"
            :props="{ children: 'children', label: 'label' }"
            style="max-height: 300px; overflow: auto; border: 1px solid #ebeef5; border-radius: 4px; padding: 8px; width: 100%"
          >
            <template #default="{ data }">
              <span class="perm-node">
                <el-icon :size="16" :color="data.children ? '#0C447C' : '#1D9E75'">
                  <FolderOpened v-if="data.children" />
                  <Check v-else />
                </el-icon>
                <span>{{ data.label }}</span>
              </span>
            </template>
          </el-tree>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog v-model="permDialogVisible" title="权限配置" width="1500px" destroy-on-close>
      <div class="perm-info">
        <span>当前角色：<strong>{{ currentRole?.name }}</strong></span>
        <el-button type="primary" link @click="toggleAllExpand">{{ expandAll ? '收起全部' : '展开全部' }}</el-button>
      </div>
      <el-tree
        ref="permTreeRef"
        :data="permTree"
        show-checkbox
        node-key="name"
        :default-checked-keys="currentPermKeys"
        :default-expanded-keys="defaultExpandedKeys"
        :props="{ children: 'children', label: 'label' }"
        highlight-current
      >
        <template #default="{ data }">
          <span class="perm-node">
            <el-icon :size="16" :color="data.children ? '#0C447C' : '#1D9E75'">
              <FolderOpened v-if="data.children" />
              <Check v-else />
            </el-icon>
            <span>{{ data.label }}</span>
          </span>
        </template>
      </el-tree>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPerm" @click="handlePermSave">保存权限</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit, Delete, Key, Avatar, FolderOpened, Check, Search, Refresh, Grid } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { get, post, put, del } from '@/utils/request'

const router = useRouter()
const goMatrix = () => router.push('/settings/role/matrix')

interface Role {
  id: number
  name: string
  description: string
  memberCount: number
  permCount: number
  color: string
  createTime: string
  permissionNames?: string[]
}

interface PermNode {
  id?: number
  name?: string
  label: string
  children?: PermNode[]
}

const roles = ref<Role[]>([])
const loading = ref(false)
const saving = ref(false)
const savingPerm = ref(false)
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const keyword = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

const permTree = ref<PermNode[]>([])
const defaultExpandedKeys = ref<string[]>([])

async function fetchRoles() {
  loading.value = true
  try {
    const res = await get('/roles', { keyword: keyword.value, page: page.value, per_page: perPage.value })
    // 后端 {code:0, data: {data: [...], total, per_page, ...}} 已经被解包为 data
    roles.value = res.data
    total.value = res.total
  } catch (e) {
    /* request.ts already toasted */
  } finally {
    loading.value = false
  }
}

async function fetchPermTree() {
  const res = await get('/permissions/tree')
  permTree.value = res
  // 默认展开所有模块
  defaultExpandedKeys.value = res.map(n => n.label)
}

function debouncedSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchRoles()
  }, 300)
}

onMounted(() => {
  fetchRoles()
  fetchPermTree()
})

// ========== 新增/编辑 ==========
const dialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const editingId = ref<number | null>(null)
const form = reactive({ name: '', description: '', color: '#0C447C', permissionNames: [] as string[] })
const formPermTreeRef = ref<any>(null)

function handleAdd() {
  editingId.value = null
  dialogTitle.value = '新增角色'
  Object.assign(form, { name: '', description: '', color: '#0C447C', permissionNames: [] })
  dialogVisible.value = true
}

function handleEdit(row: Role) {
  editingId.value = row.id
  dialogTitle.value = `编辑角色 - ${row.name}`
  // 取详情拿完整 permissions
  get(`/roles/${row.id}`).then((res) => {
    Object.assign(form, {
      name: res.name,
      description: res.description ?? '',
      color: res.color ?? '#0C447C',
      permissionNames: res.permissions ?? [],
    })
    dialogVisible.value = true
  })
}

async function handleDelete(row: Role) {
  try {
    await del(`/roles/${row.id}`)
    ElMessage.success(`角色「${row.name}」已删除`)
    fetchRoles()
  } catch (e) {
    /* request.ts already toasted */
  }
}

async function handleSave() {
  if (!form.name) {
    ElMessage.warning('请输入角色名称')
    return
  }
  // 收集选中的权限（叶子节点）
  const checkedNames = formPermTreeRef.value?.getCheckedNodes(false, true)?.map((n: PermNode) => n.name).filter(Boolean) as string[]
  const payload = {
    name: form.name,
    description: form.description,
    color: form.color,
    permissions: checkedNames ?? [],
  }
  saving.value = true
  try {
    if (editingId.value) {
      await put(`/roles/${editingId.value}`, payload)
      ElMessage.success('角色已更新')
    } else {
      await post('/roles', payload)
      ElMessage.success('角色已创建')
    }
    dialogVisible.value = false
    fetchRoles()
  } catch (e) {
    /* request.ts already toasted */
  } finally {
    saving.value = false
  }
}

// ========== 权限配置 ==========
const permDialogVisible = ref(false)
const currentRole = ref<Role | null>(null)
const currentPermKeys = ref<string[]>([])
const expandAll = ref(true)
const permTreeRef = ref<any>(null)

function toggleAllExpand() {
  expandAll.value = !expandAll.value
  const tree = permTreeRef.value
  if (!tree) return
  if (expandAll.value) {
    permTree.value.forEach(n => tree.store.nodesMap[n.label]?.expand())
  } else {
    permTree.value.forEach(n => tree.store.nodesMap[n.label]?.collapse())
  }
}

function handlePermission(row: Role) {
  currentRole.value = row
  // 拉最新权限
  get(`/roles/${row.id}`).then((res) => {
    currentPermKeys.value = res.permissions ?? []
    permDialogVisible.value = true
  })
}

async function handlePermSave() {
  if (!currentRole.value) return
  const checkedNodes = permTreeRef.value?.getCheckedNodes(false, true) ?? []
  const checkedNames = checkedNodes.map((n: PermNode) => n.name).filter(Boolean) as string[]
  savingPerm.value = true
  try {
    await post(`/roles/${currentRole.value.id}/permissions`, { permissions: checkedNames })
    ElMessage.success('权限配置已保存')
    permDialogVisible.value = false
    fetchRoles()
  } catch (e) {
    /* request.ts already toasted */
  } finally {
    savingPerm.value = false
  }
}
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }
}

.content-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.role-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.perm-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.perm-node {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}
</style>
