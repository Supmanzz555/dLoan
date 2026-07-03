import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api/auth'

function storage() {
  return localStorage.getItem('refresh_token') ? localStorage : sessionStorage
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || sessionStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isReviewer = computed(() => user.value?.role === 'admin' || user.value?.role === 'reviewer' || user.value?.is_super_admin === true)
  const isSuperAdmin = computed(() => user.value?.is_super_admin === true)

  function save(t, rt, u, remember) {
    const store = remember ? localStorage : sessionStorage
    token.value = t
    refreshToken.value = rt
    user.value = u
    store.setItem('token', t)
    store.setItem('refresh_token', rt)
    store.setItem('user', JSON.stringify(u))
    if (remember && sessionStorage.getItem('token')) {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('refresh_token')
      sessionStorage.removeItem('user')
    }
  }

  async function login(credentials) {
    const res = await authAPI.login(credentials)
    save(res.access_token, res.refresh_token, res.user, credentials.remember)
    return res
  }

  async function register(data) {
    const res = await authAPI.register(data)
    save(res.access_token, res.refresh_token, res.user, true)
    return res
  }

  async function refresh() {
    if (!refreshToken.value) return false
    try {
      const res = await authAPI.refresh(refreshToken.value)
      token.value = res.access_token
      const store = storage()
      store.setItem('token', res.access_token)
      return true
    } catch {
      logout()
      return false
    }
  }

  async function fetchProfile() {
    const res = await authAPI.profile()
    user.value = res
    storage().setItem('user', JSON.stringify(res))
  }

  function logout() {
    authAPI.logout().catch(() => {})
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('user')
    window.location.href = '/login'
  }

  return { token, refreshToken, user, isAuthenticated, isAdmin, isReviewer, isSuperAdmin, login, register, refresh, fetchProfile, logout }
})
