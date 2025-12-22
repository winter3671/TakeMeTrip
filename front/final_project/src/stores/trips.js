import axios from 'axios'
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAccountStore } from './accounts'

export const useTripStore = defineStore('trip', () => {
  const trips = ref([])
  const categories = ref([])
  const totalCount = ref(0)

  const API_URL = 'http://127.0.0.1:8000/api/trips/'

  const getTrips = async (params = {}) => {
    try {
      const res = await axios.get(API_URL, { params })
      trips.value = res.data.results ? res.data.results : res.data
      if (res.data.count !== undefined) {
        totalCount.value = res.data.count
      }
      return trips.value
    } catch (error) {
      console.error('여행지 목록 로드 실패:', error)
      return []
    }
  }

  const getRandomBannerTrips = async () => {
    try {
      const res = await axios.get(`${API_URL}banner-random/`)
      return res.data
    } catch (error) {
      console.error('배너 데이터 로드 실패:', error)
      return []
    }
  }

  const getRandomTrips = async (categoryId = null) => {
    try {
      const params = { count: 10 };
      if (categoryId) params.category = categoryId;

      const res = await axios.get(`${API_URL}random/`, { params });
      return res.data;
    } catch (error) {
      console.error('랜덤 추천 로드 실패:', error);
      return [];
    }
  }

  const getCategories = async () => {
    try {
      if (categories.value.length > 0) return categories.value

      const res = await axios.get(`${API_URL}categories/`)
      categories.value = res.data
      return res.data
    } catch (error) {
      console.error('카테고리 로드 실패:', error)
      return []
    }
  }

  // ✅ 수정: my-wishlist/ → my/wishlist/ (Django URL과 일치)
  // ✅ 수정: 헤더에 토큰 추가
  const getMyWishlist = async () => {
    const accountStore = useAccountStore()  // ✅ 함수 내부에서 호출
    
    try {
      const res = await axios({
        method: 'get',
        url: `${API_URL}my/wishlist/`,  // ✅ 경로 수정
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      return res.data.results ? res.data.results : res.data
    } catch (error) {
      console.error('찜 목록 로드 실패:', error)
      return []
    }
  }

  const toggleLike = async (tripId) => {
    const accountStore = useAccountStore()
    
    if (!accountStore.isLogin) { 
      alert('로그인이 필요합니다.')
      return null
    }

    try {
      const res = await axios({
        method: 'post',
        url: `${API_URL}${tripId}/like/`, 
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      return res.data.is_liked
    } catch (error) {
      console.error('좋아요 실패:', error)
      if (error.response?.status === 401) {
        alert('로그인이 만료되었습니다.')
      }
      return null
    }
  }

  return {
    trips,
    categories,
    totalCount,
    getTrips,
    getCategories,
    getRandomBannerTrips,
    getRandomTrips,
    getMyWishlist,
    toggleLike
  }
}, { persist: true })