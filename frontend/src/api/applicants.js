import client from './client'

export const applicantsAPI = {
  list: (params) => client.get('/applicants/', { params }).then((r) => r.data),
  get: (id) => client.get(`/applicants/${id}/`).then((r) => r.data),
  create: (data) => client.post('/applicants/', data).then((r) => r.data),
  update: (id, data) => client.patch(`/applicants/${id}/`, data).then((r) => r.data),
  delete: (id) => client.delete(`/applicants/${id}/`).then((r) => r.data),
}
