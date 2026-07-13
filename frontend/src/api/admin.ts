import client from './client'

export const adminApi = {
  // 工作台
  stats: () => client.get('/admin/stats'),
  dashboard: () => client.get('/statistics/dashboard'),

  // 用户管理
  listUsers: (page = 1, pageSize = 20, keyword = '') =>
    client.get('/admin/users', { params: { page, page_size: pageSize, keyword } }),
  updateUserStatus: (userId: number, isActive: boolean) =>
    client.put(`/admin/users/${userId}/status`, { is_active: isActive }),
  resetUserPassword: (userId: number, newPassword: string) =>
    client.put(`/admin/users/${userId}/password`, { new_password: newPassword }),

  // 商品管理
  listItems: (page = 1, pageSize = 20, status?: number) =>
    client.get('/admin/items', { params: { page, page_size: pageSize, status } }),
  auditItem: (itemId: number, status: number) =>
    client.put(`/admin/items/${itemId}/audit`, { status }),
  deleteItem: (itemId: number) => client.delete(`/admin/items/${itemId}`),

  // 分类管理
  listCategories: () => client.get('/categories/'),
  createCategory: (name: string, parentId = 0) =>
    client.post('/categories/', { name, parent_id: parentId, sort_order: 0 }),
  updateCategory: (id: number, name: string) =>
    client.put(`/categories/${id}`, null, { params: { name } }),
  deleteCategory: (id: number) => client.delete(`/categories/${id}`),

  // 交易管理
  listTransactions: (page = 1, pageSize = 20, status?: number) =>
    client.get('/admin/transactions', { params: { page, page_size: pageSize, status } }),

  // 评价管理
  listReviews: (page = 1, pageSize = 20) =>
    client.get('/admin/reviews', { params: { page, page_size: pageSize } }),
  deleteReview: (reviewId: number) => client.delete(`/admin/reviews/${reviewId}`),

  // 消息管理
  listMessages: (page = 1, pageSize = 20) =>
    client.get('/admin/messages', { params: { page, page_size: pageSize } }),
}
