import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getToken, setToken, clearAuth, getUserInfo, setUserInfo } from '@/utils/auth'
import { post, get } from '@/utils/request'
import { usePermissionStore } from '@/utils/permission'
import router from '@/router'

// Mock 用户数据（演示用）
const MOCK_USERS: Record<string, { password: string; user: any; permissions: string[]; roles: string[] }> = {
  admin: {
    password: 'admin123',
    user: { id: 1, username: 'admin', name: '张建国', avatar: '', department: '总经办', position: '总经理', phone: '13800138000', email: 'admin@security-oa.com' },
    permissions: ['*'],
    roles: ['admin']
  },
  manager: {
    password: '123456',
    user: { id: 2, username: 'manager', name: '李明辉', avatar: '', department: '技术部', position: '项目经理', phone: '13900139001', email: 'manager@security-oa.com' },
    permissions: ['project', 'service', 'employee', 'attendance', 'customer', 'expense', 'vehicle', 'inventory', 'finance', 'disk', 'knowledge', 'message'],
    roles: ['manager']
  },
  user: {
    password: '123456',
    user: { id: 3, username: 'user', name: '王小红', avatar: '', department: '售后部', position: '维修工程师', phone: '13700137002', email: 'user@security-oa.com' },
    permissions: ['service', 'attendance', 'message'],
    roles: ['user']
  }
}

// 是否启用 Mock 模式（无后端时设为 true）
const USE_MOCK = false

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(getToken() || '')
  const userInfo = ref<any>(getUserInfo() || null)
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])

  // 登录
  async function login(loginForm: { username: string; password: string }) {
    if (USE_MOCK) {
      // Mock 模式登录
      const mockUser = MOCK_USERS[loginForm.username]
      if (!mockUser || mockUser.password !== loginForm.password) {
        throw new Error('用户名或密码错误')
      }
      token.value = 'mock-token-' + Date.now()
      setToken(token.value)
      userInfo.value = mockUser.user
      permissions.value = mockUser.permissions
      roles.value = mockUser.roles
      setUserInfo(mockUser.user)
      return
    }
    const res: any = await post('/auth/login', loginForm)
    // axios 拦截器已解包 {code,message,data} → res = {token, user, ...}
    token.value = res.token
    setToken(res.token)
    if (res.user) {
      userInfo.value = res.user
      // V0.5.0: 同步从 /auth/me 拉 roles (后端 user 结构不含 roles)
      try {
        const me: any = await get('/auth/me')
        if (me?.roles) {
          userInfo.value.roles = me.roles
        }
        if (me?.user) {
          Object.assign(userInfo.value, me.user)
        }
      } catch (e) {
        // ignore — fallback username prefix
      }
      setUserInfo(userInfo.value)
      // 触发 permission store 加载
      const permStore = usePermissionStore()
      permStore.reset()
      await permStore.load()
    }
    return res
  }

  // 获取用户信息
  async function getUserInfoAction() {
    if (USE_MOCK) return // Mock 模式已在 login 中设置
    const res: any = await get('/auth/userinfo')
    userInfo.value = res.user
    permissions.value = res.permissions || []
    roles.value = res.roles || []
    setUserInfo(res.user)
    return res
  }

  // 退出登录
  async function logout() {
    try {
      await post('/auth/logout')
    } finally {
      clearAuth()
      token.value = ''
      userInfo.value = null
      permissions.value = []
      roles.value = []
      router.push('/login')
    }
  }

  // 检查权限
  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission)
  }

  function hasRole(role: string): boolean {
    return roles.value.includes(role)
  }

  return {
    token,
    userInfo,
    permissions,
    roles,
    login,
    getUserInfoAction,
    logout,
    hasPermission,
    hasRole
  }
})
