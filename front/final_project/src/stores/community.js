// src/stores/community.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useCommunityStore = defineStore('community', () => {
  const router = useRouter()
  const articles = ref([])
  const article = ref(null)
  
  const API_URL = 'http://127.0.0.1:8000/api/community' 

  // 1. 게시글 목록 조회
  const getArticles = async (params = {}) => {
    try {
      const res = await axios.get(`${API_URL}/articles/`, { params })
      articles.value = res.data
    } catch (error) {
      console.error('게시글 목록 로드 실패:', error)
    }
  }

  // 2. 게시글 상세 조회
  const getArticleDetail = async (id) => {
    try {
      const res = await axios.get(`${API_URL}/articles/${id}/`)
      article.value = res.data
    } catch (error) {
      console.error('상세 정보 로드 실패:', error)
    }
  }

  // 3. 게시글 삭제
  const deleteArticle = async (id) => {
    try {
      if(!confirm('정말 삭제하시겠습니까?')) return

      await axios.delete(`${API_URL}/articles/${id}/`)
      alert('게시글이 삭제되었습니다.')
      router.push({ name: 'community' })
    } catch (error) {
      console.error('삭제 실패:', error)
      alert('삭제 권한이 없거나 오류가 발생했습니다.')
    }
  }

  // 4. 댓글 작성
  const createComment = async (articleId, content) => {
    try {
      await axios.post(`${API_URL}/articles/${articleId}/comments/`, { content })
      // 댓글 작성 후 상세 정보 다시 불러와서 화면 갱신
      await getArticleDetail(articleId)
    } catch (error) {
      console.error('댓글 작성 실패:', error)
      alert('댓글 작성에 실패했습니다.')
    }
  }

  // 5. 좋아요 토글
  const likeArticle = async (articleId) => {
    try {
      const res = await axios.post(`${API_URL}/articles/${articleId}/likes/`)
      // 백엔드에서 { liked: boolean, count: int } 를 리턴한다고 가정
      if (article.value) {
        article.value.like_count = res.data.count
        // 내가 좋아요 눌렀는지 여부 업데이트 로직은 백엔드 응답 구조에 따라 추가 처리 가능
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
    createComment,
    likeArticle
  }
})