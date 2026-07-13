<template>
  <div class="admin-page">
    <div class="page-toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索用户名/邮箱/学校"
        clearable
        style="width: 280px"
        @keyup.enter="search"
      >
        <template #append>
          <el-button :icon="Search" @click="search" />
        </template>
      </el-input>
    </div>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="user_id" label="ID" width="70" align="center" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="school" label="学校" min-width="140" />
      <el-table-column label="信誉分" width="100" align="center">
        <template #default="{ row }">
          <span style="color: #f5a623">★ {{ Number(row.reputation_score).toFixed(1) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_admin" type="danger">管理员</el-tag>
          <el-tag v-else type="success">普通用户</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '正常' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="170" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            :type="row.is_active ? 'danger' : 'success'"
            @click="toggleStatus(row)"
            :disabled="row.user_id === 1"
          >
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" @click="openReset(row)">重置密码</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="load"
      style="margin-top: 16px; justify-content: flex-end"
    />

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="resetVisible" title="重置密码" width="400px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <span>{{ currentUser?.username }}</span>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="newPassword" type="password" show-password placeholder="输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetVisible = false">取消</el-button>
        <el-button type="primary" @click="doReset">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const keyword = ref('')

const resetVisible = ref(false)
const currentUser = ref<any>(null)
const newPassword = ref('')

async function load() {
  loading.value = true
  try {
    const res = await adminApi.listUsers(page.value, pageSize, keyword.value)
    list.value = res.data.data.items
    total.value = res.data.data.total
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  load()
}

async function toggleStatus(row: any) {
  await ElMessageBox.confirm(
    `确定要${row.is_active ? '禁用' : '启用'}用户「${row.username}」吗？`,
    '提示',
    { type: 'warning' }
  )
  await adminApi.updateUserStatus(row.user_id, !row.is_active)
  ElMessage.success('操作成功')
  load()
}

function openReset(row: any) {
  currentUser.value = row
  newPassword.value = ''
  resetVisible.value = true
}

async function doReset() {
  if (!newPassword.value || newPassword.value.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  await adminApi.resetUserPassword(currentUser.value.user_id, newPassword.value)
  ElMessage.success('密码已重置')
  resetVisible.value = false
}

onMounted(load)
</script>

<style scoped>
.admin-page {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

.page-toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}
</style>
