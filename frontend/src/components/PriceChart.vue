<template>
  <div ref="chartRef" class="chart-box"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ data: Array<{ range: string; count: number }> }>()
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
      data: props.data.map(d => d.range),
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
      type: 'bar',
      data: props.data.map(d => d.count),
      barWidth: '60%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#5a8a2a' },
          { offset: 1, color: 'rgba(90,138,42,0.2)' },
        ]),
        borderRadius: [2, 2, 0, 0],
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
