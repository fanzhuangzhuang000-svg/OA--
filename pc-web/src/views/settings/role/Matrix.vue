<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">权限矩阵</span>
      <div class="header-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>勾选 / 取消勾选会立即保存到「
          <el-tag v-if="editingRole" :color="editingRole.color" effect="dark" size="small">
            {{ editingRole.name }}
          </el-tag>
          <span v-else class="text-muted">未选角色</span>
        」并按继承链自动同步</span>
      </div>
    </div>

    <div class="content-card">
      <!-- 角色切换 tab -->
      <el-tabs v-model="activeRole" @tab-change="onRoleChange" type="card" class="role-tabs">
        <el-tab-pane
          v-for="r in matrix.roles"
          :key="r.name"
          :name="r.name"
        >
          <template #label>
            <el-tag :color="r.color" effect="dark" size="small" style="margin-right: 6px;">
              {{ r.name }}
            </el-tag>
            <span class="tab-desc">{{ r.description }}</span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <!-- 继承链提示 -->
      <el-alert
        v-if="inheritanceHint"
        :title="inheritanceHint"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />

      <!-- 权限树 -->
      <div v-loading="loading" class="matrix-container">
        <el-table
          :data="permissionRows"
          border
          stripe
          height="600"
          :row-key="(row: any) => row.name"
          style="width: 100%"
        >
          <el-table-column label="模块" prop="module" width="160" fixed>
            <template #default="{ row }">
              <el-tag effect="plain" size="small">{{ row.module }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="权限" prop="label" min-width="200">
            <template #default="{ row }">
              <div class="perm-name">
                <code>{{ row.name }}</code>
                <span class="perm-desc">{{ row.label }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-switch
                :model-value="hasPerm(row.name)"
                :loading="savingPerms.has(row.name)"
                :disabled="!editingRole"
                @change="(v: boolean) => togglePerm(row.name, v)"
              />
              <el-tag
                v-if="isInherited(row.name) && !hasOwn(row.name)"
                type="info"
                size="small"
                effect="plain"
                style="margin-left: 6px;"
              >继承</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 底部统计 -->
      <div class="matrix-footer">
        <div>
          <el-statistic title="当前角色" :value="activeRole" />
        </div>
        <div>
          <el-statistic title="自有权限" :value="ownCount" />
        </div>
        <div>
          <el-statistic title="继承权限" :value="inheritedCount" />
        </div>
        <div>
          <el-statistic title="总有效权限" :value="totalCount" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { get, post } from '@/utils/request'

const loading = ref(false)
const savingPerms = ref(new Set<string>())

const matrix = ref<any>({
  roles: [],
  permissions: [],
  matrix: {} as Record<string, string[]>,
  inheritance: { nodes: [], edges: [] },
})
const activeRole = ref('')
const editingRole = computed(() => matrix.value.roles.find((r: any) => r.name === activeRole.value))

// 当前角色拥有的权限 (含继承, 直接看 roleHasPerms 自有)
const roleOwnPerms = computed(() => new Set(matrix.value.matrix[activeRole.value] || []))

// 所有父角色的权限 union (用于"继承"标记)
const inheritedPerms = computed(() => {
  const parents = [] as string[]
  function collect(nodeName: string) {
    matrix.value.inheritance.edges?.forEach((e: any) => {
      if (e.child === nodeName) {
        const ps = matrix.value.matrix[e.parent] || []
        parents.push(...ps)
        collect(e.parent)
      }
    })
  }
  collect(activeRole.value)
  return new Set(parents)
})

const hasOwn = (name: string) => roleOwnPerms.value.has(name)
const hasPerm = (name: string) => hasOwn(name) || inheritedPerms.value.has(name)
const isInherited = (name: string) => !hasOwn(name) && inheritedPerms.value.has(name)

// 权限按 module 分组 + 排序
const permissionRows = computed(() => {
  const all = matrix.value.permissions || []
  // 同 module 内按 name 排
  return [...all].sort((a: any, b: any) => {
    if (a.module !== b.module) return a.module.localeCompare(b.module, 'zh')
    return a.name.localeCompare(b.name)
  })
})

const ownCount = computed(() => roleOwnPerms.value.size)
const inheritedCount = computed(() => {
  let cnt = 0
  permissionRows.value.forEach((p: any) => {
    if (isInherited(p.name)) cnt++
  })
  return cnt
})
const totalCount = computed(() => ownCount.value + inheritedCount.value)

const inheritanceHint = computed(() => {
  const parents = [] as string[]
  matrix.value.inheritance.edges?.forEach((e: any) => {
    if (e.child === activeRole.value) parents.push(e.parent)
  })
  if (!parents.length) return null
  return `「${activeRole.value}」继承自 [${parents.join(', ')}], 父角色的权限自动可见 (但可单独开关)`
})

const fetchMatrix = async () => {
  loading.value = true
  try {
    const res: any = await get('/roles/matrix')
    const data = res.data || res
    matrix.value = data
    if (!activeRole.value && data.roles?.length) {
      activeRole.value = data.roles[0].name
    }
  } catch (e: any) {
    ElMessage.error('加载矩阵失败: ' + (e?.message || ''))
  } finally {
    loading.value = false
  }
}

const onRoleChange = (name: string) => {
  // tab 切换不重 fetch, 切换本地视图即可
}

const togglePerm = async (permName: string, enabled: boolean) => {
  if (!activeRole.value) return

  // 二次确认: 移除继承来的权限要小心
  if (!enabled && isInherited(permName)) {
    try {
      await ElMessageBox.confirm(
        `「${permName}」是从父角色继承来的。关闭后, 父角色保留此权限, 当前角色「${activeRole.value}」会失去该权限。继续?`,
        '移除继承权限',
        { type: 'warning', confirmButtonText: '确认移除', cancelButtonText: '取消' }
      )
    } catch {
      return
    }
  }

  savingPerms.value.add(permName)
  try {
    // 1) 拿到当前角色所有"应该有的"权限 (含继承)
    const currentAll = new Set<string>()
    permissionRows.value.forEach((p: any) => {
      if (hasPerm(p.name)) currentAll.add(p.name)
    })

    if (enabled) {
      currentAll.add(permName)
    } else {
      currentAll.delete(permName)
    }

    // 2) 计算"自有"权限: 去掉继承来的部分
    // 注: 后端 syncPermissions 直接覆盖, 所以我们只传"应保留的自有"
    // 如果当前开关 = true, 且原 = 继承来的, 那需要给当前角色加这个权限 (覆盖继承)
    const allPermNames = new Set(permissionRows.value.map((p: any) => p.name))
    const ownList: string[] = []
    const inheritedList: string[] = []
    currentAll.forEach(name => {
      // 用 inbuilt 继承 map 区分
      const isInh = !roleOwnPerms.value.has(name) && inheritedPerms.value.has(name)
      if (isInh) inheritedList.push(name)
      else ownList.push(name)
    })
    // 切到 enabled = true, 但原本是继承来的: 把它加到 ownList (覆盖继承, 角色自有)
    if (enabled && isInherited(permName)) {
      ownList.push(permName)
    }
    // 切到 enabled = false, 但原本是自有的: 保持 ownList 不含
    if (!enabled && hasOwn(permName)) {
      const idx = ownList.indexOf(permName)
      if (idx >= 0) ownList.splice(idx, 1)
    }

    // 3) 调接口
    await post(`/roles/${activeRole.value}/permissions`, { permissions: ownList })
    // 4) 重新拉矩阵 (会重新算继承)
    await fetchMatrix()
    ElMessage.success(enabled ? `已开启 ${permName}` : `已关闭 ${permName}`)
  } catch (e: any) {
    if (e?.message?.includes('取消')) return
    ElMessage.error('保存失败: ' + (e?.message || '未知错误'))
    await fetchMatrix() // 回滚 UI
  } finally {
    savingPerms.value.delete(permName)
  }
}

onMounted(() => {
  fetchMatrix()
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
.header-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}
.text-muted { color: #c0c4cc; }
.content-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.role-tabs { margin-bottom: 16px; }
.tab-desc { color: #909399; font-size: 12px; margin-left: 4px; }
.matrix-container { margin-top: 8px; }
.perm-name { display: flex; flex-direction: column; gap: 2px; }
.perm-name code {
  font-size: 12px;
  color: #409eff;
  background: #ecf5ff;
  padding: 2px 6px;
  border-radius: 3px;
  align-self: flex-start;
}
.perm-desc { font-size: 12px; color: #606266; }
.matrix-footer {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
