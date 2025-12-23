// src/stores/planners.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

export const usePlannerStore = defineStore('planner', () => {
  const accountStore = useAccountStore()
  const API_URL = 'http://127.0.0.1:8000/api/planners'

  const regions = ref([]) // 지역/도시 데이터 저장
  const generatedPlan = ref(null) // 생성된 계획 저장

  // 1. 지역/도시 목록 가져오기
  const getLocations = async () => {
    try {
      const res = await axios.get(`${API_URL}/locations/`)
      regions.value = res.data
    } catch (error) {
      console.error('지역 목록 로드 실패:', error)
    }
  }

  // 2. AI 플랜 생성 요청
  const generatePlan = async (payload) => {
    if (!accountStore.token) {
      alert('로그인이 필요합니다.')
      return null
    }

    try {
      const res = await axios.post(`${API_URL}/generate/`, payload, {
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      generatedPlan.value = res.data
      return res.data
    } catch (error) {
      console.error('플랜 생성 실패:', error)
      if (error.response) {
        if (error.response.status >= 500 || typeof error.response.data === 'string') {
          alert("서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
        } else {
          alert(JSON.stringify(error.response.data))
        }
      } else {
        alert("네트워크 오류가 발생했습니다.")
      }
      return null
    }
  }

  const saveCourse = async (courseTitle, formData) => {
    if (!accountStore.token) {
      alert('로그인이 필요합니다.')
      return false
    }

    if (!generatedPlan.value) return false

    // 1. 백엔드로 보낼 데이터 가공
    // Course 모델 필드: title, region, start_date, end_date
    // CourseDetail 모델 필드: trip_id, day, order
    
    // 지역 이름 찾기 (region_id로)
    const regionObj = regions.value.find(r => r.id === formData.region_id)
    const regionName = regionObj ? regionObj.name : 'Unknown'

    const payload = {
      title: courseTitle,
      region: regionName,
      start_date: formData.start_date,
      end_date: formData.end_date,
      // 상세 일정 데이터를 리스트로 변환
      details: [] 
    }

    // generatedPlan.plan 구조를 순회하며 details 배열 채우기
    generatedPlan.value.plan.forEach((dayPlan) => {
      dayPlan.schedule.forEach((item, index) => {
        // item.data.id는 Trip 모델의 ID여야 함
        if (item.data && item.data.id) {
          payload.details.push({
            trip_id: item.data.id,
            day: dayPlan.day,
            order: index + 1 // 순서 (1부터 시작)
          })
        }
      })
    })

    // 2. API 전송
    try {
      const res = await axios.post(`${API_URL}/save/`, payload, {
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      alert('여행 코스가 저장되었습니다! 🗺️')
      return true
    } catch (error) {
      console.error('코스 저장 실패:', error)
      alert('코스 저장 중 오류가 발생했습니다.')
      return false
    }
  }

  return { 
    regions, 
    generatedPlan, 
    getLocations, 
    generatePlan,
    saveCourse
  }
})