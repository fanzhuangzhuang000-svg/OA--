<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '240px'" class="sidebar">
      <div class="logo" @click="router.push('/')">
        <div class="logo-icon">OA</div>
        <transition name="fade">
          <span v-if="!appStore.sidebarCollapsed" class="logo-text">{{ systemConfigStore.shortName }}</span>
        </transition>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="appStore.sidebarCollapsed"
          :collapse-transition="false"
          router
          background-color="#0C447C"
          text-color="rgba(255,255,255,0.75)"
          active-text-color="#fff"
        >
          <template v-for="route in menuRoutes" :key="route.path">
            <!-- 有子菜单 -->
            <el-sub-menu v-if="route.children && route.children.length > 1" :index="route.path">
              <template #title>
                <el-icon v-if="route.meta?.icon"><component :is="route.meta.icon" /></el-icon>
                <span>{{ route.meta?.title }}</span>
              </template>
              <el-menu-item
                v-for="child in route.children"
                :key="child.path"
                :index="`/${route.path}/${child.path}`"
              >
                <el-icon v-if="child.meta?.icon"><component :is="child.meta.icon" /></el-icon>
                <template #title>{{ child.meta?.title }}</template>
              </el-menu-item>
            </el-sub-menu>
            <!-- 单个菜单项（含1个子项或无子项） -->
            <el-menu-item v-else :index="getMenuIndex(route)">
              <el-icon v-if="route.meta?.icon"><component :is="route.meta.icon" /></el-icon>
              <template #title>{{ route.meta?.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <!-- 侧边栏底部：版本号 + 版权 -->
      <div class="sidebar-footer" :class="{ 'is-collapsed': appStore.sidebarCollapsed }">
        <div class="sidebar-footer-version">v1.0.1</div>
        <div class="sidebar-footer-copyright">© 2026 宁波初阳信息技术有限公司</div>
      </div>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-container class="right-container">
      <!-- 顶栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
            <component :is="appStore.sidebarCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              <span :class="{ 'is-link': item.path }" @click="item.path && router.push(item.path)">
                {{ item.title }}
              </span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <!-- 搜索 -->
          <el-tooltip content="全局搜索" placement="bottom">
            <el-icon class="header-action"><Search /></el-icon>
          </el-tooltip>
          <!-- 消息 -->
          <el-tooltip content="消息中心" placement="bottom">
            <el-badge :value="unreadCount" :max="99" :hidden="unreadCount === 0" class="header-action">
              <el-icon class="header-action__icon" @click="goToMessage"><Bell /></el-icon>
            </el-badge>
          </el-tooltip>
          <!-- 全屏 -->
          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="header-action" @click="toggleFullscreen"><FullScreen /></el-icon>
          </el-tooltip>
          <!-- 用户下拉 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.userInfo?.name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="user-name">{{ userStore.userInfo?.name || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item command="password">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <keep-alive :include="cachedViews">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- V0.5.7 块6 — PWA 安装提示 (右下角) -->
    <PwaInstallBanner />

    <!-- 移动端访问提示 -->
    <el-dialog
      v-model="deviceCheck.dialogVisible.value"
      title="请使用 PC 端访问"
      width="420px"
      :close-on-click-modal="false"
      :show-close="true"
      @close="deviceCheck.closeDialog"
    >
      <div class="mobile-dialog">
        <el-icon :size="48" color="#BA7517"><Warning /></el-icon>
        <p>检测到您正在使用移动设备访问本系统。</p>
        <p>为获得最佳体验,请使用 <strong>PC 浏览器(Chrome/Edge)1920×1080</strong> 以上分辨率访问。</p>
        <p class="mobile-dialog__tip">移动端适配版本正在规划中,敬请期待。</p>
      </div>
      <template #footer>
        <el-button @click="deviceCheck.closeDialog">我知道了</el-button>
        <el-button type="primary" @click="deviceCheck.closeDialog">继续访问</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { computed, watch, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useSystemConfigStore } from '@/stores/systemConfig'
import { ElMessageBox } from 'element-plus'
import { get as httpGet } from '@/utils/request'
import { useDeviceCheck } from '@/composables/useDeviceCheck'
import PwaInstallBanner from '@/components/PwaInstallBanner.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const systemConfigStore = useSystemConfigStore()
const cachedViews = ref<string[]>([])

// 移动端检测
const deviceCheck = useDeviceCheck()

// 动态页面标题
function updateDocumentTitle() {
  const baseTitle = systemConfigStore.sysConfig.systemName || '安防运维OA办公系统'
  document.title = baseTitle
}
onMounted(updateDocumentTitle)
watch(() => systemConfigStore.sysConfig.systemName, updateDocumentTitle)

// ========== 顶栏消息红点 ==========
const unreadCount = ref(0)
let unreadTimer: any

async function loadUnreadCount() {
  try {
    const res: any = await httpGet('/notifications/unread-count')
    // 解包后 res = {count: 3}
    if (res && typeof res === 'object' && 'count' in res) {
      unreadCount.value = Number(res.count) || 0
    }
  } catch (e) { /* 未登录时静默 */ }
}

function goToMessage() {
  // 跳到消息中心（路由已配 alias '/message'）
  router.push('/message')
}

onMounted(() => {
  loadUnreadCount()
  // 每 60s 拉一次
  unreadTimer = setInterval(loadUnreadCount, 60000)
})

// 侧边栏菜单路由（过滤掉隐藏的）
const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find(r => r.path === '/')
  return (mainRoute?.children || [])
    .filter(item => item.meta?.title)
    .map(item => ({
      ...item,
      children: (item.children || []).filter(c => c.meta?.title && !c.meta?.hidden)
    }))
})

// 当前激活菜单
const activeMenu = computed(() => {
  return route.path
})

// 面包屑
const breadcrumbs = computed(() => {
  const crumbs: { path: string; title: string }[] = [{ path: '', title: '首页' }]
  const matched = route.matched.filter(item => item.meta?.title)
  matched.forEach(item => {
    crumbs.push({ path: item.path, title: item.meta.title as string })
  })
  return crumbs
})

// 菜单索引（处理只有1个子路由的情况）
function getMenuIndex(route: any): string {
  if (route.children?.length === 1) {
    return `/${route.path}/${route.children[0].path}`
  }
  return `/${route.path}`
}

// 全屏切换
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 用户下拉命令
function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/settings/profile')
      break
    case 'password':
      router.push('/settings/password')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        userStore.logout()
      })
      break
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #0C447C;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .logo {
    height: 56px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    cursor: pointer;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    flex-shrink: 0;

    .logo-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #1D9E75, #7fdbca);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 16px;
      font-weight: 700;
      flex-shrink: 0;
    }

    .logo-text {
      color: white;
      font-size: 16px;
      font-weight: 600;
      margin-left: 12px;
      white-space: nowrap;
    }
  }

  :deep(.el-menu) {
    border-right: none;
    padding: 8px 0;

    .el-menu-item {
      margin: 2px 8px;
      border-radius: 6px;
      height: 44px;
      line-height: 44px;

      &.is-active {
        background: linear-gradient(135deg, rgba(29,158,117,0.3), rgba(29,158,117,0.15)) !important;
        position: relative;

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 20px;
          background: #1D9E75;
          border-radius: 0 2px 2px 0;
        }
      }

      &:hover {
        background: rgba(255,255,255,0.08) !important;
      }
    }

    .el-sub-menu {
      .el-sub-menu__title {
        margin: 2px 8px;
        border-radius: 6px;
        height: 44px;
        line-height: 44px;

        &:hover {
          background: rgba(255,255,255,0.08) !important;
        }
      }
    }
  }

  .sidebar-footer {
    flex-shrink: 0;
    padding: 10px 12px;
    border-top: 1px solid rgba(255,255,255,0.08);
    background: rgba(0,0,0,0.08);
    color: rgba(255,255,255,0.55);
    line-height: 1.4;
    transition: padding 0.3s ease;
  }

  .sidebar-footer-version {
    font-size: 12px;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.4px;
  }

  .sidebar-footer-copyright {
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sidebar-footer.is-collapsed {
    padding: 10px 4px;
    text-align: center;

    .sidebar-footer-copyright {
      display: none;
    }
  }
}

.right-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 56px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  z-index: 10;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: #606266;
      transition: color 0.3s;

      &:hover {
        color: #0C447C;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 8px;

    .header-action {
      font-size: 18px;
      cursor: pointer;
      color: #606266;
      padding: 8px;
      border-radius: 6px;
      transition: all 0.3s;
      display: inline-flex;
      align-items: center;

      &:hover {
        background: #f5f7fa;
        color: #0C447C;
      }

      &__icon {
        cursor: pointer;
        font-size: 18px;
        &:hover { color: #0C447C; }
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 12px 4px 4px;
      border-radius: 20px;
      transition: background 0.3s;
      margin-left: 8px;

      &:hover {
        background: #f5f7fa;
      }

      .user-avatar {
        background: linear-gradient(135deg, #0C447C, #1D9E75);
        color: white;
        font-size: 14px;
      }

      .user-name {
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
  padding: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}
.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

.mobile-dialog {
  text-align: center;
  padding: 8px 0;
  .el-icon { margin-bottom: 16px; }
  p { margin: 8px 0; color: #606266; line-height: 1.6; }
  strong { color: #0C447C; }
  &__tip {
    margin-top: 16px;
    padding: 8px 12px;
    background: #fdf6ec;
    border-radius: 4px;
    color: #BA7517;
    font-size: 13px;
  }
}
</style>
