<template>
  <div class="admin" v-loading="loading">
    <div class="page-header">
      <p class="page-eyebrow">数据看板</p>
      <h1 class="page-title">平台<span class="title-accent">全景</span></h1>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-label">用户数</span>
        <span class="stat-num amber">{{ data?.overview.total_users ?? 0 }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">商品数</span>
        <span class="stat-num moss">{{ data?.overview.total_items ?? 0 }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">在售</span>
        <span class="stat-num amber">{{ data?.overview.available_items ?? 0 }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">成交</span>
        <span class="stat-num moss">{{ data?.overview.completed_orders ?? 0 }}</span>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-row">
      <div class="chart-card">
        <h3 class="chart-title">交易趋势</h3>
        <TrendChart :data="data?.trend || []" />
      </div>
      <div class="chart-card">
        <h3 class="chart-title">分类占比</h3>
        <CategoryChart :data="data?.categories || []" />
      </div>
    </div>

    <div class="chart-card full">
      <h3 class="chart-title">价格分布</h3>
      <PriceChart :data="data?.price_ranges || []" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TrendChart from '@/components/TrendChart.vue'
import CategoryChart from '@/components/CategoryChart.vue'
import PriceChart from '@/components/PriceChart.vue'
import { statsApi } from '@/api/stats'
import type { DashboardData } from '@/types'

const data = ref<DashboardData | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await statsApi.dashboard()
    data.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.admin {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  margin-bottom: 8px;
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

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.2s;
}
.stat-card:hover {
  border-color: var(--accent);
}

.stat-label {
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.stat-num {
  font-family: var(--font-body);
  font-size: 40px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.03em;
}
.stat-num.amber {
  color: var(--accent);
}
.stat-num.moss {
  color: var(--color-success);
}

/* 图表卡片 */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.chart-card.full {
  grid-column: 1 / -1;
}

.chart-title {
  font-family: var(--font-body);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
