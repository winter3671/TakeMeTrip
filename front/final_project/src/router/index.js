import ArticleCreateView from '@/views/ArticleCreateView.vue'
import ArticleDetailView from '@/views/ArticleDetailView.vue'
import CommunityView from '@/views/CommunityView.vue'
import HomeView from '@/views/HomeView.vue'
import InformationView from '@/views/InformationView.vue'
import LocationView from '@/views/LocationView.vue'
import LoginView from '@/views/LoginView.vue'
import MapView from '@/views/MapView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SignUpView from '@/views/SignUpView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAccountStore } from '@/stores/accounts'
import SocialCallback from '@/views/SocialCallback.vue'
import AIPlannerView from '@/views/AIPlannerView.vue'
import ArticleUpdateView from '@/views/ArticleUpdateView.vue'
import TripDetailView from '@/views/TripDetailView.vue'
import TripSearchView from '@/views/TripSearchView.vue'
import DartGameView from '@/views/DartGameView.vue'

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
      path: '/planner',
      name: 'planner',
      component: AIPlannerView
    },
    {
      path: '/trips/:id', 
      name: 'trip-detail',
      component: TripDetailView
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
      path: '/search',
      name: 'search',
      component: TripSearchView
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
    {
      path: '/community/:id/update',
      name: 'article-update',
      component: ArticleUpdateView
    },
    {
      path: '/auth/callback',
      name: 'SocialCallback',
      component: SocialCallback,
    },
    {
      path: '/game',
      name: 'game',
      component: DartGameView
    }
  ],
})

export default router
