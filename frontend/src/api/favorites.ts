import client from './client'

export interface FavoriteItem {
  favorite_id: number
  item_id: number
  title: string
  price: number
  status: number
  images?: string
  created_at?: string
}

export const favoritesApi = {
  list: () => client.get<{ data: FavoriteItem[] }>('/favorites/'),
  add: (item_id: number) => client.post('/favorites/', { item_id }),
  remove: (item_id: number) => client.delete(`/favorites/${item_id}`),
}
