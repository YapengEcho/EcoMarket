<template>
  <div class="admin-page">
    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="review_id" label="ID" width="70" align="center" />
      <el-table-column prop="reviewer_name" label="评价者" width="120" />
      <el-table-column prop="reviewee_id" label="被评价者ID" width="120" align="center" />
      <el-table-column label="评分" width="200" align="center">
        <template #default="{ row }">
          <el-rate :model-value="row.rating" disabled size="small" show-score />
        </template>
      </el-table-column>
      <el-table-column prop="comment" label="评价内容" min-width="250" show-overflow-tooltip />
      <el-table-column prop="created_at" label="评价时间" width="170" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function load() {
  loading.value = true
  try {
    const res = await adminApi.listReviews(page.value, pageSize)
    list.value = res.data.data.items
    total.value = res.data.data.total
  } finally {
    loading.value = false
  }
}

async function del(row: any) {
  await ElMessageBox.confirm('确定要删除这条评价吗？', '删除', { type: 'warning' })
  await adminApi.deleteReview(row.review_id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.admin-page { background: #fff; padding: 20px; border-radius: 8px; }
</style>
