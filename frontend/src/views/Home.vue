<template>
  <div class="home">
    <!-- 标题 -->
    <section class="page-head">
      <h1>校园市集</h1>
      <p>买卖闲置，简单直接</p>
    </section>

    <!-- 筛选栏 -->
    <section class="filter-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索商品…"
        clearable
        @keyup.enter="search"
        class="search-input"
      >
        <template #append>
          <el-button :icon="Search" @click="search" />
        </template>
      </el-input>
      <el-select
        v-model="categoryId"
        placeholder="全部分类"
        clearable
        @change="search"
        class="cat-select"
      >
        <el-option v-for="c in categories" :key="c.category_id" :label="c.name" :value="c.category_id" />
      </el-select>
      <el-input-number v-model="minPrice" :min="0" placeholder="最低价" controls-position="right" class="price-input" />
      <span class="price-dash">—</span>
      <el-input-number v-model="maxPrice" :min="0" placeholder="最高价" controls-position="right" class="price-input" />
      <el-button @click="reset">重置</el-button>
    </section>

    <!-- 商品网格 -->
    <section class="items-section">
      <div class="section-header">
        <h2>最新上架</h2>
        <span class="section-count">共 {{ total }} 件</span>
      </div>

      <div v-loading="loading" class="grid">
        <ItemCard v-for="it in items" :key="it.item_id" :item="it" />
        <div v-if="!loading && items.length === 0" class="empty-state">
          <p>暂无商品</p>
        </div>
      </div>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="load"
        class="pagination"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import ItemCard from '@/components/ItemCard.vue'
import { itemsApi } from '@/api/items'
import client from '@/api/client'
import type { Item } from '@/types'

const keyword = ref('')
const categoryId = ref<number | undefined>(undefined)
const minPrice = ref<number | undefined>(undefined)
const maxPrice = ref<number | undefined>(undefined)
const items = ref<Item[]>([])
const categories = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function load() {
  loading.value = true
  try {
    const hasFilter = keyword.value || categoryId.value || minPrice.value || maxPrice.value
    let res
    if (hasFilter) {
      res = await itemsApi.search({
        keyword: keyword.value || undefined,
        category_id: categoryId.value,
        min_price: minPrice.value,
        max_price: maxPrice.value,
        page: page.value,
        page_size: pageSize,
      })
      items.value = res.data.data.items
      total.value = res.data.data.total
    } else {
      res = await itemsApi.list({ page: page.value, page_size: pageSize })
      items.value = res.data.data.items
      total.value = res.data.data.total
    }
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const res = await client.get('/categories/')
  categories.value = res.data.data
}

function search() {
  page.value = 1
  load()
}
function reset() {
  keyword.value = ''
  categoryId.value = undefined
  minPrice.value = undefined
  maxPrice.value = undefined
  search()
}

onMounted(() => {
  loadCategories()
  load()
})
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 标题 */
.page-head h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px;
}
.page-head p {
  color: var(--text-muted);
  margin: 0;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 16px;
  background: #fafafa;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.search-input {
  flex: 1;
  min-width: 240px;
}
.search-input :deep(.el-input-group__append) {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}
.search-input :deep(.el-input-group__append .el-button) {
  color: #fff !important;
}

.cat-select {
  width: 140px;
}

.price-input {
  width: 120px;
}

.price-dash {
  color: var(--text-muted);
}

/* 商品区 */
.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}
.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.section-count {
  font-size: 13px;
  color: var(--text-muted);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: var(--text-muted);
}

.pagination {
  margin-top: 24px;
  justify-content: center;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .cat-select,
  .price-input {
    width: 100%;
  }
  .price-dash {
    display: none;
  }
}
</style>
