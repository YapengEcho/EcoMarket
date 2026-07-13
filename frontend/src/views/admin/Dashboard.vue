<template>
  <div class="dashboard" v-loading="loading">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #e8f3ff; color: #2563eb">
          <el-icon size="24"><User /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">用户总数</span>
          <span class="stat-num">{{ data?.overview.total_users ?? 0 }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #f0f9eb; color: #16a34a">
          <el-icon size="24"><Goods /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">商品总数</span>
          <span class="stat-num">{{ data?.overview.total_items ?? 0 }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #d97706">
          <el-icon size="24"><ShoppingCart /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">在售商品</span>
          <span class="stat-num">{{ data?.overview.available_items ?? 0 }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef0f0; color: #dc2626">
          <el-icon size="24"><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">成交订单</span>
          <span class="stat-num">{{ data?.overview.completed_orders ?? 0 }}</span>
        </div>
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
import { User, Goods, ShoppingCart, CircleCheck } from '@element-plus/icons-vue'
import TrendChart from '@/components/TrendChart.vue'
import CategoryChart from '@/components/CategoryChart.vue'
import PriceChart from '@/components/PriceChart.vue'
import { adminApi } from '@/api/admin'
import type { DashboardData } from '@/types'

const data = ref<DashboardData | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await adminApi.dashboard()
    data.value = res.data.data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: #fff;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 20px;
}

.chart-card.full {
  grid-column: 1 / -1;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

@media (max-width: 992px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
