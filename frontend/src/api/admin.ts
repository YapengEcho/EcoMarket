import client from './client'

export const adminApi = {
  listUsers: () => client.get('/admin/users'),
  auditItem: (id: number, status: number) =>
    client.put(`/admin/items/${id}/audit`, null, { params: { status } }),
  stats: () => client.get('/admin/stats'),
}
