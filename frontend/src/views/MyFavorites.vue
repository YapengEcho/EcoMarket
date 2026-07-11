<template>
  <div class="my-favorites">
    <div class="page-header">
      <h1>我的收藏</h1>
      <p>共 {{ filtered.length }} 件收藏</p>
    </div>

    <!-- 状态过滤 -->
    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" @change="applyFilter">
        <el-radio-button label="all">全部 ({{ favorites.length }})</el-radio-button>
        <el-radio-button :label="0">在售 ({{ countByStatus(0) }})</el-radio-button>
        <el-radio-button :label="1">已预订 ({{ countByStatus(1) }})</el-radio-button>
        <el-radio-button :label="2">已售出 ({{ countByStatus(2) }})</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 商品网格 -->
    <div v-loading="loading" class="grid">
      <div v-for="fav in filtered" :key="fav.favorite_id" class="fav-card" @click="goDetail(fav.item_id)">
        <div class="img-wrap">
          <img v-if="fav.images" :src="imgUrl(fav.images)" :alt="fav.title" @error="onImgError" />
          <div v-else class="img-placeholder">暂无图片</div>
          <span class="status-tag" :class="statusClass(fav.status)">{{ statusText(fav.status) }}</span>
        </div>
        <div class="info">
          <h3 class="title">{{ fav.title }}</h3>
          <div class="price-row">
            <span class="price">¥{{ fav.price.toFixed(2) }}</span>
          </div>
        </div>
        <button class="remove-btn" @click.stop="removeFav(fav.item_id)" title="取消收藏">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="#ef4444"/>
          </svg>
        </button>
      </div>

      <div v-if="!loading && filtered.length === 0" class="empty">
        <p>{{ favorites.length === 0 ? '还没有收藏任何商品' : '该状态下没有商品' }}</p>
        <el-button type="primary" @click="$router.push('/')">去逛逛</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { favoritesApi, type FavoriteItem } from '@/api/favorites'

const router = useRouter()
const favorites = ref<FavoriteItem[]>([])
const filtered = ref<FavoriteItem[]>([])
const loading = ref(false)
const statusFilter = ref<string | number>('all')

function statusText(s: number) {
  return ['在售', '已预订', '已售出'][s] || '未知'
}
function statusClass(s: number) {
  return ['on-sale', 'reserved', 'sold'][s] || ''
}
function countByStatus(s: number) {
  return favorites.value.filter(f => f.status === s).length
}

function applyFilter() {
  if (statusFilter.value === 'all') {
    filtered.value = favorites.value
  } else {
    filtered.value = favorites.value.filter(f => f.status === statusFilter.value)
  }
}

function imgUrl(images: string): string {
  // images 可能是 "/uploads/item_1.png" 或 JSON 数组字符串
  try {
    const parsed = JSON.parse(images)
    if (Array.isArray(parsed) && parsed.length > 0) return parsed[0]
  } catch {
    // 不是 JSON，当作普通路径
  }
  return images
}

function onImgError(e: Event) {
  const target = e.target as HTMLImageElement
  target.style.display = 'none'
}

function goDetail(id: number) {
  router.push(`/item/${id}`)
}

async function load() {
  loading.value = true
  try {
    const res = await favoritesApi.list()
    favorites.value = res.data.data
    applyFilter()
  } finally {
    loading.value = false
  }
}

async function removeFav(itemId: number) {
  try {
    await ElMessageBox.confirm('确定取消收藏该商品？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await favoritesApi.remove(itemId)
    favorites.value = favorites.value.filter(f => f.item_id !== itemId)
    applyFilter()
    ElMessage.success('已取消收藏')
  } catch {
    // 用户点了取消
  }
}

onMounted(load)
</script>

<style scoped>
.my-favorites {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px;
}
.page-header p {
  color: var(--text-muted);
  margin: 0;
  font-size: 13px;
}

.filter-bar {
  margin-bottom: 20px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  min-height: 300px;
}

.fav-card {
  position: relative;
  background: #fff;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.fav-card:hover {
  border-color: var(--accent);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.img-wrap {
  position: relative;
  width: 100%;
  height: 180px;
  background: #f5f5f5;
  overflow: hidden;
}
.img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 13px;
}

.status-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #fff;
}
.status-tag.on-sale { background: #10b981; }
.status-tag.reserved { background: #f59e0b; }
.status-tag.sold { background: #6b7280; }

.info {
  padding: 12px;
}
.title {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.price-row {
  display: flex;
  align-items: center;
}
.price {
  font-size: 16px;
  font-weight: 600;
  color: var(--accent);
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
  backdrop-filter: blur(4px);
}
.remove-btn:hover {
  background: #fff;
  transform: scale(1.1);
}

.empty {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 0;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
  .img-wrap {
    height: 140px;
  }
}
</style>
