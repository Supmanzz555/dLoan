import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/RegisterView.vue') },
  {
    path: '/',
    component: () => import('../views/LayoutView.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'applicants', name: 'Applicants', component: () => import('../views/ApplicantListView.vue') },
      { path: 'applicants/new', name: 'ApplicantNew', component: () => import('../views/ApplicantFormView.vue') },
      { path: 'applicants/:id/edit', name: 'ApplicantEdit', component: () => import('../views/ApplicantFormView.vue') },
      { path: 'applicants/:id', name: 'ApplicantDetail', component: () => import('../views/ApplicantDetailView.vue') },
      { path: 'screen', name: 'Screen', component: () => import('../views/ScreenView.vue') },
      { path: 'history', name: 'History', component: () => import('../views/HistoryView.vue') },
      { path: 'profile', name: 'Profile', component: () => import('../views/ProfileView.vue') },
      {
        path: 'admin/users',
        name: 'UserManagement',
        component: () => import('../views/UserManagementView.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'admin/activity',
        name: 'ActivityLog',
        component: () => import('../views/ActivityLogView.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return next('/')
  }
  next()
})

export default router
