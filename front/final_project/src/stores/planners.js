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

  return { regions, generatedPlan, getLocations, generatePlan }
})