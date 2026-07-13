<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapse }">
      <div class="sidebar-logo" @click="$router.push('/admin/dashboard')">
        <span v-if="!isCollapse" class="logo-text">EcoMarket</span>
        <span v-else class="logo-mini">EM</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :router="true"
        class="sidebar-menu"
        background-color="#001529"
        text-color="#b7bdc6"
        active-text-color="#fff"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/items">
          <el-icon><Goods /></el-icon>
          <template #title>商品管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/categories">
          <el-icon><Files /></el-icon>
          <template #title>分类管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/transactions">
          <el-icon><List /></el-icon>
          <template #title>交易管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/reviews">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>评价管理</template>
        </el-menu-item>

        <el-menu-item index="/admin/messages">
          <el-icon><Message /></el-icon>
          <template #title>消息管理</template>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- 右侧主体 -->
    <div class="main">
      <!-- 顶栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">管理后台</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-chip">
              <span class="user-avatar">{{ authStore.username.charAt(0).toUpperCase() }}</span>
              <span>{{ authStore.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home">回到首页</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import {
  Odometer, User, Goods, List, ChatDotRound, Message, Fold, Expand, Files,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const pageTitleMap: Record<string, string> = {
  '/admin/dashboard': '工作台',
  '/admin/users': '用户管理',
  '/admin/items': '商品管理',
  '/admin/categories': '分类管理',
  '/admin/transactions': '交易管理',
  '/admin/reviews': '评价管理',
  '/admin/messages': '消息管理',
}

const currentPageTitle = computed(() => {
  for (const key of Object.keys(pageTitleMap)) {
    if (route.path.startsWith(key)) return pageTitleMap[key]
  }
  return '管理后台'
})

function handleCommand(cmd: string) {
  if (cmd === 'home') router.push('/')
  else if (cmd === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  background: #001529;
  transition: width 0.3s;
  flex-shrink: 0;
}
.sidebar.collapsed {
  width: 64px;
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.logo-mini {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

.sidebar-menu {
  border-right: none !important;
}
.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* 主体 */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #f5f7fa;
}

/* 顶栏 */
.topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
}
.collapse-btn:hover {
  color: var(--accent);
}

.topbar-right {
  margin-left: auto;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px 4px 4px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
}
.user-chip:hover {
  border-color: var(--border-strong);
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

/* 内容区 */
.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
