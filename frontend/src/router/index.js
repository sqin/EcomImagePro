import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  const requiresAuth = to.meta.requiresAuth !== false

  if (to.path === '/login') {
    // 如果已登录，跳转到主页
    if (token) {
      next('/')
    } else {
      next()
    }
  } else if (requiresAuth) {
    // 需要登录的页面
    if (token) {
      next()
    } else {
      next('/login')
    }
  } else {
    next()
  }
})

export default router

