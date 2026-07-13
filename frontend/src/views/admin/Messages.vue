<template>
  <div class="admin-page">
    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="msg_id" label="ID" width="70" align="center" />
      <el-table-column prop="sender_name" label="发送者" width="120" />
      <el-table-column prop="receiver_id" label="接收者ID" width="100" align="center" />
      <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" min-width="250" show-overflow-tooltip />
      <el-table-column prop="item_id" label="关联商品" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.item_id">#{{ row.item_id }}</span>
          <span v-else style="color: #999">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="发送时间" width="170" />
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="load"
      style="margin-top: 16px; justify-content: flex-end"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function load() {
  loading.value = true
  try {
    const res = await adminApi.listMessages(page.value, pageSize)
    list.value = res.data.data.items
    total.value = res.data.data.total
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.admin-page { background: #fff; padding: 20px; border-radius: 8px; }
</style>
