import axios from 'axios'

const client = axios.create({ baseURL: '/api', timeout: 30000 })

let isRefreshing = false
let refreshSubscribers = []

function onRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

function onRefreshFailed(err) {
  refreshSubscribers.forEach((cb) => cb(null))
  refreshSubscribers = []
}

function storage() {
  return localStorage.getItem('refresh_token') ? localStorage : sessionStorage
}

client.interceptors.request.use((config) => {
  const token = storage().getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    const originalRequest = err.config
    if (err.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = storage().getItem('refresh_token')
      if (!refreshToken) {
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('refresh_token')
        sessionStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(err)
      }
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshSubscribers.push((token) => {
            if (!token) return reject(err)
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(client(originalRequest))
          })
        })
      }
      originalRequest._retry = true
      isRefreshing = true
      try {
        const res = await axios.post('/api/auth/refresh/', { refresh_token: refreshToken })
        const newToken = res.data.access_token
        storage().setItem('token', newToken)
        onRefreshed(newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return client(originalRequest)
      } catch {
        onRefreshFailed()
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('refresh_token')
        sessionStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(err)
  },
)

export default client
