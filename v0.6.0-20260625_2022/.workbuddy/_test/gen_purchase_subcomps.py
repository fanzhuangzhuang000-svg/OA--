"""快速生成 purchase × 5 + finance/index 共 6 套子组件的脚本
只生成不依赖具体 schema 的最小骨架（filter + table + stat-cards），
每个模块的具体列用 placeholder，build 通过后用户填业务字段。
"""
import os

BASE = r'D:\work\website\OA\pc-web\src\views'

# 模块 → (子目录名, 主文件名, 标题, 列描述)
MODULES = [
    ('logistics',      'Logistics.vue',      '物流跟踪', [
        ('code',         '单号',     'width="160" fixed'),
        ('carrier',      '物流公司', 'width="120"'),
        ('tracking_no',  '物流单号', 'width="180"'),
        ('status',       '状态',     'width="100" align="center"'),
        ('shipped_at',   '发货时间', 'width="160" align="center"'),
    ]),
    ('approval',       'Approval.vue',       '采购审批', [
        ('code',     '计划编号', 'width="140" fixed'),
        ('title',    '计划名称', 'min-width="200" show-overflow-tooltip'),
        ('status',   '状态',     'width="100" align="center"'),
        ('created_at', '提交时间', 'width="160" align="center"'),
    ]),
    ('payment-request', 'PaymentRequest.vue', '付款申请', [
        ('code',         '申请编号', 'width="160" fixed'),
        ('contract_id',  '关联合同', 'width="100" align="center"'),
        ('amount',       '申请金额', 'width="140" align="right"'),
        ('status',       '状态',     'width="100" align="center"'),
        ('created_at',   '申请时间', 'width="160" align="center"'),
    ]),
    ('payment',        'Payment.vue',        '付款执行', [
        ('code',            '付款单号', 'width="160" fixed'),
        ('amount',          '付款金额', 'width="140" align="right"'),
        ('payment_method',  '付款方式', 'width="100" align="center"'),
        ('status',          '状态',     'width="100" align="center"'),
        ('paid_at',         '付款时间', 'width="160" align="center"'),
    ]),
    ('plan',           'Plan.vue',           '采购计划', [
        ('code',     '计划编号', 'width="140" fixed'),
        ('title',    '计划名称', 'min-width="200" show-overflow-tooltip'),
        ('status',   '状态',     'width="100" align="center"'),
        ('priority', '优先级',   'width="100" align="center"'),
    ]),
]

for sub, main, title, cols in MODULES:
    sub_dir = f'{BASE}\\purchase\\components\\{sub}'
    os.makedirs(sub_dir, exist_ok=True)

    # types.ts
    types = f'''// {title} 共享类型
export const STATUS_OPTIONS_{sub.upper().replace("-", "_")} = [
  {{ value: 'draft',     label: '草稿' }},
  {{ value: 'submitted', label: '已提交' }},
  {{ value: 'approved',  label: '已通过' }},
  {{ value: 'rejected',  label: '已驳回' }},
  {{ value: 'completed', label: '已完成' }},
]

export const statusLabel = (s: string) => STATUS_OPTIONS_{sub.upper().replace("-", "_")}.find(o => o.value === s)?.label || s
export const statusTagType = (s: string): 'info' | 'success' | 'warning' | 'danger' | 'primary' => {{
  if (s === 'draft') return 'info'
  if (s === 'submitted') return 'warning'
  if (s === 'approved' || s === 'completed') return 'success'
  if (s === 'rejected') return 'danger'
  return 'primary'
}}

export const formatMoney = (n: any) => Number(n || 0).toLocaleString('zh-CN', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }})
export const sliceDate = (s?: string) => s ? String(s).slice(0, 10) : '-'
'''
    with open(f'{sub_dir}\\types.ts', 'w', encoding='utf-8') as f:
        f.write(types)

    # FilterBar
    filter_bar = f'''<template>
  <div class="filter-bar">
    <el-form :inline="true" @submit.prevent="$emit('search')">
      <el-form-item label="关键词">
        <el-input :model-value="keyword" @update:model-value="(v: string) => emit('update:keyword', v)" placeholder="搜索 {title}" clearable style="width: 220px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :icon="Search" @click="emit('search')">查询</el-button>
        <el-button :icon="Refresh" @click="emit('reset')">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import {{ Search, Refresh }} from '@element-plus/icons-vue'
defineProps<{{ keyword: string }}>()
const emit = defineEmits<{{
  (e: 'update:keyword', v: string): void
  (e: 'search'): void
  (e: 'reset'): void
}}>()
</script>

<style lang="scss" scoped>
.filter-bar {{ background: #fff; padding: 16px 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03); }}
</style>
'''
    with open(f'{sub_dir}\\{sub.capitalize()}FilterBar.vue', 'w', encoding='utf-8') as f:
        f.write(filter_bar)

    # Table
    cols_template = '\n'.join([
        f'''      <el-table-column {extra}>
        <template #default="{{ row }}">
          {{{{ row.{key} || '-' }}}}
        </template>
      </el-table-column>'''
        for key, _, extra in cols
    ])

    table = f'''<template>
  <div>
    <el-table :data="list" stripe border v-loading="loading" :header-cell-style="{{{{ background: '#f5f7fa', color: '#303133', fontWeight: 600 }}}}">
{cols_template}
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{{ row }}">
          <el-button link type="primary" @click="emit('view', row)">查看</el-button>
          <el-button link type="warning" @click="emit('edit', row)">编辑</el-button>
          <el-button link type="danger" @click="emit('delete', row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-wrapper">
      <el-pagination
        :current-page="page" :page-size="pageSize"
        :page-sizes="[5, 10, 20]" :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="(p: number) => emit('pageChange', p)"
        @size-change="(s: number) => emit('sizeChange', s)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{{
  list: any[]
  loading: boolean
  page: number
  pageSize: number
  total: number
}}>()
const emit = defineEmits<{{
  (e: 'view', row: any): void
  (e: 'edit', row: any): void
  (e: 'delete', row: any): void
  (e: 'pageChange', p: number): void
  (e: 'sizeChange', s: number): void
}}>()
</script>

<style lang="scss" scoped>
.pagination-wrapper {{ margin-top: 16px; display: flex; justify-content: flex-end; }}
</style>
'''
    with open(f'{sub_dir}\\{sub.capitalize()}Table.vue', 'w', encoding='utf-8') as f:
        f.write(table)

    # StatCards
    stat_cards = f'''<template>
  <div class="stats-row">
    <div class="stat-card" v-for="(s, i) in cards" :key="i" :style="{{{{ borderColor: s.color }}}}">
      <div class="stat-icon" :style="{{{{ background: s.color + '15', color: s.color }}}}">
        <el-icon :size="20"><component :is="s.icon" /></el-icon>
      </div>
      <div>
        <div class="stat-value" :style="{{{{ color: s.color }}}}">{{{{ s.value }}}}</div>
        <div class="stat-label">{{{{ s.label }}}}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ computed }} from 'vue'
import {{ Document, Money, CircleCheck }} from '@element-plus/icons-vue'
import {{ formatMoney }} from './types'

interface Stats {{ total: number; total_amount: number }}
const props = defineProps<{{ stats: Stats }}>()

const cards = computed(() => [
  {{ label: '{title}总数',   value: props.stats.total,                           icon: Document,    color: '#0C447C' }},
  {{ label: '总金额',         value: '¥ ' + formatMoney(props.stats.total_amount), icon: Money,       color: '#1D9E75' }},
  {{ label: '已完成',         value: props.stats.total,                           icon: CircleCheck, color: '#BA7517' }},
])
</script>

<style lang="scss" scoped>
.stats-row {{ display: flex; gap: 16px; margin-bottom: 16px; }}
.stat-card {{
  flex: 1; display: flex; align-items: center; gap: 12px;
  padding: 16px; background: #fff; border-radius: 8px;
  border-left: 3px solid #909399; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
}}
.stat-icon {{ width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }}
.stat-value {{ font-size: 22px; font-weight: 700; }}
.stat-label {{ font-size: 12px; color: #909399; }}
</style>
'''
    with open(f'{sub_dir}\\{sub.capitalize()}StatCards.vue', 'w', encoding='utf-8') as f:
        f.write(stat_cards)

    print(f'  generated: {sub} (FilterBar/Table/StatCards/types)')

print('done')
