<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">审批流程引擎</span>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新建流程模板</el-button>
    </div>

    <div class="content-card">
      <div class="toolbar">
        <el-input v-model="searchKey" placeholder="搜索流程名称" clearable style="width: 280px;" :prefix-icon="Search" @input="page = 1" />
        <el-select v-model="filterModule" placeholder="适用模块" clearable style="width: 160px; margin-left: 12px;" @change="page = 1">
          <el-option label="全部" value="" />
          <el-option label="请假" value="请假" />
          <el-option label="报销" value="报销" />
          <el-option label="出差" value="出差" />
          <el-option label="采购" value="采购" />
          <el-option label="合同" value="合同" />
        </el-select>
        <el-button :icon="Refresh" @click="loadTemplates" style="margin-left: 12px;">刷新</el-button>
      </div>

      <el-table :data="pagedTemplates" border stripe style="width: 100%; margin-top: 16px;" v-loading="loading">
        <el-table-column prop="name" label="流程名称" width="200">
          <template #default="{ row }">
            <div class="flow-name">
              <el-icon color="#0C447C" :size="18"><Share /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="适用模块" width="120">
          <template #default="{ row }">
            <el-tag :type="moduleTagType(row.module)" size="small">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nodeCount" label="节点数" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '启用' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedBy" label="最后修改人" width="120" />
        <el-table-column prop="updatedAt" label="修改时间" width="170" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :icon="View" @click="handlePreview(row)">预览</el-button>
            <el-button link type="primary" size="small" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="warning" size="small" :icon="SwitchButton" @click="handleToggle(row)">
              {{ row.status === '启用' ? '停用' : '启用' }}
            </el-button>
            <el-popconfirm :title="`确定删除「${row.name}」？`" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger" size="small" :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 流程设计器说明 -->
    <div class="flow-designer-card">
      <div class="flow-designer-header">
        <span class="card-title">可视化流程设计器</span>
        <el-tag type="warning" size="small">即将上线</el-tag>
      </div>
      <div class="flow-designer-placeholder">
        <el-icon :size="48" color="#c0c4cc"><Connection /></el-icon>
        <p class="placeholder-title">可视化拖拽流程设计器</p>
        <p class="placeholder-desc">
          支持拖拽式流程节点编排，包括：开始节点、审批节点、条件分支、并行会签、抄送通知、结束节点等。<br />
          敬请期待该功能上线，如需配置流程请联系系统管理员。
        </p>
      </div>
    </div>

    <!-- 流程预览 -->
    <el-dialog v-model="previewVisible" title="流程预览" width="1500px">
      <div class="flow-preview" v-if="previewFlow">
        <div class="flow-steps">
          <template v-for="(node, idx) in (previewFlow.nodes || [])" :key="idx">
            <div class="flow-node" :class="`flow-node--${node.type}`">
              <div class="flow-node__icon">
                <el-icon :size="20">
                  <CircleCheck v-if="node.type === 'start'" />
                  <User v-else-if="node.type === 'approval'" />
                  <Switch v-else-if="node.type === 'condition'" />
                  <Bell v-else-if="node.type === 'notify'" />
                  <CircleClose v-else />
                </el-icon>
              </div>
              <div class="flow-node__info">
                <span class="flow-node__name">{{ node.name }}</span>
                <span class="flow-node__desc">{{ node.desc }}</span>
              </div>
            </div>
            <div class="flow-arrow" v-if="idx < previewFlow.nodes.length - 1">
              <el-icon :size="20" color="#c0c4cc"><ArrowDown /></el-icon>
            </div>
          </template>
        </div>
      </div>
    </el-dialog>

    <!-- 新建/编辑流程模板 -->
    <el-dialog v-model="formVisible" :title="editingId ? '编辑流程模板' : '新建流程模板'" width="1500px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="流程名称" required>
          <el-input v-model="form.name" placeholder="请输入流程名称" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="适用模块" required>
          <el-select v-model="form.module" placeholder="请选择" style="width:100%">
            <el-option label="请假" value="请假" />
            <el-option label="报销" value="报销" />
            <el-option label="出差" value="出差" />
            <el-option label="采购" value="采购" />
            <el-option label="合同" value="合同" />
          </el-select>
        </el-form-item>
        <el-form-item label="流程描述">
          <el-input v-model="form.description" type="textarea" :rows="2" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="启用">启用</el-radio>
            <el-radio label="停用">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="流程节点">
          <div class="nodes-editor">
            <div v-for="(n, i) in form.nodes" :key="i" class="node-row">
              <el-select v-model="n.type" style="width:120px" size="small">
                <el-option label="开始" value="start" />
                <el-option label="审批" value="approval" />
                <el-option label="条件" value="condition" />
                <el-option label="抄送" value="notify" />
                <el-option label="结束" value="end" />
              </el-select>
              <el-input v-model="n.name" placeholder="节点名称" size="small" style="width:160px" />
              <el-input v-model="n.desc" placeholder="说明" size="small" style="flex:1;min-width:100px" />
              <el-button :icon="Delete" size="small" link type="danger" @click="removeNode(i)" />
            </div>
            <el-button :icon="Plus" size="small" type="primary" link @click="addNode" style="margin-top:8px">
              添加节点
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Search, Share, View, Edit, Delete, SwitchButton, Connection, CircleCheck, User, Switch, Bell, CircleClose, ArrowDown, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { get, post, put, del } from '@/utils/request'

interface FlowNode {
  name: string
  desc: string
  type: 'start' | 'approval' | 'condition' | 'notify' | 'end'
}

interface FlowTemplate {
  id: number
  name: string
  module: string
  description?: string
  nodeCount: number
  status: '启用' | '停用'
  updatedBy: string
  updatedAt: string
  nodes?: FlowNode[]
}

const searchKey = ref('')
const filterModule = ref('')
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const saving = ref(false)
const templates = ref<FlowTemplate[]>([])

const filteredTemplates = computed(() => {
  let list = templates.value
  if (searchKey.value) {
    const kw = searchKey.value.toLowerCase()
    list = list.filter(t => t.name.toLowerCase().includes(kw))
  }
  if (filterModule.value) {
    list = list.filter(t => t.module === filterModule.value)
  }
  return list
})

const pagedTemplates = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredTemplates.value.slice(start, start + pageSize.value)
})

function moduleTagType(module: string) {
  const map: Record<string, string> = { '请假': 'warning', '报销': 'danger', '出差': 'info', '采购': 'primary', '合同': 'success' }
  return map[module] || 'info'
}

async function loadTemplates() {
  loading.value = true
  try {
    const res: any = await get('/approval-templates')
    // request.ts 解包后是 array
    if (Array.isArray(res)) {
      templates.value = res
    } else if (res?.code === 0 && res.data) {
      templates.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载流程模板失败')
  } finally {
    loading.value = false
  }
}

// 预览
const previewVisible = ref(false)
const previewFlow = ref<FlowTemplate | null>(null)
function handlePreview(row: FlowTemplate) {
  previewFlow.value = row
  previewVisible.value = true
}

// 新建/编辑
const formVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<{ name: string; module: string; description: string; status: '启用' | '停用'; nodes: FlowNode[] }>({
  name: '', module: '请假', description: '', status: '启用', nodes: [],
})
function handleAdd() {
  editingId.value = null
  Object.assign(form, {
    name: '', module: '请假', description: '', status: '启用',
    nodes: [
      { name: '发起申请', desc: '员工提交申请', type: 'start' },
      { name: '部门经理审批', desc: '部门经理审核', type: 'approval' },
      { name: '流程结束', desc: '流程结束', type: 'end' },
    ],
  })
  formVisible.value = true
}

function handleEdit(row: FlowTemplate) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    module: row.module,
    description: row.description ?? '',
    status: row.status,
    nodes: (row.nodes && row.nodes.length) ? row.nodes.map(n => ({ ...n })) : [],
  })
  formVisible.value = true
}

function addNode() {
  form.nodes.push({ name: '新节点', desc: '', type: 'approval' })
}
function removeNode(i: number) {
  if (form.nodes.length <= 2) {
    ElMessage.warning('至少保留 2 个节点（开始 + 结束）')
    return
  }
  form.nodes.splice(i, 1)
}

async function handleSave() {
  if (!form.name) {
    ElMessage.warning('请输入流程名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name,
      module: form.module,
      description: form.description,
      status: form.status,
      nodes: form.nodes,
    }
    if (editingId.value) {
      await put(`/approval-templates/${editingId.value}`, payload)
      ElMessage.success('流程模板已更新')
    } else {
      await post('/approval-templates', payload)
      ElMessage.success('流程模板已创建')
    }
    formVisible.value = false
    loadTemplates()
  } catch (e: any) {
    /* request.ts 已 toast */
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: FlowTemplate) {
  try {
    await del(`/approval-templates/${row.id}`)
    ElMessage.success(`流程「${row.name}」已删除`)
    loadTemplates()
  } catch (e) { /* handled */ }
}

async function handleToggle(row: FlowTemplate) {
  try {
    const res: any = await post(`/approval-templates/${row.id}/toggle`, {})
    if (res?.code === 0) {
      row.status = res.data?.status ?? (row.status === '启用' ? '停用' : '启用')
      ElMessage.success(`流程已${row.status}`)
    }
  } catch (e) { /* handled */ }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
  .page-title { font-size: 20px; font-weight: 600; color: #303133; }
}
.content-card {
  background: #fff; border-radius: 8px; padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06); margin-bottom: 20px;
}
.toolbar { display: flex; align-items: center; }
.flow-name { display: flex; align-items: center; gap: 8px; font-weight: 500; }

.flow-designer-card {
  background: #fff; border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06); overflow: hidden;
}
.flow-designer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 20px 0;
  .card-title { font-size: 16px; font-weight: 600; color: #303133; }
}
.flow-designer-placeholder { text-align: center; padding: 48px 20px;
  .placeholder-title { font-size: 18px; font-weight: 600; color: #909399; margin-top: 16px; }
  .placeholder-desc { font-size: 13px; color: #c0c4cc; margin-top: 12px; line-height: 1.8; max-width: 500px; margin-left: auto; margin-right: auto; }
}

.flow-preview { padding: 20px;
  .flow-steps { display: flex; flex-direction: column; align-items: center; gap: 0; }
  .flow-node { display: flex; align-items: center; gap: 16px; padding: 16px 24px; border: 1px solid #e4e7ed; border-radius: 8px; width: 320px; background: #fff;
    &--start    { border-left: 4px solid #1D9E75; }
    &--approval { border-left: 4px solid #0C447C; }
    &--condition{ border-left: 4px solid #BA7517; }
    &--notify   { border-left: 4px solid #534AB7; }
    &--end      { border-left: 4px solid #A32D2D; }
    &__icon { flex-shrink: 0; }
    &__info { display: flex; flex-direction: column; }
    &__name { font-size: 14px; font-weight: 600; color: #303133; }
    &__desc { font-size: 12px; color: #909399; margin-top: 2px; }
  }
  .flow-arrow { padding: 4px 0; }
}

.nodes-editor { width: 100%; }
.node-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
</style>
