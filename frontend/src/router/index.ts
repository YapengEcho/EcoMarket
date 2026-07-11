import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/Home.vue') },
    { path: '/login', name: 'login', component: () => import('@/views/Login.vue') },
    { path: '/register', name: 'register', component: () => import('@/views/Register.vue') },
    { path: '/item/:id', name: 'item-detail', component: () => import('@/views/ItemDetail.vue') },
    {
      path: '/publish', name: 'publish', component: () => import('@/views/Publish.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/my-items', name: 'my-items', component: () => import('@/views/MyItems.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/my-orders', name: 'my-orders', component: () => import('@/views/MyOrders.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/my-favorites', name: 'my-favorites', component: () => import('@/views/MyFavorites.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile', name: 'profile', component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin', name: 'admin', component: () => import('@/views/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
