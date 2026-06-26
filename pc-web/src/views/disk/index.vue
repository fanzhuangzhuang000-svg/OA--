<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title-wrap">
        <span class="page-title">公司网盘</span>
        <span class="page-desc">项目文档、日常资料、技术资料统一管理</span>
      </div>
      <div>
        <el-button @click="refreshAll"><el-icon><Refresh /></el-icon>刷新</el-button>
        <el-button type="primary" :disabled="!currentFolder || currentFolder.id === 0" @click="triggerUpload">
          <el-icon><Upload /></el-icon>上传文件
        </el-button>
        <el-button type="success" @click="showFolderDialog = true">
          <el-icon><FolderAdd /></el-icon>新建文件夹
        </el-button>
        <input ref="fileInput" type="file" multiple style="display:none" @change="handleFileSelected" />
      </div>
    </div>

    <div class="disk-body">
      <!-- 左侧文件夹树 -->
      <div class="disk-side">
        <div class="disk-side__head">
          <span>文件夹</span>
          <el-tooltip content="新建文件夹" placement="top">
            <el-icon class="disk-side__add" @click="showFolderDialog = true"><Plus /></el-icon>
          </el-tooltip>
        </div>
        <div class="disk-side__tree">
          <div class="tree-node tree-node--root" :class="{ active: !currentFolder }" @click="goHome">
            <el-icon><HomeFilled /></el-icon>
            <span>全部文件</span>
          </div>
          <el-tree
            ref="treeRef"
            :data="folderTree"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            highlight-current
            :expand-on-click-node="false"
            :default-expand-all="false"
            @node-click="handleTreeClick"
            empty-text="暂无文件夹"
          >
            <template #default="{ node, data }">
              <span class="tree-node tree-node--custom" :class="{ active: currentFolder?.id === data.id }">
                <el-icon><Folder /></el-icon>
                <span class="tree-node__name">{{ data.name }}</span>
                <el-tag v-if="data.system_type" size="small" :type="systemTag(data.system_type)" effect="plain" class="tree-node__tag">
                  {{ systemLabel(data.system_type) }}
                </el-tag>
                <el-dropdown trigger="click" @click.stop @command="(c) => onTreeAction(c, data)">
                  <el-icon class="tree-node__more" @click.stop><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="rename">重命名</el-dropdown-item>
                      <el-dropdown-item command="delete" :disabled="!!data.system_type" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </span>
            </template>
          </el-tree>
        </div>
        <!-- 系统文件夹说明 -->
        <div class="disk-side__hint">
          <el-icon><InfoFilled /></el-icon>
          <div>
            <div>📁 <b>project</b> - 每个新建项目自动生成子文件夹</div>
            <div>📁 <b>work</b> - 存放日常工作文档</div>
          </div>
        </div>
      </div>

      <!-- 右侧文件区 -->
      <div class="disk-main">
        <div class="disk-toolbar">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item><a @click="goHome" style="cursor:pointer;color:#0C447C">全部文件</a></el-breadcrumb-item>
            <el-breadcrumb-item v-for="f in breadcrumb" :key="f.id"><a @click="goToFolder(f)" style="cursor:pointer">{{ f.name }}</a></el-breadcrumb-item>
          </el-breadcrumb>
          <el-input v-model="keyword" placeholder="搜索文件..." clearable style="width:240px" @clear="loadData" @keyup.enter="loadData">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div class="content-card">
          <el-table :data="tableData" v-loading="loading" stripe style="width:100%">
            <el-table-column type="selection" width="40" />
            <el-table-column label="文件名" min-width="320" sortable>
              <template #default="{ row }">
                <div class="file-name" :class="{ 'is-folder': row.type==='folder' }" @click="row.type==='folder' && goToFolder(row)">
                  <el-icon :size="22" :color="row.type==='folder' ? '#BA7517' : fileColor(row.extension)">
                    <Folder v-if="row.type==='folder'" />
                    <Document v-else-if="['doc','docx'].includes(row.extension)" />
                    <Document v-else-if="['xls','xlsx'].includes(row.extension)" />
                    <Picture v-else-if="['jpg','png','gif','bmp','webp'].includes(row.extension)" />
                    <VideoCamera v-else-if="['mp4','avi','mov','mkv'].includes(row.extension)" />
                    <Headset v-else-if="['mp3','wav','flac'].includes(row.extension)" />
                    <Files v-else-if="['zip','rar','7z','tar','gz'].includes(row.extension)" />
                    <Document v-else />
                  </el-icon>
                  <span class="file-name__text">{{ row.name }}</span>
                  <el-tag v-if="row.type==='folder' && row.system_type" size="small" :type="systemTag(row.system_type)" effect="plain" round>
                    {{ systemLabel(row.system_type) }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="大小" width="120" align="right">
              <template #default="{ row }">
                <span v-if="row.type==='folder'">{{ row.files_count ?? '-' }} 项</span>
                <span v-else>{{ formatSize(row.size) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="上传者" width="100">
              <template #default="{ row }">{{ row.uploader_name || row.creator_name || '-' }}</template>
            </el-table-column>
            <el-table-column label="修改时间" width="160">
              <template #default="{ row }">{{ formatTime(row.updated_at || row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button v-if="row.type!=='folder'" text type="primary" size="small" @click="handleDownload(row)">下载</el-button>
                <el-button text type="primary" size="small" @click="handleRename(row)">重命名</el-button>
                <el-button text type="danger" size="small" :disabled="row.type==='folder' && !!row.system_type" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && tableData.length===0" :description="currentFolder ? '该文件夹为空，点击右上角上传文件' : '请在左侧选择文件夹'" />
        </div>
      </div>
    </div>

    <!-- 新建文件夹对话框 -->
    <FolderDialog
      v-model:visible="showFolderDialog"
      :title="`新建文件夹${currentFolder ? '（在 ' + currentFolder.name + ' 下）' : ''}`"
      v-model:name="newFolderName"
      :creating="creating"
      @confirm="handleCreateFolder"
    />

    <!-- 重命名对话框 -->
    <RenameDialog
      v-model:visible="showRenameDialog"
      v-model:value="renameValue"
      @confirm="confirmRename"
    />

    <!-- 上传进度 -->
    <UploadProgressDialog
      v-model:visible="showUploading"
      :queue="uploadQueue"
      @close="showUploading=false;uploadQueue=[]"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, FolderAdd, Folder, Document, Picture, VideoCamera, Headset, Files,
  Search, Refresh, HomeFilled, Plus, InfoFilled, MoreFilled
} from '@element-plus/icons-vue'
import { get, post, put, del } from '@/utils/request'
import FolderDialog from './components/FolderDialog.vue'
import RenameDialog from './components/RenameDialog.vue'
import UploadProgressDialog from './components/UploadProgressDialog.vue'

const fileInput = ref<HTMLInputElement>()
const treeRef = ref()
const loading = ref(false)
const keyword = ref('')

// 当前选中文件夹
const currentFolder = ref<any>(null)
const breadcrumb = ref<any[]>([])
const tableData = ref<any[]>([])

// 整棵文件夹树
const folderTree = ref<any[]>([])

// 新建文件夹
const showFolderDialog = ref(false)
const newFolderName = ref('')
const creating = ref(false)

// 重命名
const showRenameDialog = ref(false)
const renameValue = ref('')
const renameTarget = ref<any>(null)

// 上传
const showUploading = ref(false)
const uploadQueue = ref<any[]>([])

function fileColor(ext: string) {
  const m: any = { pdf: '#A32D2D', doc: '#185FA5', docx: '#185FA5', xls: '#1D9E75', xlsx: '#1D9E75', jpg: '#D85A30', png: '#D85A30', gif: '#D85A30', mp4: '#534AB7', zip: '#909399' }
  return m[ext?.toLowerCase()] || '#909399'
}

function formatSize(bytes: number): string {
  if (!bytes && bytes !== 0) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
  if (bytes < 1024*1024*1024) return (bytes/1024/1024).toFixed(1) + ' MB'
  return (bytes/1024/1024/1024).toFixed(2) + ' GB'
}

function formatTime(s?: string) {
  if (!s) return '-'
  return s.slice(0, 16).replace('T', ' ')
}

// 系统文件夹类型
const SYSTEM_LABELS: Record<string, { label: string; type: string }> = {
  project_root: { label: '项目', type: 'primary' },
  work: { label: '工作', type: 'success' },
  project_doc: { label: '项目文档', type: 'warning' },
}
function systemLabel(t: string) { return SYSTEM_LABELS[t]?.label || t }
function systemTag(t: string): any { return SYSTEM_LABELS[t]?.type || 'info' }

async function loadTree() {
  try {
    const res: any = await get('/disk/folders')
    folderTree.value = (res.data || res || []) as any[]
  } catch (e) {
    folderTree.value = []
  }
}

async function loadData() {
  loading.value = true
  try {
    const [folRes, fileRes] = await Promise.all([
      get<any>('/disk/folders', { parent_id: currentFolder.value?.id ?? null }),
      get<any>('/disk/files', {
        folder_id: currentFolder.value?.id ?? null,
        ...(keyword.value ? { keyword: keyword.value } : {})
      })
    ])
    const folders = ((folRes.data || folRes || []) as any[]).map((f: any) => ({ ...f, type: 'folder' }))
    const filesRaw = fileRes.data?.data?.items || fileRes.data?.data || fileRes.data || []
    const files = (Array.isArray(filesRaw) ? filesRaw : []).map((f: any) => ({ ...f, type: 'file' }))
    tableData.value = [...folders, ...files]
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function handleTreeClick(data: any) {
  if (data.is_system) {
    // 系统根文件夹，可点击进入
  }
  currentFolder.value = data
  breadcrumb.value = buildBreadcrumb(data)
  loadData()
}

function buildBreadcrumb(target: any): any[] {
  const map = new Map<number, any>()
  function collect(nodes: any[]) {
    for (const n of nodes) {
      map.set(n.id, n)
      if (n.children?.length) collect(n.children)
    }
  }
  collect(folderTree.value)
  const path: any[] = []
  let cur = map.get(target.id)
  while (cur && cur.parent_id) {
    const p = map.get(cur.parent_id)
    if (p) { path.unshift(p); cur = p } else break
  }
  return path
}

function goToFolder(row: any) {
  if (row.type !== 'folder') return
  currentFolder.value = row
  breadcrumb.value = buildBreadcrumb(row)
  loadData()
  // 同步展开树
  treeRef.value?.setCurrentKey(row.id)
}

function goHome() {
  currentFolder.value = null
  breadcrumb.value = []
  loadData()
  treeRef.value?.setCurrentKey(null)
}

function refreshAll() {
  loadTree()
  loadData()
}

async function handleCreateFolder() {
  if (!newFolderName.value.trim()) { ElMessage.warning('请输入文件夹名称'); return }
  creating.value = true
  try {
    await post<any>('/disk/folders', {
      name: newFolderName.value.trim(),
      parent_id: currentFolder.value?.id ?? null
    })
    ElMessage.success('文件夹创建成功')
    showFolderDialog.value = false
    newFolderName.value = ''
    await loadTree()
    await loadData()
  } catch (e: any) {
    ElMessage.error(e?.message || '创建失败')
  } finally {
    creating.value = false
  }
}

function handleRename(row: any) {
  renameTarget.value = row
  renameValue.value = row.name
  showRenameDialog.value = true
}

async function confirmRename() {
  if (!renameValue.value.trim()) { ElMessage.warning('名称不能为空'); return }
  try {
    if (renameTarget.value.type === 'folder') {
      await put(`/disk/folders/${renameTarget.value.id}`, { name: renameValue.value.trim() })
    } else {
      await put(`/disk/files/${renameTarget.value.id}`, { name: renameValue.value.trim() })
    }
    ElMessage.success('已重命名')
    showRenameDialog.value = false
    refreshAll()
  } catch (e: any) {
    ElMessage.error(e?.message || '重命名失败')
  }
}

function triggerUpload() { fileInput.value?.click() }

async function handleFileSelected(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files || files.length === 0) return
  if (!currentFolder.value) {
    ElMessage.warning('请先在左侧选择目标文件夹')
    return
  }
  showUploading.value = true
  for (const file of Array.from(files)) {
    const item: any = { name: file.name, progress: 0, status: 'uploading' }
    uploadQueue.value.push(item)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('folder_id', String(currentFolder.value.id))
      const res: any = await post<any>('/disk/upload', fd)
      if (res && (res.id || res.file_id || res.success)) {
        item.status = 'done'; item.progress = 100
      } else {
        item.status = 'error'; item.error = res?.message || '上传失败'
      }
    } catch (e: any) {
      item.status = 'error'; item.error = e?.response?.data?.message || e?.message || '上传失败'
    }
  }
  await loadData()
  // 清空 input 允许同名文件再选
  if (fileInput.value) fileInput.value.value = ''
}

async function handleDownload(row: any) {
  ElMessage.info('下载功能：' + row.original_name || row.name)
}

async function handleDelete(row: any) {
  if (row.type === 'folder' && row.system_type) {
    ElMessage.warning('系统文件夹不可删除')
    return
  }
  try {
    await ElMessageBox.confirm(`确认删除「${row.name}」？${row.type === 'folder' ? '文件夹内所有内容也会被删除' : ''}`, '删除确认', { type: 'warning' })
  } catch { return }
  try {
    if (row.type === 'folder') {
      await del(`/disk/folders/${row.id}`)
    } else {
      await del(`/disk/files/${row.id}`)
    }
    ElMessage.success('已删除')
    refreshAll()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function onTreeAction(cmd: string, data: any) {
  if (cmd === 'rename') handleRename(data)
  if (cmd === 'delete') handleDelete(data)
}

onMounted(() => { loadTree() })
</script>

<style lang="scss" scoped>
$primary: #0C447C;
$success: #1D9E75;
$warning: #BA7517;
$danger: #A32D2D;

.page-container { padding: 20px; background: linear-gradient(180deg, #f0f4fa 0%, #f5f7fa 100%); min-height: 100vh; }

.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding:18px 20px; background:#fff; border-radius:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);
  .page-title-wrap { display: flex; align-items: baseline; gap: 12px; }
  .page-title { font-size:20px; color:$primary; font-weight:600; }
  .page-desc { font-size:13px; color:#6b7280; }
}

.disk-body { display:grid; grid-template-columns: 260px 1fr; gap:16px; min-height: 600px; }

.disk-side { background:#fff; border-radius:12px; padding:16px; box-shadow:0 1px 4px rgba(0,0,0,0.04); display:flex; flex-direction:column;
  &__head { display:flex; justify-content:space-between; align-items:center; font-size:14px; font-weight:600; color:#374151; padding-bottom:12px; border-bottom:1px solid #f0f0f0; }
  &__add { cursor:pointer; padding:4px; border-radius:4px; transition:background .2s; &:hover { background:#f0f4fa; color:$primary; } }
  &__tree { flex:1; margin-top:8px; overflow:auto; }
  &__hint { padding:10px 12px; background:#f9fafb; border-radius:6px; font-size:12px; color:#6b7280; line-height:1.8; display:flex; gap:6px;
    :deep(.el-icon) { margin-top:2px; color:$warning; }
  }
}

.tree-node { display:flex; align-items:center; gap:6px; padding:4px 6px; border-radius:4px; cursor:pointer; font-size:13px; transition: background .2s; width:100%;
  &--root { font-weight:500; color:#374151; padding:8px 10px; }
  &--custom { color:#374151; }
  &.active { background:#e6f0fa !important; color:$primary; font-weight:600; }
  &:hover { background:#f5f7fa; }
  &__name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  &__tag { flex-shrink:0; }
  &__more { padding:2px; border-radius:3px; color:#9ca3af; opacity:0; transition: opacity .2s; .tree-node:hover & { opacity:1; } &:hover { background:#e5e7eb; color:$primary; } }
}

.disk-main { display:flex; flex-direction:column; gap:12px; }
.disk-toolbar { display:flex; justify-content:space-between; align-items:center; padding:12px 20px; background:#fff; border-radius:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.content-card { background:#fff; border-radius:12px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,0.04); flex:1; }

.file-name { display:flex; align-items:center; gap:8px;
  &__text { color:#1f2937; }
  &.is-folder { cursor:pointer; .file-name__text { color:$primary; font-weight:500; } }
  &.is-folder:hover .file-name__text { text-decoration:underline; }
}

:deep(.el-tree-node__content) { height: 32px; }
:deep(.el-tree-node__content:hover) { background: transparent; }
:deep(.el-tree-node.is-current > .el-tree-node__content) { background: transparent; }
</style>
