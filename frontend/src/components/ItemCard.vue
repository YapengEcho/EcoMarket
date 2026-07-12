<template>
  <article class="item-card" @click="onClick">
    <div class="card-media">
      <img
        v-if="imgUrl && !imgError"
        :src="imgUrl"
        :alt="item.title"
        loading="lazy"
        @error="imgError = true"
      />
      <div v-else class="media-placeholder">暂无图片</div>
      <span v-if="item.status !== 0" class="status-badge">{{ statusText(item.status) }}</span>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ item.title }}</h3>
      <div class="card-meta">
        <span class="card-seller">卖家：{{ item.seller_name || '匿名' }}</span>
        <span class="card-score">★ {{ formatScore(item.seller_score) }}</span>
      </div>
      <span class="card-price">¥{{ formatPrice(item.price) }}</span>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Item } from '@/types'
import { formatPrice, formatImage, statusText } from '@/utils/format'

const props = defineProps<{ item: Item }>()
const router = useRouter()
const imgError = ref(false)
const imgUrl = computed(() => formatImage(props.item.images))

function formatScore(v?: number): string {
  const s = Number(v)
  return isNaN(s) ? '5.0' : s.toFixed(1)
}

function onClick() {
  router.push(`/item/${props.item.item_id}`)
}
</script>

<style scoped>
.item-card {
  background: #fff;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.item-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-card);
}

.card-media {
  position: relative;
  aspect-ratio: 4 / 3;
  background: #fafafa;
  overflow: hidden;
}
.card-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
  font-size: 13px;
}

.status-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 2px 8px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: var(--radius-sm);
}

.card-body {
  padding: 12px 14px;
}
.card-title {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  color: var(--text-primary);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}
.card-price {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-meta {
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-seller {
  font-size: 12px;
  color: var(--text-muted);
}
.card-score {
  font-size: 12px;
  color: #f5a623;
  font-weight: 600;
}
</style>
