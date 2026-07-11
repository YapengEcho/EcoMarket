import client from './client'

export const messagesApi = {
  /** 我的收件箱 */
  list: (unreadOnly = false) =>
    client.get('/messages/', { params: { unread_only: unreadOnly } }),
  /** 发送站内消息（基于商品，用于交易后协商时间地点） */
  send: (receiver_id: number, content: string, item_id?: number, title?: string) =>
    client.post('/messages/', { receiver_id, content, item_id, title }),
  /** 查询某商品下与对方的对话历史 */
  conversation: (itemId: number, peerId: number) =>
    client.get(`/messages/conversation/${itemId}`, { params: { peer_id: peerId } }),
  /** 标记单条消息已读 */
  markRead: (msgId: number) =>
    client.put(`/messages/${msgId}/read`),
  /** 未读消息数 */
  unreadCount: () =>
    client.get('/messages/unread/count'),
}
