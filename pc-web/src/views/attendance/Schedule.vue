<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">排班计划</span>
      <div class="header-actions">
        <el-button :icon="MagicStick" @click="handleSmartSuggest">智能排班建议</el-button>
        <el-button type="primary" :icon="Check" @click="saveSchedules" :loading="saving">保存排班</el-button>
      </div>
    </div>

    <el-alert
      title="排班说明"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    >
      <template #default>
        1) 选班组批量排: <b>左侧选班组 + 选班次 + 日期范围 + 一键应用</b>，整组自动填好；<br>
        2) 表格里每个格子直接点选下拉选班次，<b>标黄</b>的格子表示已修改未保存；<br>
        3) 顶部"智能建议"基于历史 30 天打卡时间推断每位员工最匹配的班次，<b>一键填充</b>。
      </template>
    </el-alert>

    <!-- 快速排班: 班组 + 班次 + 日期范围 -->
    <div class="quick-card">
      <div class="quick-card__title">⚡ 快速排班 (整组设置)</div>
      <el-form :inline="true" :model="quickForm" class="quick-card__form">
        <el-form-item label="班组">
          <el-select v-model="quickForm.group_id" placeholder="选班组" style="width: 180px" filterable>
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班次">
          <el-select v-model="quickForm.shift_id" placeholder="选班次" style="width: 180px" filterable>
            <el-option v-for="s in shifts" :key="s.id" :value="s.id">
              <span :style="{ color: s.color, fontWeight: 600 }">●</span>
              {{ s.name }} ({{ s.start_time?.slice(0,5) }}~{{ s.end_time?.slice(0,5) }})
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="quickForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 150px" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="quickForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 150px" />
        </el-form-item>
        <el-form-item label="跳过周末">
          <el-switch v-model="quickForm.skip_weekends" />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" :icon="MagicStick" @click="applyByGroup" :loading="applying">一键应用</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 周排班表 -->
    <div class="content-card">
      <div class="toolbar">
        <el-button :icon="ArrowLeft" size="small" @click="changeWeek(-7)">上一周</el-button>
        <el-button :icon="ArrowRight" size="small" @click="changeWeek(7)">下一周</el-button>
        <el-button size="small" @click="goToday">本周</el-button>
        <span class="toolbar__range">{{ weekRangeLabel }}</span>
        <el-select v-model="filterGroupId" placeholder="筛选班组" clearable style="width: 160px" size="small">
          <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
        <span class="toolbar__count" v-if="dirtyCount > 0">已修改 {{ dirtyCount }} 项</span>
      </div>

      <el-table
        :data="tableRows"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        empty-text="本周无排班"
        :cell-class-name="cellClass"
      >
        <el-table-column prop="name" label="员工" min-width="100" fixed>
          <template #default="{ row }">
            <div class="emp-cell">
              <span class="emp-cell__name">{{ row.name }}</span>
              <el-tag v-if="row.group_name" size="small" :style="{ background: row.group_color, color: '#fff', border: 'none' }">{{ row.group_name }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          v-for="day in weekDays"
          :key="day.iso"
          :label="day.label"
          :min-width="110"
          align="center"
        >
          <template #header>
            <div class="day-header">
              <div class="day-header__date">{{ day.dateLabel }}</div>
              <div class="day-header__week" :class="{ 'is-weekend': day.isWeekend }">{{ day.weekLabel }}</div>
            </div>
          </template>
          <template #default="{ row }">
            <el-select
              :model-value="cellValue(row.id, day.iso)"
              placeholder="+"
              size="small"
              clearable
              style="width: 100%"
              @change="(v: any) => setCell(row.id, day.iso, v)"
              @clear="setCell(row.id, day.iso, null)"
            >
              <el-option
                v-for="s in shifts"
                :key="s.id"
                :value="s.id"
              >
                <span :style="{ color: s.color, fontWeight: 600 }">●</span>
                {{ s.name }}<br>
                <span style="font-size: 11px; color: #909399">{{ s.start_time?.slice(0,5) }}~{{ s.end_time?.slice(0,5) }}</span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 智能建议对话框 -->
    <el-dialog v-model="suggestDialogVisible" title="智能排班建议" width="1500px" destroy-on-close>
      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 12px">
        <template #default>
          基于每位员工过去 30 天的打卡时间, 推断最匹配的班次。
        </template>
      </el-alert>
      <el-table :data="suggestions" stripe max-height="400">
        <el-table-column prop="user_name" label="员工" />
        <el-table-column label="建议班次">
          <template #default="{ row }">
            <el-tag v-if="row.suggested_shift_name" :color="row.suggested_shift_color" effect="dark" style="color: #fff; border: none">
              {{ row.suggested_shift_name }}
            </el-tag>
            <span v-else style="color:#c0c4cc">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="applySuggestion(row)" :disabled="!row.suggested_shift_id">采用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Check, MagicStick, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { schedule } from '@/api/modules'
import { get } from '@/utils/request'

const shifts = ref<any[]>([])
const groups = ref<any[]>([])
const users = ref<any[]>([])
const weekStart = ref(getMonday(today()))

const tableRows = ref<any[]>([])
const cellMap = ref<Record<string, any>>({})   // key: `${userId}-${date}` → { shift_id, shift_name, color, id, dirty, original_shift_id }
const originalMap = ref<Record<string, number>>({}) // 用于 dirty 检测
const loading = ref(false)
const saving = ref(false)
const applying = ref(false)
const filterGroupId = ref<number | null>(null)

const suggestDialogVisible = ref(false)
const suggestions = ref<any[]>([])

const quickForm = reactive({
  group_id: null as number | null,
  shift_id: null as number | null,
  start_date: today(),
  end_date: today(),
  skip_weekends: false,
})

function today() { return new Date().toISOString().slice(0, 10) }
function getMonday(d: string) {
  const dt = new Date(d)
  const dow = dt.getDay() || 7  // 周日 0 → 7
  dt.setDate(dt.getDate() - (dow - 1))
  return dt.toISOString().slice(0, 10)
}

const weekDays = computed(() => {
  const out = []
  const start = new Date(weekStart.value)
  for (let i = 0; i < 7; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i)
    const iso = d.toISOString().slice(0, 10)
    out.push({
      iso,
      dateLabel: `${d.getMonth() + 1}/${d.getDate()}`,
      weekLabel: ['日', '一', '二', '三', '四', '五', '六'][d.getDay()],
      isWeekend: d.getDay() === 0 || d.getDay() === 6,
    })
  }
  return out
})

const weekRangeLabel = computed(() => {
  const start = weekDays.value[0]?.iso
  const end = weekDays.value[6]?.iso
  return start && end ? `${start} ~ ${end}` : ''
})

const dirtyCount = computed(() => {
  return Object.values(cellMap.value).filter((c: any) => c.dirty).length
})

const cellValue = (userId: number, iso: string) => {
  const c = cellMap.value[`${userId}-${iso}`]
  return c?.shift_id ?? undefined
}

const cellClass = ({ row, column }: any) => {
  if (column.label === '员工') return ''
  // column.label 是日期 (1/20 这种)
  const day = weekDays.value.find(d => d.dateLabel === column.label)
  if (!day) return ''
  const c = cellMap.value[`${row.id}-${day.iso}`]
  return c?.dirty ? 'cell-dirty' : ''
}

const setCell = (userId: number, iso: string, shiftId: number | null) => {
  const key = `${userId}-${iso}`
  const original = originalMap.value[key]
  if (shiftId === null) {
    delete cellMap.value[key]
    return
  }
  const shift = shifts.value.find(s => s.id === shiftId)
  cellMap.value[key] = {
    shift_id: shiftId,
    shift_name: shift?.name,
    color: shift?.color,
    dirty: shiftId !== original,
    id: undefined,
  }
}

const changeWeek = (days: number) => {
  const d = new Date(weekStart.value); d.setDate(d.getDate() + days)
  weekStart.value = getMonday(d.toISOString().slice(0, 10))
  loadWeek()
}
const goToday = () => { weekStart.value = getMonday(today()); loadWeek() }

const loadUsers = async () => {
  try {
    const r: any = await get('/employees', { per_page: 200 })
    const d = r?.data?.data || r?.data || r || []
    users.value = Array.isArray(d) ? d : (d?.data || [])
  } catch { /* ignore */ }
}

const loadShifts = async () => {
  const r: any = await schedule.listShifts()
  shifts.value = Array.isArray(r) ? r : (r?.data || [])
}

const loadGroups = async () => {
  const r: any = await schedule.listGroups()
  groups.value = Array.isArray(r) ? r : (r?.data || [])
}

const loadWeek = async () => {
  loading.value = true
  cellMap.value = {}
  originalMap.value = {}
  try {
    const start = weekStart.value
    const end = weekDays.value[6]?.iso
    const r: any = await schedule.index({ start, end })
    const byDate = r?.data?.by_date || {}

    // 行: 所有员工, 按班组聚合 (无班组的放最后)
    const allUsers = users.value.map((u: any) => {
      const grp = groups.value.find((g: any) => g.members?.some((m: any) => m.user_id === u.id))
      return {
        id: u.id,
        name: u.name || u.username,
        group_name: grp?.name,
        group_color: grp?.color,
        group_id: grp?.id,
      }
    }).filter((u: any) => !filterGroupId.value || u.group_id === filterGroupId.value)
      .sort((a: any, b: any) => (a.group_name || 'zzz').localeCompare(b.group_name || 'zzz'))
    tableRows.value = allUsers

    // 填格子
    for (const iso of Object.keys(byDate)) {
      for (const a of byDate[iso]) {
        const key = `${a.user_id}-${iso}`
        cellMap.value[key] = {
          shift_id: a.shift_id,
          shift_name: a.shift_name,
          color: a.shift_color,
          dirty: false,
          id: a.id,
        }
        originalMap.value[key] = a.shift_id
      }
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  } finally { loading.value = false }
}

const saveSchedules = async () => {
  const assignments: any[] = []
  for (const [key, c] of Object.entries(cellMap.value)) {
    if (!c.dirty) continue
    const [user_id, date] = key.split('-')
    assignments.push({ user_id: Number(user_id), date, shift_id: c.shift_id })
  }
  if (assignments.length === 0) {
    ElMessage.info('没有修改需要保存')
    return
  }
  saving.value = true
  try {
    const r: any = await schedule.batchSave(assignments)
    ElMessage.success(r?.message || '保存成功')
    await loadWeek()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally { saving.value = false }
}

const applyByGroup = async () => {
  if (!quickForm.group_id || !quickForm.shift_id) {
    ElMessage.warning('请选班组和班次')
    return
  }
  if (!quickForm.start_date || !quickForm.end_date) {
    ElMessage.warning('请选日期范围')
    return
  }
  applying.value = true
  try {
    const r: any = await schedule.batchByGroup({
      group_id: quickForm.group_id,
      shift_id: quickForm.shift_id,
      start_date: quickForm.start_date,
      end_date: quickForm.end_date,
      skip_weekends: quickForm.skip_weekends,
    })
    ElMessage.success(r?.message || '已应用')
    await loadWeek()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '应用失败')
  } finally { applying.value = false }
}

const handleSmartSuggest = async () => {
  const start = weekStart.value
  const end = weekDays.value[6]?.iso
  const r: any = await schedule.smartSuggest({ start_date: start, end_date: end })
  const list = Array.isArray(r) ? r : (r?.data || [])
  suggestions.value = list.map((s: any) => {
    const u = users.value.find((x: any) => x.id === s.user_id)
    return { ...s, user_name: u?.name || u?.username || `#${s.user_id}` }
  })
  suggestDialogVisible.value = true
}

const applySuggestion = (row: any) => {
  // 一键填入本周
  for (const day of weekDays.value) {
    if (day.isWeekend) continue
    setCell(row.user_id, day.iso, row.suggested_shift_id)
  }
  ElMessage.success(`已为 ${row.user_name} 填充本周`)
  suggestDialogVisible.value = false
}

onMounted(async () => {
  await loadShifts()
  await loadGroups()
  await loadUsers()
  await loadWeek()
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; .page-title { font-size: 20px; font-weight: 600; color: #303133; } }
.quick-card { background: #fff; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); &__title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 12px; } &__form { display: flex; flex-wrap: wrap; gap: 0; } }
.content-card { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; &__range { font-size: 14px; font-weight: 600; color: #303133; margin: 0 8px; } &__count { margin-left: auto; color: #BA7517; font-size: 13px; } }
.emp-cell { display: flex; align-items: center; gap: 6px; &__name { font-weight: 500; } }
.day-header__date { font-weight: 600; font-size: 14px; } .day-header__week { font-size: 12px; color: #606266; &.is-weekend { color: #A32D2D; } }
:deep(.cell-dirty) { background: #fffbe6 !important; }
:deep(.cell-dirty .el-select__wrapper) { box-shadow: 0 0 0 1px #BA7517 inset !important; }
</style>
