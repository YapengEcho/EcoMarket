<template>
  <div class="my-items">
    <div class="page-header">
      <p class="page-eyebrow">我的商品</p>
      <h1 class="page-title">我发布的<span class="title-accent">闲置</span></h1>
    </div>

    <div class="table-card" v-loading="loading">
      <el-table :data="items" stripe>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column label="价格" width="120">
          <template #default="{ row }">
            <span class="cell-price">¥{{ formatPrice(row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览" width="80" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/item/${row.item_id}`)">查看</el-button>
            <el-button size="small" type="danger" @click="del(row.item_id)">下架</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && items.length === 0" class="empty">
        <span class="empty-mark">◐</span>
        <p>还没发布过商品</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { itemsApi } from '@/api/items'
import { formatPrice, statusText, statusTagType } from '@/utils/format'

const items = ref<any[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await itemsApi.myItems()
    items.value = res.data.data
  } finally {
    loading.value = false
  }
}

async function del(id: number) {
  await ElMessageBox.confirm('确定下架此商品？', '提示', { type: 'warning' })
  await itemsApi.remove(id)
  ElMessage.success('已下架')
  load()
}

onMounted(load)
</script>

<style scoped>
.my-items {
  max-width: 1000px;
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

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 8px;
  min-height: 300px;
}

.cell-price {
  font-family: var(--font-body);
  font-weight: 700;
  color: var(--accent);
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-muted);
}

.empty-mark {
  font-family: var(--font-body);
  font-size: 48px;
  color: var(--border-strong);
}
</style>
