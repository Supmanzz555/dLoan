import client from './client'

export const screeningAPI = {
  screen: (data) => client.post('/screen/', data).then((r) => r.data),
  status: (jobId) => client.get(`/screen/${jobId}/status/`).then((r) => r.data),
  list: (params) => client.get('/screenings/', { params }).then((r) => r.data),
  detail: (id) => client.get(`/screenings/${id}/detail/`).then((r) => r.data),
  feedback: (data) => client.post('/feedback/', data).then((r) => r.data),
  feedbackList: () => client.get('/feedback/').then((r) => r.data),
  review: (screeningId, data) => client.post(`/screenings/${screeningId}/review/`, data).then((r) => r.data),
}
