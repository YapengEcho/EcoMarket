<template>
  <div v-loading="loading" class="detail">
    <template v-if="item">
      <!-- 返回 -->
      <button class="back-btn" @click="$router.back()">← 返回市集</button>

      <!-- 主体：左图右信息 -->
      <div class="detail-grid">
        <!-- 左：图片展示 -->
        <div class="media-panel">
          <div class="img-box">
            <img v-if="mainImg" :src="mainImg" :alt="item.title" />
            <div v-else class="placeholder">
              <span class="placeholder-mark">◐</span>
              <span class="placeholder-text">暂无图片</span>
            </div>
          </div>
        </div>

        <!-- 右：信息面板 -->
        <div class="info-panel">
          <div class="info-header">
            <span class="status-tag" :class="statusClass">{{ statusText(item.status) }}</span>
            <span class="view-count">{{ item.view_count || 0 }} 次浏览</span>
          </div>

          <h1 class="item-title">{{ item.title }}</h1>

          <div class="price-block">
            <span class="price-current">¥{{ formatPrice(item.price) }}</span>
            <span v-if="item.original_price" class="price-origin">原价 ¥{{ formatPrice(item.original_price) }}</span>
            <span v-if="item.original_price" class="price-discount">
              {{ Math.round((item.price / item.original_price) * 100) }}% off
            </span>
          </div>

          <div class="meta-row">
            <div class="meta-item">
              <span class="meta-label">成色</span>
              <span class="meta-value">{{ item.condition === 0 ? "全新" : "闲置" }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">卖家</span>
              <span class="meta-value">{{ item.seller_name || '匿名' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">发布</span>
              <span class="meta-value">{{ item.created_at?.slice(0, 10) }}</span>
            </div>
          </div>

          <div class="divider"></div>

          <div class="desc-block">
            <p class="desc-label">商品描述</p>
            <p class="desc-text">{{ item.description || '卖家暂未填写描述。' }}</p>
          </div>

          <div class="actions">
            <button
              class="btn-buy"
              :disabled="item.status !== 0 || !authStore.token"
              @click="buy"
            >
              {{ item.status !== 0 ? "已售出" : "立即购买" }}
            </button>
            <button class="btn-fav" :class="{ active: isFav }" @click="toggleFavorite">
              <span class="fav-icon">{{ isFav ? "♥" : "♡" }}</span>
              {{ isFav ? "已收藏" : "收藏" }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { itemsApi } from '@/api/items'
import { requestsApi } from '@/api/requests'
import { useAuthStore } from '@/stores/auth'
import type { Item } from '@/types'
import { formatPrice, formatImage, statusText } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const item = ref<Item | null>(null)
const loading = ref(false)
const isFav = ref(false)

const mainImg = computed(() => formatImage(item.value?.images))

const statusClass = computed(() => {
  const s = item.value?.status
  if (s === 0) return 'tag-available'
  if (s === 1) return 'tag-reserved'
  return 'tag-sold'
})

async function load() {
  loading.value = true
  try {
    const res = await itemsApi.detail(Number(route.params.id))
    item.value = res.data.data
  } finally {
    loading.value = false
  }
}

async function checkFavorite() {
  if (!authStore.token) return
  const res = await itemsApi.favorites()
  const list = res.data.data
  isFav.value = list.some((f: any) => f.item_id === Number(route.params.id))
}

async function toggleFavorite() {
  if (!authStore.token) { router.push('/login'); return }
  try {
    if (isFav.value) {
      await itemsApi.removeFavorite(Number(route.params.id))
      isFav.value = false
      ElMessage.success('已取消收藏')
    } else {
      await itemsApi.addFavorite(Number(route.params.id))
      isFav.value = true
      ElMessage.success('收藏成功')
    }
  } catch {}
}

async function buy() {
  try {
    const { value } = await ElMessageBox.prompt('请输入给卖家的留言（选填）', '确认购买', {
      inputType: 'textarea', confirmButtonText: '确认', cancelButtonText: '取消',
    })
    await requestsApi.create(Number(route.params.id), value || undefined)
    ElMessage.success('交易请求已发送，等待卖家处理')
    router.push('/my-orders')
  } catch {}
}

onMounted(() => {
  load()
  checkFavorite()
})
</script>

<style scoped>
.detail {
  min-height: 500px;
}

.back-btn {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0 0 24px;
  transition: color 0.2s;
}
.back-btn:hover {
  color: var(--accent);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: start;
}

/* ====== 左侧图片 ====== */
.media-panel {
  position: sticky;
  top: 88px;
}

.img-box {
  aspect-ratio: 4 / 5;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.img-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
}

.placeholder-mark {
  font-family: var(--font-body);
  font-size: 80px;
  color: var(--border-strong);
}

.placeholder-text {
  font-family: var(--font-body);
  font-size: 12px;
}

/* ====== 右侧信息 ====== */
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 8px 0;
}

.info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-tag {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 4px 12px;
  border-radius: var(--radius-sm);
}

.tag-available {
  background: var(--accent-soft);
  color: var(--color-success);
  border: 1px solid var(--color-success);
}
.tag-reserved {
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid var(--accent);
}
.tag-sold {
  background: rgba(196, 80, 44, 0.12);
  color: var(--color-danger);
  border: 1px solid var(--color-danger);
}

.view-count {
  font-family: var(--font-body);
  font-size: 12px;
  color: var(--text-muted);
}

.item-title {
  font-family: var(--font-body);
  font-size: 36px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.price-block {
  display: flex;
  align-items: baseline;
  gap: 14px;
  flex-wrap: wrap;
}

.price-current {
  font-family: var(--font-body);
  font-size: 44px;
  font-weight: 800;
  color: var(--accent);
  letter-spacing: -0.03em;
  line-height: 1;
}

.price-origin {
  font-size: 15px;
  color: var(--text-muted);
  text-decoration: line-through;
}

.price-discount {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-success);
  background: var(--accent-soft);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
}

.meta-row {
  display: flex;
  gap: 32px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-family: var(--font-body);
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.meta-value {
  font-size: 14px;
  color: var(--text-secondary);
}

.divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 4px 0;
}

.desc-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.desc-label {
  font-family: var(--font-body);
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.desc-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-secondary);
  min-height: 60px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.btn-buy {
  flex: 1;
  font-family: var(--font-body);
  font-size: 15px;
  font-weight: 600;
  color: var(--bg-base);
  background: var(--accent);
  border: none;
  padding: 16px 24px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-buy:hover:not(:disabled) {
  background: #ff8d3a;
  transform: translateY(-1px);
  box-shadow: var(--shadow-card);
}
.btn-buy:disabled {
  background: var(--border-strong);
  color: var(--text-muted);
  cursor: not-allowed;
}

.btn-fav {
  font-family: var(--font-body);
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  padding: 16px 24px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-fav:hover {
  border-color: var(--accent);
  color: var(--accent);
}
.btn-fav.active {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.fav-icon {
  font-size: 16px;
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .media-panel {
    position: static;
  }
  .item-title {
    font-size: 28px;
  }
  .price-current {
    font-size: 36px;
  }
}
</style>
