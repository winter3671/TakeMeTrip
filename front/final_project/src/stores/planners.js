// src/stores/planners.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

export const usePlannerStore = defineStore('planner', () => {
  const accountStore = useAccountStore()
  const API_URL = 'http://127.0.0.1:8000/api/planner'

  const regions = ref([])
  const generatedPlan = ref(null)

  const getLocations = async () => {
    try {
      const res = await axios.get(`${API_URL}/locations/`)
      regions.value = res.data
    } catch (error) {
      console.error('지역 목록 로드 실패:', error)
    }
  }

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

    if (!generatedPlan.value) {
      alert('생성된 플랜이 없습니다.')
      return false
    }

    const regionObj = regions.value.find(r => r.id === formData.region_id)
    const regionName = regionObj ? regionObj.name : 'Unknown'

    const payload = {
      title: courseTitle,
      region: regionName,
      start_date: formData.start_date,
      end_date: formData.end_date,
      plan: generatedPlan.value.plan
    }

    try {
      const res = await axios.post(`${API_URL}/save/`, payload, {
        headers: {
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      
      alert('여행 코스가 저장되었습니다! 🗺️')
      return true
    } catch (error) {
      console.error('=== 코스 저장 실패 ===')
      console.error('error:', error)
      console.error('error.response:', error.response)
      console.error('error.response.data:', error.response?.data)
      
      if (error.response?.data) {
        alert(`코스 저장 실패: ${JSON.stringify(error.response.data)}`)
      } else {
        alert('코스 저장 중 오류가 발생했습니다.')
      }
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