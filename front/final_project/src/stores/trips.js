import axios from 'axios'
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useTripStore = defineStore('trip', () => {
  const trips = ref([])
  const categories = ref([])

  const API_URL = 'http://127.0.0.1:8000/api/trips/'

  const getTrips = async (params = {}) => {
    try {
      const res = await axios.get(API_URL, { params })
      if (Object.keys(params).length === 0) {
        trips.value = res.data.results ? res.data.results : res.data
      }
      return res.data.results ? res.data.results : res.data
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
    getTrips,
    getCategories
  }
}, { persist: true })