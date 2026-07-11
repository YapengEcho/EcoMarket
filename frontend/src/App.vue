<template>
  <div class="app-shell">
    <header class="nav-bar">
      <div class="nav-inner">
        <div class="logo" @click="$router.push('/')">EcoMarket</div>
        <nav class="nav-links">
          <router-link to="/">市集</router-link>
          <router-link v-if="authStore.token" to="/publish">发布</router-link>
          <router-link v-if="authStore.token" to="/my-items">我的商品</router-link>
          <router-link v-if="authStore.token" to="/my-orders">交易</router-link>
          <router-link v-if="authStore.token" to="/my-favorites">收藏</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin">看板</router-link>
        </nav>
        <div class="nav-right">
          <template v-if="authStore.token">
            <el-dropdown @command="handleCommand" trigger="click">
              <div class="user-chip">
                <span class="user-avatar">{{ authStore.username.charAt(0).toUpperCase() }}</span>
                <span>{{ authStore.username }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="favorites">我的收藏</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" size="small" @click="$router.push('/login')">登录</el-button>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>EcoMarket · 校园二手交易平台</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

function handleCommand(cmd: string) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'favorites') router.push('/my-favorites')
  else if (cmd === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid var(--border-subtle);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-links a {
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
}
.nav-links a:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}
.nav-links a.router-link-exact-active {
  color: var(--accent);
  font-weight: 500;
}

.nav-right {
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

/* 主内容 */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
}

/* 页脚 */
.footer {
  border-top: 1px solid var(--border-subtle);
  padding: 24px;
  text-align: center;
}
.footer p {
  font-size: 13px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .nav-inner {
    padding: 0 16px;
    gap: 16px;
  }
  .nav-links a {
    padding: 6px 8px;
    font-size: 13px;
  }
  .main-content {
    padding: 24px 16px;
  }
}
</style>
