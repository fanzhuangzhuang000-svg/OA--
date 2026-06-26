import { defineStore } from 'pinia'
import { ref, reactive, computed, watch } from 'vue'
import { get as httpGet, put as httpPut } from '@/utils/request'

/** 系统设置（标题/版权/备案号/公告/联系邮箱） */
export interface SystemSettings {
  system_name: string
  system_short_name: string
  copyright: string
  copyright_url: string
  announcement: string
  icp: string
  contact_email: string
}

const DEFAULT_SETTINGS: SystemSettings = {
  system_name: '安防运维OA办公系统',
  system_short_name: '安防OA',
  copyright: '© 2026 安防运维科技有限公司',
  copyright_url: 'https://www.example.com',
  announcement: '',
  icp: '粤ICP备2026000000号-1',
  contact_email: 'admin@example.com',
}

const STORAGE_KEY = 'oa-system-config'

function loadFromLocal(): SystemSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }
  } catch (e) { /* noop */ }
  return { ...DEFAULT_SETTINGS }
}

export const useSystemConfigStore = defineStore('systemConfig', () => {
  // 本地 reactive（用于"标题编辑"实时预览）
  const settings = reactive<SystemSettings>(loadFromLocal())

  /** 拉取后端最新设置（应用启动时调一次） */
  async function fetchSettings() {
    try {
      const res: any = await httpGet('/settings')
      // request.ts 已解包 res = {system_name, copyright, ...}
      if (res && typeof res === 'object') {
        Object.assign(settings, DEFAULT_SETTINGS, res)
        // 持久化到 localStorage 作离线缓存
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)) } catch (e) { /* noop */ }
      }
    } catch (e) {
      // 离线或未登录 — 用本地缓存
      console.warn('[systemConfig] fetch failed, use local cache', e)
    }
  }

  /** 写回后端 */
  async function saveSettings(patch: Partial<SystemSettings>): Promise<boolean> {
    try {
      Object.assign(settings, patch)
      const res: any = await httpPut('/settings', patch)
      // request.ts 拦截器已解包：res 直接是后端的 data 字段
      // 成功：res 是对象（含任意字段 — system_name/copyright/announcement/...）
      // 失败：res 会变成 undefined 或被 throw 掉
      if (res && typeof res === 'object') {
        // 同步最新值到 store + localStorage
        Object.assign(settings, res)
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)) } catch (e) { /* noop */ }
        return true
      }
      return false
    } catch (e) {
      console.error('[systemConfig] save failed', e)
      return false
    }
  }

  /** 短名称（用于侧边栏 / 大屏） */
  const shortName = computed(() => {
    const n = settings.system_short_name || settings.system_name || 'OA'
    return n.length > 8 ? n.slice(0, 8) : n
  })

  // 兼容旧字段（sysConfig.systemName）— 旧代码仍可能读
  const sysConfig = computed(() => ({
    systemName: settings.system_name,
    shortName: shortName.value,
  }))

  return {
    settings,
    sysConfig,
    shortName,
    fetchSettings,
    saveSettings,
  }
})
