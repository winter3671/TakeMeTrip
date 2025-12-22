// src/stores/community.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAccountStore } from '@/stores/accounts'

export const useCommunityStore = defineStore('community', () => {
  const articles = ref([])
  const article = ref(null)
  const API_URL = 'http://127.0.0.1:8000/api/community'

  const getArticles = async (params = {}) => {
    try {
      const res = await axios.get(`${API_URL}/articles/`, { params })
      articles.value = res.data
    } catch (error) {
      console.error('게시글 목록 로드 실패:', error)
    }
  }
  
  const getArticleDetail = async (id) => {
    try {
      const res = await axios.get(`${API_URL}/articles/${id}/`)
      article.value = res.data
      return res.data
    } catch (error) {
      console.error('게시글 상세 로드 실패:', error)
    }
  }

  return { 
    articles, 
    article, 
    getArticles, 
    getArticleDetail,
    API_URL 
  }
})