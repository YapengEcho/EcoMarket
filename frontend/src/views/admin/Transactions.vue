<template>
  <div class="admin-page">
    <div class="page-toolbar">
      <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="search" style="width: 140px">
        <el-option label="全部" :value="-1" />
        <el-option label="待处理" :value="0" />
        <el-option label="已接受" :value="1" />
        <el-option label="已拒绝" :value="2" />
        <el-option label="已完成" :value="3" />
      </el-select>
    </div>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="request_id" label="ID" width="70" align="center" />
      <el-table-column prop="item_title" label="商品" min-width="200" />
      <el-table-column prop="requester_name" label="买家" width="120" />
      <el-table-column prop="seller_id" label="卖家ID" width="80" align="center" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="trade_code" label="交易码" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.trade_code" style="font-family: monospace; font-weight: 600; color: #2563eb">
            {{ row.trade_code }}
          </span>
          <span v-else style="color: #999">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="message" label="附言" min-width="150" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="170" />
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
const statusFilter = ref(-1)

function statusText(s: number) {
  return ['待处理', '已接受', '已拒绝', '已完成'][s] || '未知'
}
function statusType(s: number): any {
  return ['info', 'warning', 'danger', 'success'][s] || ''
}

async function load() {
  loading.value = true
  try {
    const res = await adminApi.listTransactions(page.value, pageSize, statusFilter.value >= 0 ? statusFilter.value : undefined)
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

onMounted(load)
</script>

<style scoped>
.admin-page { background: #fff; padding: 20px; border-radius: 8px; }
.page-toolbar { margin-bottom: 16px; display: flex; gap: 12px; }
</style>
