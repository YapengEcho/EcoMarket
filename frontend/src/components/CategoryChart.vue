<template>
  <div ref="chartRef" class="chart-box"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{ data: Array<{ name: string; count: number }> }>()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const palette = ['#d9651a', '#5a8a2a', '#b54324', '#9a9382', '#c4a878', '#5c5648']

function render() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#ffffff',
      borderColor: '#d4cdbb',
      textStyle: { color: '#1a1813' },
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#5c5648', fontSize: 11 },
    },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '45%'],
      label: { color: '#5c5648', fontSize: 11 },
      data: props.data.map((d, i) => ({
        name: d.name,
        value: d.count,
        itemStyle: { color: palette[i % palette.length] },
      })),
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
