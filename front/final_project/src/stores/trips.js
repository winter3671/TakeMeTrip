import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

export const useTripStore = defineStore('trip', () => {
  const accountStore = useAccountStore()
  
  // 백엔드 API URL (확인 필요)
  const API_URL = 'http://127.0.0.1:8000/api/trips'

  const categories = ref([])

  // 카테고리 목록 가져오기
  const getCategories = async () => {
    try {
      const res = await axios.get(`${API_URL}/categories/`)
      return res.data
    } catch (error) {
      console.error('카테고리 로드 실패:', error)
      return []
    }
  }

  // 상단 배너용 랜덤 추천
  const getRandomBannerTrips = async () => {
    try {
      const res = await axios.get(`${API_URL}/banner-random/`)
      return res.data
    } catch (error) {
      console.error('배너 로드 실패:', error)
      return []
    }
  }

  // 카테고리별 추천 (없으면 전체 랜덤)
  const getRandomTrips = async (category) => {
    try {
      const params = category ? { category } : {}
      const endpoint = category ? `${API_URL}/recommend/category/` : `${API_URL}/random/`
      const res = await axios.get(endpoint, { params })
      return res.data
    } catch (error) {
      console.error('추천 여행지 로드 실패:', error)
      return []
    }
  }

  // 내 찜 목록 가져오기
  const getMyWishlist = async () => {
    if (!accountStore.token) return []
    try {
      const res = await axios.get(`${API_URL}/my/wishlist/`, {
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      return res.data
    } catch (error) {
      console.error('찜 목록 로드 실패:', error)
      return []
    }
  }

  // 좋아요 토글
  const toggleLike = async (tripId) => {
    if (!accountStore.token) {
      alert('로그인이 필요합니다.')
      return null
    }

    try {
      const res = await axios.post(`${API_URL}/${tripId}/like/`, {}, {
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      return res.data.is_liked 
    } catch (error) {
      console.error('좋아요 실패:', error)
      return null
    }
  }

  const getAiRecommendations = async () => {
    try {
      const res = await axios.get(`${API_URL}/recommend/ai/`, {
        headers: {
          Authorization: `Bearer ${accountStore.token}` 
        }
      })
      return res.data
    } catch (error) {
      console.error('AI 추천 로드 실패:', error)
      return []
    }
  }

  return { 
    categories, 
    getCategories, 
    getRandomBannerTrips, 
    getRandomTrips, 
    getMyWishlist,
    toggleLike,
    getAiRecommendations
  }
})