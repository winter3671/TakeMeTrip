import CommunityView from '@/view/CommunityView.vue'
import CourseView from '@/view/CourseView.vue'
import HomeView from '@/view/HomeView.vue'
import InformationView from '@/view/InformationView.vue'
import LocationView from '@/view/LocationView.vue'
import MapView from '@/view/MapView.vue'
import ProfileView from '@/view/ProfileView.vue'
import { createRouter, createWebHistory } from 'vue-router'

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
  ],
})

export default router
