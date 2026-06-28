/**
 * V0.5.3 L1+L2 frontend authorization (FIXED)
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserInfo } from './auth'
import http from './request'

export const usePermissionStore = defineStore('permission', () => {
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])
  const loaded = ref(false)

  async function load() {
    if (loaded.value) return
    try {
      const user = getUserInfo()
      if (user && Array.isArray(user.roles)) {
        roles.value = user.roles
      }

      const res: any = await http.get('/permissions/my')
      const list = Array.isArray(res) ? res : (res?.data || [])
      permissions.value = list.map((p: any) => typeof p === 'string' ? p : p.name).filter(Boolean)

      // V0.5.3 FIX: extract roles from response if not already set
      if (roles.value.length === 0) {
        if (res?.roles && Array.isArray(res.roles)) {
          roles.value = res.roles
        }
        const userInfo = getUserInfo()
        if (userInfo?.roles && Array.isArray(userInfo.roles)) {
          roles.value = userInfo.roles
        }
      }

      loaded.value = true
    } catch (e) {
      console.warn('Permission load failed:', e)
      permissions.value = []
      loaded.value = true
    }
  }

  function hasPermission(perm: string): boolean {
    if (roles.value.includes('admin')) return true
    return permissions.value.includes(perm)
  }

  function hasAnyPermission(perms: string[]): boolean {
    if (roles.value.includes('admin')) return true
    return perms.some(p => permissions.value.includes(p))
  }

  function reset() {
    permissions.value = []
    roles.value = []
    loaded.value = false
  }

  return { permissions, roles, loaded, load, hasPermission, hasAnyPermission, reset }
})

export function hasPermission(perm: string): boolean {
  const store = usePermissionStore()
  return store.hasPermission(perm)
}

export const permissionDirective = {
  mounted(el: HTMLElement, binding: { value: string | string[]; modifiers?: Record<string, boolean> }) {
    applyPermission(el, binding)
  },
  updated(el: HTMLElement, binding: { value: string | string[]; modifiers?: Record<string, boolean> }) {
    applyPermission(el, binding)
  },
}

function applyPermission(el: HTMLElement, binding: { value: string | string[]; modifiers?: Record<string, boolean> }) {
  const { value, modifiers } = binding
  const perms = Array.isArray(value) ? value : [value]
  const store = usePermissionStore()

  if (store.roles.includes('admin')) return

  if (!store.loaded) {
    const checkLater = () => {
      if (store.roles.includes('admin')) return
      const isOrMode = modifiers?.or
      const has = isOrMode
        ? perms.some(p => store.permissions.includes(p))
        : perms.every(p => store.permissions.includes(p))
      if (!has) {
        el.style.display = 'none'
        el.setAttribute('aria-hidden', 'true')
      }
    }
    const unwatch = store.$subscribe(() => {
      if (store.loaded) {
        checkLater()
        unwatch()
      }
    })
    setTimeout(() => {
      checkLater()
      unwatch()
    }, 2000)
    return
  }

  const isOrMode = modifiers?.or
  const has = isOrMode
    ? perms.some(p => store.permissions.includes(p))
    : perms.every(p => store.permissions.includes(p))

  if (!has) {
    el.style.display = 'none'
    el.setAttribute('aria-hidden', 'true')
  } else {
    el.style.display = ''
    el.removeAttribute('aria-hidden')
  }
}
