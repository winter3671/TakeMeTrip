import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

// ★ [수정 1] 파일명 'accounts.js'로 정확히 import (s가 붙어있는지 확인)
import { useAccountStore } from '@/stores/accounts' 

export const useCommunityStore = defineStore('community', () => {
  const router = useRouter()
  
  // ★ [수정 2] 여기서 accountStore를 반드시 선언해야 아래 함수들에서 쓸 수 있습니다.
  const accountStore = useAccountStore()
  
  const articles = ref([])
  const article = ref(null)

  // API URL 확인 (http://127.0.0.1:8000/api/community)
  const API_URL = 'http://127.0.0.1:8000/api/community'

  // 게시글 목록 조회
  const getArticles = async (params = {}) => {
    try {
      const res = await axios.get(`${API_URL}/articles/`, { params })
      articles.value = res.data
    } catch (error) {
      console.error('게시글 목록 로드 실패:', error)
    }
  }

  // 게시글 상세 조회
  const getArticleDetail = async (id) => {
    try {
      const res = await axios.get(`${API_URL}/articles/${id}/`)
      article.value = res.data
    } catch (error) {
      console.error('상세 정보 로드 실패:', error)
    }
  }

  // 게시글 삭제
  const deleteArticle = async (id) => {
    try {
      if(!confirm('정말 삭제하시겠습니까?')) return

      await axios.delete(`${API_URL}/articles/${id}/`, {
        headers: {
          // ★ Token -> Bearer 로 변경
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      alert('게시글이 삭제되었습니다.')
      router.push({ name: 'community' }) 
    } catch (error) {
      console.error('삭제 실패:', error)
      alert('삭제 권한이 없거나 오류가 발생했습니다.')
    }
  }

  // 2. 게시글 생성 (수정됨)
  const createArticle = async (payload) => {
    try {
      const res = await axios.post(`${API_URL}/articles/`, payload, {
        headers: {
          // ★ Token -> Bearer 로 변경
          Authorization: `Bearer ${accountStore.token}` 
        }
      })
      
      alert('게시글이 등록되었습니다!')
      router.push({ name: 'community' }) 
    } catch (error) {
      console.error('게시글 작성 실패:', error)
      alert('게시글 작성 중 오류가 발생했습니다.')
    }
  }

  // 3. 댓글 작성 (수정됨)
  const createComment = async (articleId, content) => {
    try {
      await axios.post(`${API_URL}/articles/${articleId}/comments/`, { content }, {
        headers: {
          // ★ Token -> Bearer 로 변경
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      await getArticleDetail(articleId)
    } catch (error) {
      console.error('댓글 작성 실패:', error)
      alert('댓글 작성에 실패했습니다.')
    }
  }

  // 4. 좋아요 (수정됨)
  const likeArticle = async (articleId) => {
    try {
      const res = await axios.post(`${API_URL}/articles/${articleId}/likes/`, {}, {
        headers: {
          // ★ Token -> Bearer 로 변경
          Authorization: `Bearer ${accountStore.token}`
        }
      })
      
      if (article.value) {
        article.value.like_count = res.data.count
      }
    } catch (error) {
      console.error('좋아요 요청 실패:', error)
      if (error.response && error.response.status === 401) {
        alert('로그인이 필요합니다.')
      }
    }
  }

  return { 
    articles, 
    article, 
    getArticles, 
    getArticleDetail, 
    deleteArticle,
    createArticle,
    createComment,
    likeArticle,
    API_URL 
  }
})