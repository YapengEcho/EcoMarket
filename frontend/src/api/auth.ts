import client from './client'
import type { User } from '@/types'

export const authApi = {
  register: (data: { username: string; password: string; email?: string; school?: string }) =>
    client.post('/auth/register', data),
  login: (data: { username: string; password: string }) =>
    client.post<{ data: { token: string; user_id: number; username: string } }>('/auth/login', data),
  me: () => client.get<{ data: User }>('/auth/me'),
  updateMe: (data: Partial<User>) => client.put('/auth/me', data),
}
