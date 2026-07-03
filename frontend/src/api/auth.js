import client from './client'

export const authAPI = {
  login: (data) => client.post('/auth/login/', data).then((r) => r.data),
  register: (data) => client.post('/auth/register/', data).then((r) => r.data),
  refresh: (refreshToken) => client.post('/auth/refresh/', { refresh_token: refreshToken }).then((r) => r.data),
  logout: () => client.post('/auth/logout/').then((r) => r.data),
  profile: () => client.get('/auth/profile/').then((r) => r.data),
  updateProfile: (data) => client.patch('/auth/profile/', data).then((r) => r.data),
  changePassword: (data) => client.post('/auth/change-password/', data).then((r) => r.data),
  listUsers: () => client.get('/auth/users/').then((r) => r.data),
  createUser: (data) => client.post('/auth/users/', data).then((r) => r.data),
  updateUser: (id, data) => client.patch(`/auth/users/${id}/`, data).then((r) => r.data),
  disableUser: (id) => client.delete(`/auth/users/${id}/`).then((r) => r.data),
  activityLog: () => client.get('/auth/activity/').then((r) => r.data),
}
