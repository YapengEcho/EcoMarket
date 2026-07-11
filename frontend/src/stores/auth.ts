import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const username = ref<string>(localStorage.getItem('username') || '')
  const userId = ref<number>(Number(localStorage.getItem('userId')) || 0)
  const isAdmin = ref<boolean>(localStorage.getItem('isAdmin') === 'true')
  const user = ref<User | null>(null)

  const isLogged = computed(() => !!token.value)

  async function login(uname: string, pwd: string) {
    const res = await authApi.login({ username: uname, password: pwd })
    const d = res.data.data
    token.value = d.token
    username.value = d.username
    userId.value = d.user_id
    localStorage.setItem('token', d.token)
    localStorage.setItem('username', d.username)
    localStorage.setItem('userId', String(d.user_id))
    isAdmin.value = d.user_id === 1
    localStorage.setItem('isAdmin', String(isAdmin.value))
  }

  async function fetchProfile() {
    const res = await authApi.me()
    user.value = res.data.data
    return res.data.data
  }

  function logout() {
    token.value = ''
    username.value = ''
    userId.value = 0
    isAdmin.value = false
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
    localStorage.removeItem('isAdmin')
  }

  return { token, username, userId, isAdmin, user, isLogged, login, fetchProfile, logout }
})
