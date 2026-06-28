<template>
  <el-container class="main-layout">
    <!-- 全局背景效果 -->
    <ParticleBackground />
    <MouseGlow />

    <!-- 侧边栏 -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '240px'" class="sidebar">
      <div class="logo" @click="router.push('/')">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
        </div>
        <transition name="fade">
          <span v-if="!appStore.sidebarCollapsed" class="logo-text">
            <span class="logo-nova">NOVA</span><span class="logo-ops">OPS</span>
          </span>
        </transition>
      </div>
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="appStore.sidebarCollapsed"
          :collapse-transition="false"
          router
        >
          <template v-for="route in menuRoutes" :key="route.path">
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
            <el-menu-item v-else :index="getMenuIndex(route)">
              <el-icon v-if="route.meta?.icon"><component :is="route.meta.icon" /></el-icon>
              <template #title>{{ route.meta?.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <div class="sidebar-footer" :class="{ 'is-collapsed': appStore.sidebarCollapsed }">
        <div class="sidebar-footer-version">v2.0.0</div>
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
          <el-tooltip content="全局搜索" placement="bottom">
            <el-icon class="header-action"><Search /></el-icon>
          </el-tooltip>
          <el-tooltip content="消息中心" placement="bottom">
            <el-badge :value="unreadCount" :max="99" :hidden="unreadCount === 0" class="header-action">
              <el-icon class="header-action__icon" @click="goToMessage"><Bell /></el-icon>
            </el-badge>
          </el-tooltip>
          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="header-action" @click="toggleFullscreen"><FullScreen /></el-icon>
          </el-tooltip>
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

    <PwaInstallBanner />

    <el-dialog
      v-model="deviceCheck.dialogVisible.value"
      title="请使用 PC 端访问"
      width="420px"
      :close-on-click-modal="false"
      :show-close="true"
      @close="deviceCheck.closeDialog"
    >
      <div class="mobile-dialog">
        <el-icon :size="48" color="#ff9f0a"><Warning /></el-icon>
        <p>检测到您正在使用移动设备访问本系统。</p>
        <p>为获得最佳体验，请使用 <strong>PC 浏览器(Chrome/Edge)1920×1080</strong> 以上分辨率访问。</p>
        <p class="mobile-dialog__tip">移动端适配版本正在规划中，敬请期待。</p>
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
import ParticleBackground from '@/components/ParticleBackground.vue'
import MouseGlow from '@/components/MouseGlow.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const systemConfigStore = useSystemConfigStore()
const cachedViews = ref<string[]>([])
const deviceCheck = useDeviceCheck()

function updateDocumentTitle() {
  const baseTitle = systemConfigStore.sysConfig.systemName || 'NOVA OPS — 智能运维管理平台'
  document.title = baseTitle
}
onMounted(updateDocumentTitle)
watch(() => systemConfigStore.sysConfig.systemName, updateDocumentTitle)

const unreadCount = ref(0)
let unreadTimer: any

async function loadUnreadCount() {
  try {
    const res: any = await httpGet('/notifications/unread-count')
    if (res && typeof res === 'object' && 'count' in res) {
      unreadCount.value = Number(res.count) || 0
    }
  } catch (e) {}
}

function goToMessage() {
  router.push('/message')
}

onMounted(() => {
  loadUnreadCount()
  unreadTimer = setInterval(loadUnreadCount, 60000)
})

const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find(r => r.path === '/')
  return (mainRoute?.children || [])
    .filter(item => item.meta?.title)
    .map(item => ({
      ...item,
      children: (item.children || []).filter(c => c.meta?.title && !c.meta?.hidden)
    }))
})

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const crumbs: { path: string; title: string }[] = [{ path: '', title: '首页' }]
  const matched = route.matched.filter(item => item.meta?.title)
  matched.forEach(item => {
    crumbs.push({ path: item.path, title: item.meta.title as string })
  })
  return crumbs
})

function getMenuIndex(route: any): string {
  if (route.children?.length === 1) {
    return `/${route.path}/${route.children[0].path}`
  }
  return `/${route.path}`
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

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
@use '@/styles/variables' as *;

.main-layout {
  height: 100vh;
  overflow: hidden;
  position: relative;
}

// ========== 侧边栏 ==========
.sidebar {
  background: $bg-sidebar;
  backdrop-filter: $glass-blur;
  -webkit-backdrop-filter: $glass-blur;
  border-right: 1px solid $glass-border;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 10;

  .logo {
    height: 56px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    cursor: pointer;
    border-bottom: 1px solid $glass-border;
    flex-shrink: 0;

    .logo-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, $primary, $accent);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(10, 132, 255, 0.3);
    }

    .logo-text {
      font-size: 16px;
      font-weight: 700;
      margin-left: 12px;
      white-space: nowrap;
      letter-spacing: 1px;

      .logo-nova {
        color: #fff;
      }
      .logo-ops {
        color: rgba(255, 255, 255, 0.4);
      }
    }
  }

  :deep(.el-menu) {
    border-right: none;
    padding: 8px 0;
    background: transparent;

    .el-menu-item,
    .el-sub-menu__title {
      color: $text-secondary;
      margin: 2px 8px;
      border-radius: $radius-md;
      height: 44px;
      line-height: 44px;
      transition: $transition;

      &:hover {
        background: $glass-bg !important;
        color: $text-primary;
      }
    }

    .el-menu-item {
      &.is-active {
        background: $primary-lighter !important;
        color: $primary !important;
        position: relative;

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 20px;
          background: $primary;
          border-radius: 0 2px 2px 0;
        }
      }
    }

    .el-sub-menu {
      .el-sub-menu__title {
        &:hover {
          background: $glass-bg !important;
        }
      }
    }
  }

  .sidebar-footer {
    flex-shrink: 0;
    padding: 10px 12px;
    border-top: 1px solid $glass-border;
    background: rgba(0, 0, 0, 0.2);
    color: $text-secondary;
    line-height: 1.4;
    transition: padding 0.3s ease;
  }

  .sidebar-footer-version {
    font-size: 12px;
    font-weight: 600;
    color: $primary;
    letter-spacing: 0.4px;
  }

  .sidebar-footer-copyright {
    font-size: 11px;
    color: $text-placeholder;
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

// ========== 顶栏 ==========
.right-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 56px;
  background: $bg-header;
  backdrop-filter: $glass-blur;
  -webkit-backdrop-filter: $glass-blur;
  border-bottom: 1px solid $glass-border;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
  z-index: 10;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: $text-secondary;
      transition: $transition;
      padding: 6px;
      border-radius: $radius-sm;

      &:hover {
        color: $text-primary;
        background: $glass-bg;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 4px;

    .header-action {
      font-size: 18px;
      cursor: pointer;
      color: $text-secondary;
      padding: 8px;
      border-radius: $radius-md;
      transition: $transition;
      display: inline-flex;
      align-items: center;

      &:hover {
        background: $glass-bg;
        color: $text-primary;
      }

      &__icon {
        cursor: pointer;
        font-size: 18px;
        &:hover { color: $primary; }
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 12px 4px 4px;
      border-radius: 20px;
      transition: $transition;
      margin-left: 8px;

      &:hover {
        background: $glass-bg;
      }

      .user-avatar {
        background: linear-gradient(135deg, $primary, $accent);
        color: white;
        font-size: 14px;
      }

      .user-name {
        font-size: 14px;
        color: $text-regular;
      }
    }
  }
}

// ========== 主内容区 ==========
.main-content {
  flex: 1;
  overflow-y: auto;
  background: $bg-primary;
  padding: 0;
  position: relative;
}

// ========== 过渡动画 ==========
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

// ========== 移动端提示 ==========
.mobile-dialog {
  text-align: center;
  padding: 8px 0;
  .el-icon { margin-bottom: 16px; }
  p { margin: 8px 0; color: $text-regular; line-height: 1.6; }
  strong { color: $primary; }
  &__tip {
    margin-top: 16px;
    padding: 8px 12px;
    background: $warning-light;
    border-radius: $radius-sm;
    color: $warning;
    font-size: 13px;
  }
}

// ========== Element Plus 覆盖 ==========
:deep(.el-breadcrumb) {
  .el-breadcrumb__inner {
    color: $text-secondary;
    &.is-link:hover { color: $primary; }
  }
  .el-breadcrumb__separator { color: $text-placeholder; }
}

:deep(.el-dropdown-menu) {
  background: $bg-elevated;
  border: 1px solid $glass-border;
  border-radius: $radius-lg;
  box-shadow: $shadow-lg;

  .el-dropdown-menu__item {
    color: $text-regular;
    &:hover {
      background: $glass-bg;
      color: $text-primary;
    }
  }
}
</style>
