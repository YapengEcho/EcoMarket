import client from './client'
import type { Item } from '@/types'

export const itemsApi = {
  list: (params?: { page?: number; page_size?: number }) =>
    client.get('/items/', { params }),
  search: (params: {
    keyword?: string; category_id?: number
    min_price?: number; max_price?: number; status?: number
    page?: number; page_size?: number
  }) => client.get('/items/search', { params }),
  detail: (id: number) => client.get<{ data: Item }>(`/items/${id}`),
  create: (data: Partial<Item>) => client.post('/items/', data),
  update: (id: number, data: Partial<Item>) => client.put(`/items/${id}`, data),
  remove: (id: number) => client.delete(`/items/${id}`),
  myItems: () => client.get('/items/my/items'),
  favorites: () => client.get('/favorites/'),
  addFavorite: (item_id: number) => client.post('/favorites/', { item_id }),
  removeFavorite: (item_id: number) => client.delete(`/favorites/${item_id}`),
}
