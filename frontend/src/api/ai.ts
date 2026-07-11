import client from './client'

export const aiApi = {
  generate: (product_name: string, additional_info?: string) =>
    client.post('/ai/generate', { product_name, additional_info }),
  search: (query: string) => client.post('/ai/search', null, { params: { query } }),
}
