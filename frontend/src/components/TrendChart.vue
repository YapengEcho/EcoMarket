<template>
  <div ref="chartRef" class="chart-box"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ data: Array<{ date: string; count: number }> }>()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function render() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    backgroundColor: 'transparent',
    grid: { top: 20, right: 20, bottom: 32, left: 40 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#ffffff',
      borderColor: '#d4cdbb',
      textStyle: { color: '#1a1813' },
    },
    xAxis: {
      type: 'category',
      data: props.data.map(d => d.date),
      axisLine: { lineStyle: { color: '#d4cdbb' } },
      axisLabel: { color: '#9a9382', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#e8e3d6' } },
      axisLabel: { color: '#9a9382', fontSize: 11 },
    },
    series: [{
      name: '成交量',
      type: 'line',
      smooth: true,
      data: props.data.map(d => d.count),
      lineStyle: { color: '#d9651a', width: 2 },
      itemStyle: { color: '#d9651a' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(217,101,26,0.25)' },
          { offset: 1, color: 'rgba(217,101,26,0)' },
        ]),
      },
    }],
  })
}

onMounted(render)
watch(() => props.data, render)
onUnmounted(() => chart?.dispose())
</script>

<style scoped>
.chart-box {
  width: 100%;
  height: 280px;
}
</style>
