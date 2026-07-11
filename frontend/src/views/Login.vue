<template>
  <div class="auth-page">
    <div class="form-wrap">
      <h1>登录</h1>
      <form @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <el-input v-model="form.username" placeholder="输入用户名" :prefix-icon="User" size="large" />
        </div>
        <div class="field">
          <label>密码</label>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="输入密码"
            :prefix-icon="Lock"
            show-password
            size="large"
          />
        </div>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width: 100%">
          登录
        </el-button>
      </form>
      <p class="form-footer">
        还没账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

async function submit() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.form-wrap {
  width: 100%;
  max-width: 360px;
}
.form-wrap h1 {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 24px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field label {
  font-size: 13px;
  color: var(--text-secondary);
}

.form-footer {
  margin-top: 20px;
  font-size: 14px;
  color: var(--text-muted);
  text-align: center;
}
.form-footer a {
  color: var(--accent);
  text-decoration: none;
}
.form-footer a:hover {
  text-decoration: underline;
}
</style>
