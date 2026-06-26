<template>
  <el-dialog
    v-model="visible"
    title="编辑客户"
    width="780px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      v-if="form"
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <div class="section-title">基本信息</div>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="客户名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入客户名称" maxlength="128" show-word-limit />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="行业" prop="industry">
            <el-input v-model="form.industry" placeholder="例: 智能制造/金融/政府" maxlength="64" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="客户分类" prop="category">
            <el-select v-model="form.category" placeholder="请选择" clearable style="width: 100%">
              <el-option label="VIP 客户" value="vip" />
              <el-option label="普通客户" value="normal" />
              <el-option label="潜在客户" value="potential" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="客户来源" prop="source">
            <el-select v-model="form.source" placeholder="请选择" clearable allow-create filterable style="width: 100%">
              <el-option label="转介绍" value="referral" />
              <el-option label="陌拜" value="cold_call" />
              <el-option label="展会" value="exhibition" />
              <el-option label="网络营销" value="online" />
              <el-option label="老客户" value="existing" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

        <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="省" prop="province">
            <el-input v-model="form.province" placeholder="例: 北京市 (可选)" maxlength="32" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="市" prop="city">
            <el-input v-model="form.city" placeholder="例: 北京市 (可选)" maxlength="32" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="区/县" prop="district">
            <el-input v-model="form.district" placeholder="例: 朝阳区 (可选)" maxlength="32" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="详细地址" prop="address">
        <el-input v-model="form.address" placeholder="街道、楼栋、门牌号 (可选)" maxlength="255" />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="form.status">
              <el-radio value="active">启用</el-radio>
              <el-radio value="inactive">停用</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="客户标签" prop="tags">
        <el-select
          v-model="form.tags"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="可输入后回车创建标签"
          style="width: 100%"
        >
          <el-option v-for="t in commonTags" :key="t" :label="t" :value="t" />
        </el-select>
      </el-form-item>

      <el-form-item label="备注" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="客户背景、需求特点、注意事项等"
        />
      </el-form-item>

      <div class="section-title">
        联系人
        <span class="section-hint">客户的所有联系人 (姓名/职务/电话), 第一个为主联系人</span>
      </div>

      <el-form-item
        v-for="(c, idx) in contactList"
        :key="c.__key"
        :label="idx === 0 ? '主联系人' : '联系人 ' + idx"
        :prop="`contacts.${idx}.phone`"
        class="contact-row"
      >
        <div class="contact-row__fields">
          <el-input
            v-model="c.name"
            placeholder="姓名"
            maxlength="64"
            style="width: 130px"
          />
          <el-input
            v-model="c.position"
            placeholder="职务 (例: 经理/总监)"
            maxlength="100"
            style="width: 180px"
          />
          <el-input
            v-model="c.phone"
            placeholder="电话 (必填)"
            maxlength="32"
            style="flex: 1"
          />
          <el-button
            v-if="contactList.length > 1"
            :icon="Delete"
            type="danger"
            plain
            size="small"
            @click="removeContact(idx)"
          >删除</el-button>
        </div>
      </el-form-item>

      <el-form-item>
        <el-button :icon="Plus" plain type="primary" @click="addContact">添加联系人</el-button>
      </el-form-item>

      <div class="section-title">
        开票信息
        <span class="section-hint">客户的开票抬头/税号/银行账户, 可添加多条, 标记其中一条为默认</span>
      </div>

      <el-form-item
        v-for="(info, idx) in invoiceList"
        :key="info.__key"
        :label="idx === 0 ? '开票信息 1' : '开票信息 ' + (idx + 1)"
        class="invoice-row"
      >
        <div class="invoice-row__fields">
          <el-select v-model="info.invoice_type" placeholder="发票类型" style="width: 150px" size="default">
            <el-option label="增值税普通发票" value="general" />
            <el-option label="增值税专用发票" value="special" />
            <el-option label="电子发票" value="electronic" />
          </el-select>
          <el-input
            v-model="info.company_name"
            placeholder="单位名称 (抬头) *"
            maxlength="200"
            style="width: 280px"
          />
          <el-input
            v-model="info.tax_no"
            placeholder="纳税人识别号 (税号) *"
            maxlength="50"
            style="width: 220px"
          />
          <el-checkbox v-model="info.is_default" @change="onDefaultChange(idx)">默认</el-checkbox>
          <el-button
            :icon="Delete"
            type="danger"
            plain
            size="small"
            @click="removeInvoice(idx)"
          >删除</el-button>
        </div>
        <div class="invoice-row__extra">
          <el-input
            v-model="info.register_address"
            placeholder="注册地址 (选填)"
            maxlength="200"
            class="extra-cell"
          />
          <el-input
            v-model="info.register_phone"
            placeholder="注册电话 (选填)"
            maxlength="32"
            class="extra-cell"
          />
          <el-input
            v-model="info.bank_name"
            placeholder="开户银行 (选填)"
            maxlength="100"
            class="extra-cell"
          />
          <el-input
            v-model="info.bank_account"
            placeholder="银行账号 (选填)"
            maxlength="50"
            class="extra-cell"
          />
        </div>
        <el-input
          v-model="info.remark"
          type="textarea"
          :rows="1"
          placeholder="备注 (选填)"
          maxlength="500"
          style="margin-top: 6px"
        />
      </el-form-item>

      <el-form-item>
        <el-button :icon="Plus" plain type="primary" @click="addInvoice">添加开票信息</el-button>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { put, post, del } from '@/utils/request'
import type { Customer, Contact, InvoiceInfo } from './types'

interface Props {
  modelValue: boolean
  customer: Customer
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

// 表单 ref
const formRef = ref<FormInstance>()
const submitting = ref(false)

// 联系人行 — 每行带 __key 用于 v-for 追踪
interface ContactRow {
  __key: number
  id?: number         // 已有联系人带 id (用于同步删除), 新增的没有
  name: string
  position: string
  phone: string
  is_primary: boolean
  isNew: boolean      // true = 本次新增 (要 POST)
  isRemoved: boolean  // true = 本次删除 (要 DELETE)
}

let __seq = 0
function newKey() { return ++__seq }

const form = ref(emptyForm())
const contactList = ref<ContactRow[]>([])

// 开票信息行 (v0.5.8.9)
interface InvoiceRow {
  __key: number
  id?: number
  invoice_type: 'general' | 'special' | 'electronic' | string
  company_name: string
  tax_no: string
  register_address: string
  register_phone: string
  bank_name: string
  bank_account: string
  is_default: boolean
  remark: string
  isNew: boolean
  isRemoved: boolean
}
const invoiceList = ref<InvoiceRow[]>([])

function emptyForm() {
  return {
    name: '',
    industry: '',
    category: '',
    source: '',
    status: 'active',
    province: '',
    city: '',
    district: '',
    address: '',
    tags: [] as string[],
    description: '',
  }
}

const commonTags = ['重点客户', '战略合作', '续约客户', '回款及时', '待跟进', '需高层维护']

// 联系人电话校验 (动态校验每一行)
function validateContactPhone(_r: any, value: any, cb: any) {
  if (!value || !value.trim()) {
    return cb(new Error('电话不能为空'))
  }
  if (!/^[\d\-+\s()]{5,}$/.test(value)) {
    return cb(new Error('电话格式不正确'))
  }
  cb()
}

const rules: FormRules = {
  name: [
    { required: true, message: '客户名称不能为空', trigger: 'blur' },
    { max: 128, message: '最长 128 字符', trigger: 'blur' },
  ],
  category: [{ required: true, message: '请选择客户分类', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  province: [{ max: 32, message: '最长 32 字符', trigger: 'blur' }],
  city: [{ max: 32, message: '最长 32 字符', trigger: 'blur' }],
  district: [{ max: 32, message: '最长 32 字符', trigger: 'blur' }],
  address: [{ max: 255, message: '最长 255 字符', trigger: 'blur' }],
}

function newEmptyInvoice(): InvoiceRow {
  return {
    __key: newKey(),
    invoice_type: 'general',
    company_name: '',
    tax_no: '',
    register_address: '',
    register_phone: '',
    bank_name: '',
    bank_account: '',
    is_default: false,
    remark: '',
    isNew: true,
    isRemoved: false,
  }
}

// 同步 customer → form + contactList + invoiceList
function syncFromCustomer() {
  const c = props.customer
  if (!c || !c.id) {
    form.value = emptyForm()
    contactList.value = []
    invoiceList.value = []
    return
  }
  form.value = {
    name: c.name || '',
    industry: c.industry || '',
    category: c.category || 'normal',
    source: c.source || '',
    status: c.status || 'active',
    province: c.province || '',
    city: c.city || '',
    district: c.district || '',
    address: c.address || '',
    tags: Array.isArray(c.tags) ? [...c.tags] : [],
    description: c.description || '',
  }
  // 联系人按 is_primary desc, id asc 排
  const sorted = (c.contacts || [])
    .slice()
    .sort((a, b) => {
      if (a.is_primary && !b.is_primary) return -1
      if (!a.is_primary && b.is_primary) return 1
      return a.id - b.id
    })
  contactList.value = sorted.length
    ? sorted.map((x) => ({
        __key: newKey(),
        id: x.id,
        name: x.name || '',
        position: x.position || '',
        phone: x.phone || '',
        is_primary: !!x.is_primary,
        isNew: false,
        isRemoved: false,
      }))
    : [{ __key: newKey(), name: '', position: '', phone: '', is_primary: true, isNew: true, isRemoved: false }]

  // 开票信息 (v0.5.8.9)
  const sortedInv = (c.invoice_infos || [])
    .slice()
    .sort((a, b) => {
      if (a.is_default && !b.is_default) return -1
      if (!a.is_default && b.is_default) return 1
      return a.id - b.id
    })
  invoiceList.value = sortedInv.map((x) => ({
    __key: newKey(),
    id: x.id,
    invoice_type: x.invoice_type || 'general',
    company_name: x.company_name || '',
    tax_no: x.tax_no || '',
    register_address: x.register_address || '',
    register_phone: x.register_phone || '',
    bank_name: x.bank_name || '',
    bank_account: x.bank_account || '',
    is_default: !!x.is_default,
    remark: x.remark || '',
    isNew: false,
    isRemoved: false,
  }))
}

function addContact() {
  contactList.value.push({
    __key: newKey(),
    name: '',
    position: '',
    phone: '',
    is_primary: false,
    isNew: true,
    isRemoved: false,
  })
}

function addInvoice() {
  invoiceList.value.push(newEmptyInvoice())
}

function removeInvoice(idx: number) {
  const row = invoiceList.value[idx]
  if (row.id && !row.isNew) {
    row.isRemoved = true
  } else {
    invoiceList.value.splice(idx, 1)
  }
}

function onDefaultChange(changedIdx: number) {
  // 单选默认: 选了就把其他清掉
  if (invoiceList.value[changedIdx].is_default) {
    invoiceList.value.forEach((row, i) => {
      if (i !== changedIdx) row.is_default = false
    })
  }
}

function removeContact(idx: number) {
  const row = contactList.value[idx]
  if (row.id && !row.isNew) {
    row.isRemoved = true
  } else {
    contactList.value.splice(idx, 1)
  }
  // 确保至少一个可见的联系人
  const visibleRows = contactList.value.filter((r) => !r.isRemoved)
  if (!visibleRows.length) {
    contactList.value.unshift({
      __key: newKey(),
      name: '',
      position: '',
      phone: '',
      is_primary: true,
      isNew: true,
      isRemoved: false,
    })
  }
}

// 每次打开时同步
watch(
  () => props.modelValue,
  (v) => {
    if (v) {
      syncFromCustomer()
      nextTick(() => formRef.value?.clearValidate())
    }
  },
)

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  // 手动验证每一行联系人的电话
  for (let i = 0; i < contactList.value.length; i++) {
    const r = contactList.value[i]
    if (r.isRemoved) continue
    if (!r.phone || !r.phone.trim()) {
      ElMessage.warning(`联系人 ${i + 1} 的电话不能为空`)
      return
    }
    if (!/^[\d\-+\s()]{5,}$/.test(r.phone)) {
      ElMessage.warning(`联系人 ${i + 1} 的电话格式不正确`)
      return
    }
  }
  // 手动验证每一行开票信息 (v0.5.8.9)
  for (let i = 0; i < invoiceList.value.length; i++) {
    const r = invoiceList.value[i]
    if (r.isRemoved) continue
    if (!r.company_name || !r.company_name.trim()) {
      ElMessage.warning(`开票信息 ${i + 1} 的「单位名称」不能为空`)
      return
    }
    if (!r.tax_no || !r.tax_no.trim()) {
      ElMessage.warning(`开票信息 ${i + 1} 的「税号」不能为空`)
      return
    }
  }

  submitting.value = true
  try {
    const customerId = props.customer.id

    // 1) 主表更新 (不带 contact/phone, 由联系人 API 接管)
    const payload: Record<string, any> = {
      name: form.value.name.trim(),
      industry: form.value.industry || null,
      category: form.value.category || null,
      source: form.value.source || null,
      status: form.value.status,
      province: form.value.province || '',
      city: form.value.city || '',
      district: form.value.district || '',
      address: form.value.address || '',
      tags: form.value.tags.length ? form.value.tags : null,
      description: form.value.description || null,
    }
    await put(`/customers/${customerId}`, payload)

    // 2) 联系人 diff 同步
    for (const r of contactList.value) {
      if (r.isRemoved && r.id) {
        try {
          await del(`/customers/${customerId}/contacts/${r.id}`)
        } catch (e: any) {
          console.warn('删除联系人失败', r.id, e)
        }
      }
    }
    const visibleRows = contactList.value.filter((r) => !r.isRemoved)
    const primaryIdx = 0
    for (let i = 0; i < visibleRows.length; i++) {
      const r = visibleRows[i]
      const body = {
        name: r.name || '',
        position: r.position || null,
        phone: r.phone,
        is_primary: i === primaryIdx,
      }
      if (r.isNew || !r.id) {
        await post(`/customers/${customerId}/contacts`, body)
      } else {
        await put(`/customers/${customerId}/contacts/${r.id}`, body)
      }
    }

    // 3) 开票信息 diff 同步 (v0.5.8.9)
    for (const r of invoiceList.value) {
      if (r.isRemoved && r.id) {
        try {
          await del(`/customers/${customerId}/invoice-infos/${r.id}`)
        } catch (e: any) {
          console.warn('删除开票信息失败', r.id, e)
        }
      }
    }
    for (const r of invoiceList.value) {
      if (r.isRemoved) continue
      const body: Record<string, any> = {
        invoice_type: r.invoice_type || 'general',
        company_name: r.company_name.trim(),
        tax_no: r.tax_no.trim(),
        register_address: r.register_address || null,
        register_phone: r.register_phone || null,
        bank_name: r.bank_name || null,
        bank_account: r.bank_account || null,
        is_default: !!r.is_default,
        remark: r.remark || null,
      }
      if (r.isNew || !r.id) {
        await post(`/customers/${customerId}/invoice-infos`, body)
      } else {
        await put(`/customers/${customerId}/invoice-infos/${r.id}`, body)
      }
    }

    ElMessage.success('客户信息已更新')
    emit('saved')
    handleClose()
  } catch (e: any) {
    const msg = e?.response?.data?.message || e?.message || '保存失败'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  visible.value = false
}
</script>

<style lang="scss" scoped>
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #0c447c;
  margin: 4px 0 16px;
  padding-left: 10px;
  border-left: 3px solid #0c447c;
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.section-hint {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.contact-row,
.invoice-row {
  margin-bottom: 8px;
  align-items: flex-start;
}

.contact-row__fields,
.invoice-row__fields {
  display: flex;
  gap: 8px;
  align-items: center;
  width: 100%;
  flex-wrap: wrap;
}

.invoice-row__extra {
  display: flex;
  gap: 8px;
  align-items: center;
  width: 100%;
  margin-top: 6px;
  flex-wrap: wrap;

  .extra-cell {
    flex: 1;
    min-width: 180px;
  }
}
</style>
