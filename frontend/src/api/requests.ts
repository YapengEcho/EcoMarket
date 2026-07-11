import client from './client'

export const requestsApi = {
  create: (item_id: number, message?: string) =>
    client.post('/requests/', { item_id, message }),
  updateStatus: (id: number, status: number) =>
    client.put(`/requests/${id}/status`, null, { params: { status } }),
  confirm: (id: number, code: string) =>
    client.post(`/requests/${id}/confirm`, { code }),
  my: (asBuyer = true) =>
    client.get('/requests/my', { params: { as_buyer: asBuyer } }),
}
