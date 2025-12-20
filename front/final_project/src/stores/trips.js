import axios from 'axios'
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useTripStore = defineStore('trip', () => {
  const trips = ref([])
  const categories = ref([])
  const totalCount = ref(0)

  const API_URL = 'http://127.0.0.1:8000/api/trips/'

  const getTrips = async (params = {}) => {
    try {
      const res = await axios.get(API_URL, { params })
      trips.value = res.data.results ? res.data.results : res.data
      if (res.data.count) {
        totalCount.value = res.data.count
      }

      return trips.value
    } catch (error) {
      console.error('여행지 목록 로드 실패:', error)
      return []
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

  return {
    trips,
    categories,
    totalCount,
    getTrips,
    getCategories
  }
}, { persist: true })