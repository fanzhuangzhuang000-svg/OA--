<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-title-wrap">
        <span class="page-title">知识库</span>
        <span class="page-desc">安防行业经验沉淀，让知识成为企业资产</span>
      </div>
      <el-button type="primary" @click="openPublishDialog()"><el-icon><Edit /></el-icon>发布文章</el-button>
    </div>
    <el-row :gutter="16">
      <el-col :span="5">
        <el-card shadow="never" class="category-tree" v-loading="catLoading">
          <template #header>
            <div class="cat-head">
              <span>知识分类</span>
              <el-dropdown trigger="click" @command="onCategoryAction">
                <el-button type="primary" link size="small">
                  <el-icon><Plus /></el-icon>新增分类
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="root">新建顶级分类</el-dropdown-item>
                    <el-dropdown-item command="sub" :disabled="!currentCategory">在「{{ currentCategory?.name }}」下新建子分类</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <div class="cat-all" :class="{ active: !currentCategoryId }" @click="filterByCategory(null)">
            <el-icon><Files /></el-icon> 全部 ({{ totalCount }})
          </div>
          <el-tree
            ref="treeRef"
            :data="categories"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            highlight-current
            :expand-on-click-node="false"
            @node-click="(d) => filterByCategory(d.id)"
            empty-text="暂无分类，点击右上角新增"
          >
            <template #default="{ node, data }">
              <span class="cat-node" :class="{ active: currentCategoryId === data.id }">
                <el-icon><Folder /></el-icon>
                <span class="cat-node__name">{{ data.name }}</span>
                <el-tag v-if="data.articles_count" size="small" effect="plain" type="info">{{ data.articles_count }}</el-tag>
                <el-dropdown trigger="click" @click.stop @command="(c) => onNodeAction(c, data)">
                  <el-icon class="cat-node__more" @click.stop><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="addSub">新建子分类</el-dropdown-item>
                      <el-dropdown-item command="rename">重命名</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除分类</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>
      <el-col :span="19">
        <ArticleList
          v-model:keyword="keyword"
          :articles="articles"
          :loading="loading"
          :total="total"
          :page="page"
          :page-size="pageSize"
          :current-category="currentCategory"
          @search="() => { page = 1; loadArticles() }"
          @clear-category="filterByCategory(null)"
          @open="openArticle"
          @edit="openPublishDialog"
          @delete="handleDelete"
          @page-change="(p: number) => { page = p; loadArticles() }"
          @size-change="(s: number) => { pageSize = s; page = 1; loadArticles() }"
        />
      </el-col>
    </el-row>

    <!-- 发布/编辑 对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑文章' : '发布文章'"
      width="720px"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" v-loading="saving">
        <el-form-item label="文章标题" required>
          <el-input v-model="form.title" placeholder="请输入文章标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="所属分类" required>
          <el-cascader
            v-model="form.categoryPath"
            :options="categories"
            :props="{ checkStrictly: true, value: 'id', label: 'name', children: 'children', emitPath: false }"
            placeholder="请选择分类"
            style="width: 100%"
          />
          <div style="margin-top: 6px; font-size: 12px; color: #909399">
            没有合适的分类？<el-button type="primary" link size="small" @click="openCategoryDialogFromArticle">点此创建</el-button>
          </div>
        </el-form-item>
        <el-form-item label="文章摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" maxlength="500" show-word-limit placeholder="可选，留空则自动取正文前 120 字" />
        </el-form-item>
        <el-form-item label="文章类型">
          <el-radio-group v-model="form.content_type">
            <el-radio label="text">纯文本</el-radio>
            <el-radio label="file">上传文件（PDF/Word/Excel/PPT/图片）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.content_type === 'text'" label="正文内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文章正文（支持换行）"
            maxlength="20000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item v-else label="文件上传" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :on-remove="handleFileRemove"
            :file-list="form.fileList"
            v-bind:accept="acceptTypes"
            drag
          >
            <div v-if="!form.fileList.length" class="upload-trigger">
              <el-icon class="upload-trigger__icon"><UploadFilled /></el-icon>
              <div class="upload-trigger__text">点击或拖拽文件到此处上传</div>
              <div class="upload-trigger__hint">支持 PDF / Word / Excel / PPT / 图片 / TXT，单文件 ≤ 50MB</div>
            </div>
            <template #tip>
              <div class="upload-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>已选文件：<b>{{ form.fileList[0]?.name || '无' }}</b>
                  <span v-if="form.fileList[0]">（{{ formatSize(form.fileList[0].size) }}）</span>
                </span>
                <el-tag v-if="form.fileList[0]" size="small" type="info" effect="plain">发布后用户可下载查看</el-tag>
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="published">立即发布</el-radio>
            <el-radio label="draft">存为草稿</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handlePublish">{{ editingId ? '保存' : '发布' }}</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理对话框（新增/重命名） -->
    <CategoryFormDialog
      v-model:visible="categoryDialogVisible"
      :title="categoryDialogMode === 'addSub' ? `在「${categoryDialogParent?.name}」下新建子分类` :
               categoryDialogMode === 'addRoot' ? '新建顶级分类' : '重命名分类'"
      v-model:name="categoryDialogName"
      v-model:icon="categoryDialogIcon"
      :show-icon-field="categoryDialogMode !== 'rename'"
      :saving="categoryDialogSaving"
      @confirm="confirmCategoryDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Edit, Search, View, User, Calendar, Files, Folder, Plus, MoreFilled, UploadFilled, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { get, post, put, del } from '@/utils/request'
import CategoryFormDialog from './components/CategoryFormDialog.vue'

interface Article {
  id: number
  title: string
  summary?: string
  content: string
  status: 'published' | 'draft' | 'archived'
  category_id: number
  category?: { id: number; name: string }
  author?: { id: number; name: string }
  published_at?: string
  created_at?: string
  view_count?: number
}

interface Category {
  id: number
  name: string
  parent_id?: number | null
  icon?: string
  children?: Category[]
  articles_count?: number
}

const keyword = ref('')
const currentCategoryId = ref<number | null>(null)
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)
const loading = ref(false)
const catLoading = ref(false)
const saving = ref(false)
const articles = ref<Article[]>([])
const categories = ref<Category[]>([])
const treeRef = ref()

const totalCount = computed(() => total.value)
const currentCategory = computed(() => {
  function find(nodes: Category[]): Category | null {
    for (const n of nodes) {
      if (n.id === currentCategoryId.value) return n
      if (n.children) { const r = find(n.children); if (r) return r }
    }
    return null
  }
  return find(categories.value)
})

async function loadCategories() {
  catLoading.value = true
  try {
    const res: any = await get('/knowledge/categories')
    if (Array.isArray(res)) categories.value = res
    else if (res && Array.isArray(res.data)) categories.value = res.data
    else categories.value = []
  } catch (e) {
    console.error('加载分类失败', e)
    categories.value = []
  } finally {
    catLoading.value = false
  }
}

async function loadArticles() {
  loading.value = true
  try {
    const params: any = { page: page.value, per_page: pageSize.value }
    if (currentCategoryId.value) params.category_id = currentCategoryId.value
    if (keyword.value) params.keyword = keyword.value
    const res: any = await get('/knowledge/articles', params)
    if (Array.isArray(res)) { articles.value = res; total.value = res.length }
    else if (res && Array.isArray(res.data)) { articles.value = res.data; total.value = res.total || 0 }
    else { articles.value = []; total.value = 0 }
  } catch (e) {
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

function filterByCategory(id: number | null) {
  currentCategoryId.value = id
  page.value = 1
  if (id !== null) treeRef.value?.setCurrentKey(id)
  loadArticles()
}

function openArticle(item: Article) {
  ElMessageBox.alert(item.content || '(无内容)', item.title, { dangerouslyUseHTMLString: false, confirmButtonText: '关闭' })
}

// 发布/编辑对话框
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const uploadRef = ref()
const form = reactive({
  title: '',
  content: '',
  summary: '',
  categoryPath: null as number | null,
  status: 'published' as 'published' | 'draft',
  content_type: 'text' as 'text' | 'file',
  fileList: [] as any[],
})

// 支持的扩展名
const ALLOWED_EXTS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'jpg', 'jpeg', 'png', 'gif']
const acceptTypes = ALLOWED_EXTS.map(e => `.${e}`).join(',')
const MAX_SIZE = 50 * 1024 * 1024 // 50MB

function formatSize(bytes: number) {
  if (!bytes && bytes !== 0) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB'
  return (bytes/1024/1024).toFixed(1) + ' MB'
}

function handleFileChange(file: any) {
  const ext = (file.name.split('.').pop() || '').toLowerCase()
  if (!ALLOWED_EXTS.includes(ext)) {
    ElMessage.error(`不支持的文件格式：.${ext}，仅支持 PDF / Word / Excel / PPT / 图片 / TXT / MD`)
    file.status = 'fail'
    return false
  }
  if (file.size > MAX_SIZE) {
    ElMessage.error(`文件「${file.name}」超过 50MB 限制`)
    file.status = 'fail'
    return false
  }
  form.fileList = [file]
  // 自动用文件名作为标题（如果标题为空）
  if (!form.title.trim() && form.content_type === 'file') {
    form.title = file.name.replace(/\.[^.]+$/, '')
  }
  return true
}

function handleExceed() {
  ElMessage.warning('只能上传 1 个文件，请先移除已选文件')
}

function handleFileRemove() {
  form.fileList = []
}

function openPublishDialog(item?: Article) {
  if (item) {
    editingId.value = item.id
    Object.assign(form, {
      title: item.title, content: item.content, summary: item.summary || '',
      categoryPath: item.category_id,
      status: item.status === 'draft' ? 'draft' : 'published',
      content_type: 'text',
      fileList: [],
    })
  } else {
    editingId.value = null
    Object.assign(form, {
      title: '', content: '', summary: '',
      categoryPath: currentCategoryId.value || categories.value[0]?.id || null,
      status: 'published',
      content_type: 'text',
      fileList: [],
    })
  }
  dialogVisible.value = true
}

async function handlePublish() {
  if (!form.title?.trim()) { ElMessage.warning('请输入文章标题'); return }
  if (!form.categoryPath) { ElMessage.warning('请选择分类'); return }

  if (form.content_type === 'text' && !form.content?.trim()) {
    ElMessage.warning('请输入文章内容'); return
  }
  if (form.content_type === 'file' && form.fileList.length === 0) {
    ElMessage.warning('请上传文件'); return
  }

  saving.value = true
  try {
    if (form.content_type === 'file') {
      // FormData 提交（含文件）
      const fd = new FormData()
      fd.append('title', form.title.trim())
      fd.append('summary', form.summary?.trim() || '')
      fd.append('category_id', String(form.categoryPath))
      fd.append('status', form.status)
      fd.append('content_type', 'file')
      fd.append('file', form.fileList[0].raw || form.fileList[0])

      let res: any
      if (editingId.value) {
        res = await post(`/knowledge/articles/${editingId.value}?_method=PUT`, fd)
      } else {
        res = await post('/knowledge/articles', fd)
      }
      ElMessage.success(editingId.value ? '已更新' : '发布成功')
    } else {
      // 纯文本提交
      const payload = {
        title: form.title.trim(),
        content: form.content,
        summary: form.summary?.trim() || null,
        category_id: form.categoryPath,
        status: form.status,
      }
      if (editingId.value) {
        await put(`/knowledge/articles/${editingId.value}`, payload)
      } else {
        await post('/knowledge/articles', payload)
      }
      ElMessage.success(editingId.value ? '已更新' : '发布成功')
    }

    dialogVisible.value = false
    form.fileList = []
    loadArticles()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '发布失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(item: Article) {
  try {
    await del(`/knowledge/articles/${item.id}`)
    ElMessage.success('已删除')
    loadArticles()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

// ========== 分类管理 ==========
const categoryDialogVisible = ref(false)
const categoryDialogMode = ref<'addRoot' | 'addSub' | 'rename'>('addRoot')
const categoryDialogParent = ref<Category | null>(null)
const categoryDialogTarget = ref<Category | null>(null)
const categoryDialogName = ref('')
const categoryDialogIcon = ref('folder')
const categoryDialogSaving = ref(false)

function onCategoryAction(cmd: string) {
  if (cmd === 'root') openAddRoot()
  if (cmd === 'sub' && currentCategory.value) openAddSub(currentCategory.value)
}

function onNodeAction(cmd: string, data: Category) {
  if (cmd === 'addSub') openAddSub(data)
  if (cmd === 'rename') openRename(data)
  if (cmd === 'delete') deleteCategory(data)
}

function openAddRoot() {
  categoryDialogMode.value = 'addRoot'
  categoryDialogParent.value = null
  categoryDialogName.value = ''
  categoryDialogIcon.value = 'folder'
  categoryDialogVisible.value = true
}

function openAddSub(parent: Category) {
  categoryDialogMode.value = 'addSub'
  categoryDialogParent.value = parent
  categoryDialogName.value = ''
  categoryDialogIcon.value = 'folder'
  categoryDialogVisible.value = true
}

function openRename(target: Category) {
  categoryDialogMode.value = 'rename'
  categoryDialogTarget.value = target
  categoryDialogName.value = target.name
  categoryDialogVisible.value = true
}

async function confirmCategoryDialog() {
  const name = categoryDialogName.value.trim()
  if (!name) { ElMessage.warning('请输入分类名称'); return }
  categoryDialogSaving.value = true
  try {
    if (categoryDialogMode.value === 'addRoot') {
      await post('/knowledge/categories', { name, parent_id: null, icon: categoryDialogIcon.value })
      ElMessage.success('顶级分类已创建')
    } else if (categoryDialogMode.value === 'addSub') {
      await post('/knowledge/categories', {
        name, parent_id: categoryDialogParent.value!.id, icon: categoryDialogIcon.value
      })
      ElMessage.success('子分类已创建')
    } else if (categoryDialogMode.value === 'rename') {
      await put(`/knowledge/categories/${categoryDialogTarget.value!.id}`, { name })
      ElMessage.success('已重命名')
    }
    categoryDialogVisible.value = false
    await loadCategories()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '操作失败')
  } finally {
    categoryDialogSaving.value = false
  }
}

async function deleteCategory(c: Category) {
  if (c.articles_count) {
    ElMessage.warning(`「${c.name}」下还有 ${c.articles_count} 篇文章，请先移动或删除`)
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除分类「${c.name}」？${c.children?.length ? '其下所有子分类也会被删除' : ''}`,
      '删除分类', { type: 'warning' }
    )
  } catch { return }
  try {
    await del(`/knowledge/categories/${c.id}`)
    ElMessage.success('已删除')
    if (currentCategoryId.value === c.id) currentCategoryId.value = null
    await loadCategories()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '删除失败')
  }
}

function openCategoryDialogFromArticle() {
  // 在发布文章时点击"创建分类"
  categoryDialogMode.value = currentCategory.value ? 'addSub' : 'addRoot'
  categoryDialogParent.value = currentCategory.value
  categoryDialogName.value = ''
  categoryDialogIcon.value = 'folder'
  categoryDialogVisible.value = true
}

onMounted(() => {
  loadCategories()
  loadArticles()
})
</script>

<style lang="scss" scoped>
$primary: #0C447C;
$success: #1D9E75;
$warning: #BA7517;
$danger: #A32D2D;

.page-container { padding: 20px; background: linear-gradient(180deg, #f0f4fa 0%, #f5f7fa 100%); min-height: 100vh; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding:18px 20px; background:#fff; border-radius:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04);
  .page-title-wrap { display: flex; align-items: baseline; gap: 12px; }
  .page-title { font-size: 20px; font-weight: 600; color: $primary; }
  .page-desc { font-size: 13px; color: #909399; }
}

.category-tree {
  :deep(.el-card__body) { padding: 8px; }
  :deep(.el-card__header) { padding: 12px 16px; }
  :deep(.el-tree-node__content) { height: 34px; }
}
.cat-head { display: flex; align-items: center; justify-content: space-between; }
.cat-all {
  padding: 6px 10px; margin-bottom: 6px; border-radius: 6px;
  cursor: pointer; font-size: 14px; color: #303133;
  display: flex; align-items: center; gap: 6px;
  transition: background 0.2s;
  &:hover { background: #f5f7fa; }
  &.active { background: #e6f0fa; color: $primary; font-weight: 600; }
}
.cat-node { display: flex; align-items: center; gap: 6px; flex: 1; padding-right: 6px;
  &__name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  &.active { color: $primary; font-weight: 600; }
  &__more { padding: 2px 4px; border-radius: 3px; color: #9ca3af; opacity: 0; transition: opacity .2s; .cat-node:hover & { opacity: 1; } &:hover { background: #e5e7eb; color: $primary; } }
}

.filter-bar { display:flex; gap:12px; align-items:center; margin-bottom:16px; padding:12px 20px; background:#fff; border-radius:12px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.content-card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); min-height: 400px; }

.empty-hint { padding: 60px 0; }
.article-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 18px; margin-bottom: 8px; border-radius: 8px;
  border: 1px solid #f0f0f0; cursor: pointer; transition: all .2s;
  background: #fff;
  &:hover { border-color: $primary; box-shadow: 0 4px 12px rgba(12,68,124,0.08); transform: translateY(-1px); }
  .article-info { flex: 1; min-width: 0; }
  .article-title { font-size: 16px; font-weight: 600; color: #1f2937; margin: 0 0 6px; }
  .article-summary { font-size: 13px; color: #6b7280; line-height: 1.6; margin: 0 0 8px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
  .article-meta { display: flex; gap: 16px; align-items: center; font-size: 12px; color: #9ca3af;
    .el-icon { vertical-align: -2px; margin-right: 2px; }
  }
  .article-actions { flex-shrink: 0; margin-left: 16px; }
}

/* ============ 上传 ============ */
.upload-trigger { padding: 24px 0; text-align: center; color: #6b7280;
  &__icon { font-size: 48px; color: $primary; margin-bottom: 8px; }
  &__text { font-size: 14px; color: #374151; margin-bottom: 4px; }
  &__hint { font-size: 12px; color: #9ca3af; }
}
.upload-tip { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #6b7280; margin-top: 6px;
  .el-icon { color: $primary; }
}
:deep(.el-upload-dragger) { padding: 20px; border: 2px dashed #c0c4cc; border-radius: 8px; transition: all .2s;
  &:hover { border-color: $primary; background: #f0f4fa; }
}
</style>
