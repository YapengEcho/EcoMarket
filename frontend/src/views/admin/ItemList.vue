<template>
  <div class="admin-page">
    <div class="page-toolbar">
      <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="search" style="width: 140px">
        <el-option label="全部" :value="-1" />
        <el-option label="在售" :value="0" />
        <el-option label="已预订" :value="1" />
        <el-option label="已售出" :value="2" />
        <el-option label="已下架" :value="3" />
      </el-select>
    </div>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="item_id" label="ID" width="70" align="center" />
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column label="价格" width="120" align="right">
        <template #default="{ row }">
          ¥{{ Number(row.price).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="seller_name" label="卖家" width="120" />
      <el-table-column label="信誉" width="100" align="center">
        <template #default="{ row }">
          <span style="color: #f5a623">★ {{ row.seller_score?.toFixed(1) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="浏览" width="80" align="center" />
      <el-table-column prop="created_at" label="发布时间" width="170" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/item/${row.item_id}`)">查看</el-button>
          <el-button
            v-if="row.status !== 0"
            size="small"
            type="success"
            @click="audit(row, 0)"
          >上架</el-button>
          <el-button
            v-if="row.status !== 3"
            size="small"
            type="warning"
            @click="audit(row, 3)"
          >下架</el-button>
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
const statusFilter = ref(-1)

function statusText(s: number) {
  return ['在售', '已预订', '已售出', '已下架'][s] || '未知'
}
function statusType(s: number): any {
  return ['success', 'warning', 'info', 'danger'][s] || ''
}

async function load() {
  loading.value = true
  try {
    const res = await adminApi.listItems(page.value, pageSize, statusFilter.value >= 0 ? statusFilter.value : undefined)
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

async function audit(row: any, status: number) {
  await ElMessageBox.confirm(
    `确定要将商品「${row.title}」${status === 0 ? '上架' : '下架'}吗？`,
    '审核',
    { type: 'warning' }
  )
  await adminApi.auditItem(row.item_id, status)
  ElMessage.success('操作成功')
  load()
}

async function del(row: any) {
  await ElMessageBox.confirm(`确定要删除商品「${row.title}」吗？此操作不可恢复`, '删除', { type: 'warning' })
  await adminApi.deleteItem(row.item_id)
  ElMessage.success('已删除')
  load()
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
