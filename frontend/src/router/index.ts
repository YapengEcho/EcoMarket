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
    // 管理员后台
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      redirect: '/admin/dashboard',
      children: [
        {
          path: 'dashboard', name: 'admin-dashboard',
          component: () => import('@/views/admin/Dashboard.vue'),
        },
        {
          path: 'users', name: 'admin-users',
          component: () => import('@/views/admin/UserList.vue'),
        },
        {
          path: 'items', name: 'admin-items',
          component: () => import('@/views/admin/ItemList.vue'),
        },
        {
          path: 'categories', name: 'admin-categories',
          component: () => import('@/views/admin/Categories.vue'),
        },
        {
          path: 'transactions', name: 'admin-transactions',
          component: () => import('@/views/admin/Transactions.vue'),
        },
        {
          path: 'reviews', name: 'admin-reviews',
          component: () => import('@/views/admin/Reviews.vue'),
        },
        {
          path: 'messages', name: 'admin-messages',
          component: () => import('@/views/admin/Messages.vue'),
        },
      ],
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
