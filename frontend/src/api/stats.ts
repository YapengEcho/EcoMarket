import client from './client'
import type { DashboardData } from '@/types'

export const statsApi = {
  dashboard: () => client.get<{ data: DashboardData }>('/statistics/dashboard'),
}
