import client from './client'

export const dashboardAPI = {
  summary: (params) => client.get('/dashboard/summary/', { params }).then((r) => r.data),
  exportCsv: () =>
    client.get('/screenings/export/', { responseType: 'blob' }).then((r) => r.data),
}
