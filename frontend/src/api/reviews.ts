import client from './client'

export const reviewsApi = {
  /** 创建评价（交易完成后，买卖双方互评） */
  create: (request_id: number, rating: number, comment?: string) =>
    client.post('/reviews/', { request_id, rating, comment }),
  /** 获取某用户收到的评价 */
  listByUser: (userId: number) =>
    client.get(`/reviews/user/${userId}`),
}
