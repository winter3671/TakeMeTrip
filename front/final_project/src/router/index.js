import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import CourseView from '@/views/CourseView.vue'
import HomeView from '@/views/HomeView.vue'
import InformationView from '@/views/InformationView.vue'
import LocationView from '@/views/LocationView.vue'
import LoginView from '@/views/LoginView.vue'
import MapView from '@/views/MapView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SignUpView from '@/views/SignUpView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAccountStore } from '@/stores/accounts'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/community',
      name: 'community',
      component: CommunityView
    },
    {
      path: '/course',
      name: 'course',
      component: CourseView
    },
    {
      path: '/information',
      name: 'information',
      component: InformationView
    },
    {
      path: '/location',
      name: 'location',
      component: LocationView
    },
    {
      path: '/map',
      name: 'map',
      component: MapView
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpView, 
    },
    {
      path: '/community/:id',
      name: 'article-detail',
      component: ArticleDetailView
    },
    {
      path: '/community/create',
      name: 'article-create',
      component: ArticleCreateView,
      beforeEnter: (to, from, next) => {
          const store = useAccountStore()
          if (!store.isLogin) {
              alert('로그인이 필요합니다.')
              next({ name: 'login' })
          } else {
              next()
          }
      } 
    },

  ],
})

export default router
