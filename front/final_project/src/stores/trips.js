import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

export const useTripStore = defineStore('trip', () => {
  const accountStore = useAccountStore()
  const API_URL = 'http://127.0.0.1:8000/api/trips'

  // 상태 변수 (State)
  const trips = ref([])        // ★ 게시글 목록 (InformationView용)
  const totalCount = ref(0)    // ★ 전체 게시글 수 (페이지네이션용)
  const categories = ref([])

  // 1. 여행지 목록 조회 (필터링, 페이징 포함) - ★ 복구된 함수
  const getTrips = async (params) => {
    try {
      const res = await axios.get(`${API_URL}/`, { params })
      
      // DRF 페이지네이션 응답 구조 ({ count: 100, results: [...] }) 처리
      if (res.data.results) {
        trips.value = res.data.results
        totalCount.value = res.data.count
      } else {
        // 페이지네이션이 없을 경우
        trips.value = res.data
        totalCount.value = res.data.length
      }
    } catch (error) {
      console.error('여행지 목록 로드 실패:', error)
      trips.value = [] // 에러 시 빈 배열로 초기화
      totalCount.value = 0
    }
  }

  // 2. 카테고리 목록 조회
  const getCategories = async () => {
    try {
      const res = await axios.get(`${API_URL}/categories/`)
      return res.data
    } catch (error) {
      console.error('카테고리 로드 실패:', error)
      return []
    }
  }

  // 3. 배너용 랜덤 추천
  const getRandomBannerTrips = async () => {
    try {
      const res = await axios.get(`${API_URL}/banner-random/`)
      return res.data
    } catch (error) {
      console.error('배너 로드 실패:', error)
      return []
    }
  }

  // 4. 홈 화면 추천 (카테고리별 or 전체 랜덤)
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

  // 5. 내 찜 목록 조회
  const getMyWishlist = async () => {
    if (!accountStore.token) return []
    try {
      const res = await axios.get(`${API_URL}/my/wishlist/`, {
        headers: { Authorization: `Bearer ${accountStore.token}` }
      })
      return res.data
    } catch (error) {
      console.error('찜 목록 로드 실패:', error)
      return []
    }
  }

  // 6. 좋아요 토글
  const toggleLike = async (tripId) => {
    if (!accountStore.token) {
      alert('로그인이 필요합니다.')
      return null
    }
    try {
      const res = await axios.post(`${API_URL}/${tripId}/like/`, {}, {
        headers: { Authorization: `Bearer ${accountStore.token}` }
      })
      return res.data.is_liked 
    } catch (error) {
      console.error('좋아요 실패:', error)
      return null
    }
  }

  // 7. AI 추천
  const getAiRecommendations = async () => {
    try {
      const res = await axios.get(`${API_URL}/recommend/ai/`, {
        headers: { Authorization: `Bearer ${accountStore.token}` }
      })
      return res.data
    } catch (error) {
      console.error('AI 추천 로드 실패:', error)
      return []
    }
  }

const getMyCourses = async () => {
  const accountStore = useAccountStore()
  
  console.log('=== getMyCourses 호출 ===')
  console.log('accountStore.token:', accountStore.token)
  
  if (!accountStore.token) {
    console.log('토큰 없음 - 로그인 필요')
    return []
  }

  try {
    console.log('코스 목록 요청:', `${API_URL}/courses/`)
    
    const res = await axios({
      method: 'get',
      url: `${API_URL}/courses/`,
      headers: { 
        Authorization: `Bearer ${accountStore.token}` 
      }
    })
    
    console.log('=== 코스 API 원본 응답 ===')
    console.log('res.data:', res.data)
    console.log('res.status:', res.status)
    
    // DRF pagination 처리
    let courses = res.data.results ? res.data.results : res.data
    
    console.log('courses 타입:', typeof courses)
    console.log('courses 배열 여부:', Array.isArray(courses))
    console.log('courses 길이:', courses.length)
    console.log('courses 내용:', courses)
    
    // 배열인지 확인
    if (!Array.isArray(courses)) {
      console.error('코스 데이터가 배열이 아닙니다:', courses)
      return []
    }
    
    // null이나 undefined 제거
    const validCourses = courses.filter(course => {
      if (!course) {
        console.warn('null 또는 undefined 코스 발견')
        return false
      }
      if (!course.id) {
        console.warn('ID 없는 코스:', course)
        return false
      }
      return true
    })
    
    console.log('유효한 코스 개수:', validCourses.length)
    console.log('유효한 코스 목록:', validCourses)
    
    return validCourses
    
  } catch (error) {
    console.error('=== 코스 목록 로드 실패 ===')
    console.error('error:', error)
    console.error('error.response:', error.response)
    console.error('error.response?.data:', error.response?.data)
    console.error('error.response?.status:', error.response?.status)
    return []
  }
}

  return { 
    trips, 
    totalCount, 
    categories,
    getTrips,
    getCategories, 
    getRandomBannerTrips, 
    getRandomTrips, 
    getMyWishlist,
    toggleLike,
    getAiRecommendations,
    getMyCourses
  }
})