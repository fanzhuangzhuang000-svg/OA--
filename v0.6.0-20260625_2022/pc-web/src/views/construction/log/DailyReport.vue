<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" plain @click="goBack">返回</el-button>
        <span class="page-title">每日上报</span>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button :icon="ArrowLeft" @click="shiftMonth(-1)">上月</el-button>
          <el-button @click="resetMonth">本月</el-button>
          <el-button :icon="ArrowRight" @click="shiftMonth(1)">下月</el-button>
        </el-button-group>
        <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
      </div>
    </div>

    <!-- KPI 月度统计 -->
    <div class="kpi-row">
      <el-card v-for="kpi in kpis" :key="kpi.label" shadow="hover" :body-style="{ padding: '14px 18px' }" class="kpi-card">
        <div class="kpi-label">{{ kpi.label }}</div>
        <div class="kpi-value" :style="{ color: kpi.color }">{{ kpi.value }}</div>
      </el-card>
    </div>

    <!-- 漏报警告 -->
    <OverdueAlert
      v-if="overdueList.length"
      :overdue-list="overdueList"
      class="overdue-block"
      @fill="handleFillOverdue"
    />

    <!-- 日历 + 今日上报 -->
    <div class="main-grid">
      <!-- 日历 -->
      <el-card shadow="never" class="calendar-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">{{ calendarTitle }}</span>
            <div class="legend">
              <span class="legend-item"><span class="dot dot-done"></span>已报</span>
              <span class="legend-item"><span class="dot dot-miss"></span>未报</span>
              <span class="legend-item"><span class="dot dot-today"></span>今天</span>
            </div>
          </div>
        </template>
        <el-calendar v-model="calendarDate">
          <template #date-cell="{ data }">
            <div
              class="cal-cell"
              :class="{
                'is-today': data.isSelected && isToday(data.day),
                'is-done': isReported(data.day),
                'is-miss': isMissed(data.day),
                'not-in-month': data.type !== 'current-month',
              }"
              @click="selectDate(data.day)"
            >
              <div class="cal-day">{{ data.day.split('-').slice(2).join('') }}</div>
              <div v-if="isReported(data.day)" class="cal-badge done-badge">已报</div>
              <div v-else-if="isMissed(data.day)" class="cal-badge miss-badge">未报</div>
            </div>
          </template>
        </el-calendar>
      </el-card>

      <!-- 右侧今日上报表单 -->
      <el-card shadow="never" class="form-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">上报 — {{ selectedDate }}</span>
            <el-tag v-if="selectedLog" :type="statusTagType(selectedLog.status)" effect="plain" size="small">
              {{ statusLabel(selectedLog.status) }}
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="small">未上报</el-tag>
          </div>
        </template>

        <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px" size="default">
          <el-form-item label="日期" prop="date">
            <el-date-picker
              v-model="formData.date"
              type="date"
              value-format="YYYY-MM-DD"
              :disabled="!!selectedLog"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="天气" prop="weather">
            <el-select v-model="formData.weather" placeholder="请选择" style="width: 100%">
              <el-option v-for="w in weatherOptions" :key="w" :label="w" :value="w" />
            </el-select>
          </el-form-item>
          <el-form-item label="开工单" prop="commencement_id">
            <el-select
              v-model="formData.commencement_id"
              placeholder="请选择开工单"
              filterable
              clearable
              :disabled="!!selectedLog"
              style="width: 100%"
            >
              <el-option
                v-for="o in commencementOptions"
                :key="o.id"
                :label="`${o.code} - ${o.project?.name || o.team?.name || ''}`"
                :value="o.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="工序" prop="process_id">
            <el-select
              v-model="formData.process_id"
              placeholder="请选择工序"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="p in processOptions"
                :key="p.id"
                :label="`${p.name}${p.code ? ' (' + p.code + ')' : ''}`"
                :value="p.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="工人数量" prop="worker_count">
            <el-input-number v-model="formData.worker_count" :min="1" :step="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="工时" prop="work_hours">
            <el-input-number v-model="formData.work_hours" :min="0" :step="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="进度" prop="progress">
            <el-input-number v-model="formData.progress" :min="0" :max="100" :step="5" style="width: 100%" />
          </el-form-item>
          <el-form-item label="问题与风险">
            <el-input v-model="formData.issues" type="textarea" :rows="3" maxlength="1000" show-word-limit />
          </el-form-item>
          <el-form-item label="照片URL">
            <el-input v-model="formData.photos" placeholder="多个用逗号分隔（可选）" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="formData.remark" type="textarea" :rows="2" maxlength="500" show-word-limit />
          </el-form-item>
        </el-form>

        <div class="form-actions">
          <el-button v-if="selectedLog" :icon="Upload" type="success" :loading="submitting" @click="handleSubmit">
            提交日志
          </el-button>
          <el-button v-if="!selectedLog" type="primary" :loading="saving" @click="handleSave('draft')">
            保存草稿
          </el-button>
          <el-button v-if="!selectedLog" type="success" :loading="saving" @click="handleSave('submit')">
            保存并提交
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Refresh, Upload } from '@element-plus/icons-vue'
import { logApi, commencementApi, workProcessApi } from '@/api/construction'
import OverdueAlert from './components/OverdueAlert.vue'

const router = useRouter()

const weatherOptions = ['晴', '多云', '阴', '小雨', '中雨', '大雨', '雪', '雾', '大风']

const statusLabel = (s: string) => ({
  draft: '草稿', submitted: '已提交', approved: '已审核',
} as Record<string, string>)[s] || s || '-'
const statusTagType = (s: string): any => ({
  draft: 'info', submitted: 'warning', approved: 'success',
} as Record<string, string>)[s] || 'info'

const today = new Date()
const todayStr = today.toISOString().slice(0, 10)

const calendarDate = ref(today)
const selectedDate = ref(todayStr)
const calendarTitle = computed(() => {
  const d = calendarDate.value
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月`
})

const monthLogs = ref<any[]>([])      // 当月所有日志
const overdueList = ref<any[]>([])    // 漏报
const commencementOptions = ref<any[]>([])
const processOptions = ref<any[]>([])

const formRef = ref()
const saving = ref(false)
const submitting = ref(false)

const formData = reactive({
  date: todayStr,
  weather: '晴',
  commencement_id: null as number | null,
  process_id: null as number | null,
  worker_count: 1,
  work_hours: 0,
  progress: 0,
  issues: '',
  photos: '',
  remark: '',
})

const formRules = {
  date:        [{ required: true, message: '请选择日期', trigger: 'change' }],
  weather:     [{ required: true, message: '请选择天气', trigger: 'change' }],
  commencement_id: [{ required: true, message: '请选择开工单', trigger: 'change' }],
  worker_count:[{ required: true, message: '请填写工人数量', trigger: 'blur' }],
  work_hours:  [{ required: true, message: '请填写工时', trigger: 'blur' }],
  progress:    [{ required: true, message: '请填写进度', trigger: 'blur' }],
}

// === 当前选中的日志（如果已存在）===
const selectedLog = computed(() => {
  return monthLogs.value.find(l => l.date === selectedDate.value) || null
})

// === 标记日历单元格 ===
const reportedDates = computed(() => new Set(monthLogs.value.map(l => l.date)))
const isReported = (day: string) => reportedDates.value.has(day)
const isToday = (day: string) => day === todayStr
const isMissed = (day: string) => {
  if (day >= todayStr) return false   // 未来/今天不标记为漏报
  if (isReported(day)) return false
  return true
}

// === KPI ===
const kpis = computed(() => {
  const reported = monthLogs.value.length
  const submitted = monthLogs.value.filter(l => l.status === 'submitted' || l.status === 'approved').length
  const totalHours = monthLogs.value.reduce((s, l) => s + Number(l.work_hours || 0), 0)
  const avgProgress = reported
    ? Math.round(monthLogs.value.reduce((s, l) => s + Number(l.progress || 0), 0) / reported)
    : 0
  return [
    { label: '本月已报', value: reported, color: '#0C447C' },
    { label: '已提交/审核', value: submitted, color: '#67c23a' },
    { label: '累计工时', value: `${totalHours} h`, color: '#1D9E75' },
    { label: '平均进度', value: `${avgProgress}%`, color: '#E6A23C' },
  ]
})

// === 加载 ===
const monthRange = computed(() => {
  const d = calendarDate.value
  const y = d.getFullYear()
  const m = d.getMonth()
  const start = new Date(y, m, 1)
  const end = new Date(y, m + 1, 0)
  const fmt = (x: Date) => x.toISOString().slice(0, 10)
  return { from: fmt(start), to: fmt(end) }
})

const loadMonthLogs = async () => {
  try {
    const res: any = await logApi.list({
      per_page: 500,
      date_from: monthRange.value.from,
      date_to: monthRange.value.to,
    })
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    monthLogs.value = arr
  } catch {
    monthLogs.value = []
  }
}

const loadOverdue = async () => {
  try {
    const res: any = await logApi.overdue({ per_page: 20 })
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    overdueList.value = arr
  } catch {
    overdueList.value = []
  }
}

const loadCommencementOptions = async () => {
  try {
    const res: any = await commencementApi.list({ per_page: 500 })
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    commencementOptions.value = arr
  } catch {
    commencementOptions.value = []
  }
}

const loadProcessOptions = async () => {
  try {
    const res: any = await workProcessApi.list({ per_page: 500 })
    const arr = (res && Array.isArray(res.data)) ? res.data : (Array.isArray(res) ? res : [])
    processOptions.value = arr
  } catch {
    processOptions.value = []
  }
}

const loadAll = async () => {
  await Promise.all([loadMonthLogs(), loadOverdue()])
  syncFormFromSelected()
}

const syncFormFromSelected = () => {
  const log = selectedLog.value
  if (log) {
    formData.date = log.date || selectedDate.value
    formData.weather = log.weather || '晴'
    formData.commencement_id = log.commencement_id ?? null
    formData.process_id = log.process_id ?? null
    formData.worker_count = Number(log.worker_count || 1)
    formData.work_hours = Number(log.work_hours || 0)
    formData.progress = Number(log.progress || 0)
    formData.issues = log.issues || ''
    formData.photos = Array.isArray(log.photos) ? log.photos.join(',') : (log.photos || '')
    formData.remark = log.remark || ''
  } else {
    formData.date = selectedDate.value
    formData.weather = '晴'
    formData.commencement_id = null
    formData.process_id = null
    formData.worker_count = 1
    formData.work_hours = 0
    formData.progress = 0
    formData.issues = ''
    formData.photos = ''
    formData.remark = ''
  }
}

// === 操作 ===
const shiftMonth = (n: number) => {
  const d = new Date(calendarDate.value)
  d.setMonth(d.getMonth() + n)
  calendarDate.value = d
  loadMonthLogs()
}
const resetMonth = () => {
  calendarDate.value = new Date()
  selectedDate.value = todayStr
  loadMonthLogs()
  syncFormFromSelected()
}

const selectDate = (day: string) => {
  selectedDate.value = day
  syncFormFromSelected()
}

const goBack = () => router.push('/construction/log')

const handleFillOverdue = (item: any) => {
  if (item.date) {
    selectedDate.value = item.date
    formData.date = item.date
    if (item.commencement_id) formData.commencement_id = item.commencement_id
    syncFormFromSelected()
  }
}

const handleSave = async (action: 'draft' | 'submit') => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      date: formData.date,
      weather: formData.weather,
      commencement_id: formData.commencement_id,
      process_id: formData.process_id,
      worker_count: Number(formData.worker_count || 1),
      work_hours: Number(formData.work_hours || 0),
      progress: Number(formData.progress || 0),
      issues: formData.issues,
      photos: formData.photos,
      remark: formData.remark,
    }
    const res: any = await logApi.create(payload)
    const id = res?.id || res?.data?.id
    if (action === 'submit' && id) {
      await logApi.submit(id)
      ElMessage.success('已上报并提交')
    } else {
      ElMessage.success('草稿已保存')
    }
    await loadAll()
  } catch { /* 拦截器已提示 */ }
  finally { saving.value = false }
}

const handleSubmit = async () => {
  if (!selectedLog.value?.id) return
  submitting.value = true
  try {
    await logApi.submit(selectedLog.value.id)
    ElMessage.success('已提交')
    await loadAll()
  } catch { /* 拦截器已提示 */ }
  finally { submitting.value = false }
}

watch(calendarDate, () => loadMonthLogs())
watch(selectedDate, () => syncFormFromSelected())

onMounted(() => {
  loadCommencementOptions()
  loadProcessOptions()
  loadAll()
})
</script>

<style lang="scss" scoped>
.page-container { padding: 16px; background: #f5f7fa; min-height: calc(100vh - 60px); }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  .header-left { display: flex; align-items: center; gap: 12px; }
  .page-title {
    font-size: 18px; font-weight: 600; color: #0C447C;
    border-left: 4px solid #0C447C; padding-left: 10px;
  }
  .header-actions { display: flex; gap: 8px; }
}
.kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px;
}
.kpi-card {
  .kpi-label { color: #909399; font-size: 13px; }
  .kpi-value { font-size: 22px; font-weight: 700; margin-top: 4px; }
}
.overdue-block { margin-bottom: 12px; }

.main-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 12px;
}
.calendar-card :deep(.el-calendar) { padding: 0; }
.calendar-card :deep(.el-calendar__header) { padding: 8px 16px; }
.calendar-card :deep(.el-calendar-day) { padding: 4px; height: 64px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: 600; color: #303133; }

.cal-cell {
  height: 56px; display: flex; flex-direction: column; align-items: flex-start; justify-content: space-between;
  padding: 4px 6px; border-radius: 4px; cursor: pointer; transition: background 0.2s;
}
.cal-cell:hover { background: #f5f7fa; }
.cal-cell.is-today { background: #ecf5ff; }
.cal-cell.is-done { background: #f0f9eb; }
.cal-cell.is-miss { background: #fef0f0; }
.cal-cell.not-in-month { opacity: 0.4; }
.cal-day { font-size: 14px; font-weight: 500; }
.cal-badge {
  font-size: 11px; padding: 1px 6px; border-radius: 8px; line-height: 1.4;
}
.done-badge { background: #67c23a; color: #fff; }
.miss-badge { background: #f56c6c; color: #fff; }

.legend { display: flex; gap: 12px; font-size: 12px; color: #606266; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-done { background: #67c23a; }
.dot-miss { background: #f56c6c; }
.dot-today { background: #409eff; }

.form-card {
  height: fit-content;
  .form-actions {
    display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px;
    padding-top: 12px; border-top: 1px solid #ebeef5;
  }
}
</style>
