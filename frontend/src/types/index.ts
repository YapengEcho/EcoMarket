export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface User {
  user_id: number
  username: string
  email?: string
  phone?: string
  avatar?: string
  school?: string
  reputation_score: number
  is_admin: boolean
  created_at?: string
}

export interface Item {
  item_id: number
  user_id: number
  category_id?: number
  title: string
  description?: string
  price: number
  original_price?: number
  condition: number
  status: number
  images?: string[] | string
  view_count?: number
  seller_id?: number
  seller_name?: string
  seller_score?: number
  created_at?: string
}

export interface TradeRequest {
  request_id: number
  item_id: number
  status: number
  message?: string
  created_at?: string
}

export interface DashboardData {
  trend: Array<{ date: string; count: number }>
  categories: Array<{ name: string; count: number }>
  price_ranges: Array<{ range: string; count: number }>
  overview: {
    total_users: number
    total_items: number
    available_items: number
    completed_orders: number
  }
  db_type: string
}
