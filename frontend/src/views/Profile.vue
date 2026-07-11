<template>
  <div class="profile">
    <div class="page-header">
      <p class="page-eyebrow">个人中心</p>
      <h1 class="page-title">账户<span class="title-accent">信息</span></h1>
    </div>

    <div class="profile-grid">
      <!-- 左：信息卡片 -->
      <div class="info-card" v-if="user">
        <div class="avatar-block">
          <span class="avatar">{{ user.username.charAt(0).toUpperCase() }}</span>
          <div>
            <h2 class="user-name">{{ user.username }}</h2>
            <p class="user-school">{{ user.school || '未设置学校' }}</p>
          </div>
        </div>

        <div class="info-list">
          <div class="info-row">
            <span class="info-label">邮箱</span>
            <span class="info-value">{{ user.email || '未设置' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">信誉分</span>
            <span class="info-value">
              <span class="score">{{ user.reputation_score?.toFixed(2) || '5.00' }}</span>
              <span class="score-max">/ 5.00</span>
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">注册时间</span>
            <span class="info-value">{{ user.created_at?.slice(0, 10) }}</span>
          </div>
        </div>
      </div>

      <!-- 右：修改表单 -->
      <div class="form-card">
        <h3 class="form-title">修改资料</h3>
        <div class="field">
          <label class="field-label">邮箱</label>
          <el-input v-model="form.email" placeholder="填写邮箱" size="large" />
        </div>
        <div class="field">
          <label class="field-label">学校</label>
          <el-input v-model="form.school" placeholder="填写学校" size="large" />
        </div>
        <button class="btn-save" @click="save">保存修改</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import type { User } from '@/types'

const authStore = useAuthStore()
const user = ref<User | null>(null)
const form = reactive({ email: '', school: '' })

async function load() {
  user.value = await authStore.fetchProfile()
  form.email = user.value?.email || ''
  form.school = user.value?.school || ''
}

async function save() {
  await authApi.updateMe({ email: form.email, school: form.school })
  ElMessage.success('保存成功')
  load()
}

onMounted(load)
</script>

<style scoped>
.profile {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-eyebrow {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 8px;
}

.page-title {
  font-family: var(--font-body);
  font-size: 36px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.title-accent {
  font-style: italic;
  font-weight: 300;
  color: var(--accent);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* 信息卡片 */
.info-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.avatar-block {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  font-size: 24px;
  font-weight: 700;
}

.user-name {
  font-family: var(--font-body);
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.user-school {
  font-size: 13px;
  color: var(--text-muted);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 14px;
  color: var(--text-secondary);
}

.score {
  font-family: var(--font-body);
  font-size: 20px;
  font-weight: 700;
  color: var(--color-success);
}

.score-max {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}


/* 表单卡片 */
.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-title {
  font-family: var(--font-body);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.btn-save {
  margin-top: 8px;
  font-family: var(--font-body);
  font-size: 15px;
  font-weight: 600;
  color: var(--bg-base);
  background: var(--accent);
  border: none;
  padding: 14px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-save:hover {
  background: #ff8d3a;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
