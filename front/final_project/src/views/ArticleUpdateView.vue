<template>
  <div class="update-container">
    <h1 class="page-title">게시글 수정</h1>
    
    <form @submit.prevent="updateArticle" class="create-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="articleData.title" 
          placeholder="제목을 입력해주세요"
          required
        >
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="articleData.content" 
          placeholder="내용을 자유롭게 작성해주세요"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label for="image">사진 첨부</label>
        
        <div v-if="previewImage || (article.image && !isImageCleared)" class="image-preview-container">
          <img :src="previewImage || `${API_URL}${article.image}`" alt="미리보기" class="image-preview">
          <button type="button" @click="clearImage" class="clear-image-btn">사진 삭제</button>
        </div>

        <input 
          type="file" 
          id="image" 
          @change="handleFileUpload" 
          accept="image/*"
          ref="fileInput"
        >
        <p v-if="article.image && !imageFile && !isImageCleared" class="help-text">
          * 새 이미지를 선택하지 않으면 기존 이미지가 유지됩니다.
        </p>
        <p v-if="isImageCleared" class="help-text delete-msg">
          * 수정 완료 시 이미지가 삭제됩니다.
        </p>
      </div>

      <div class="form-group">
        <label for="course-select">여행 코스 첨부 (선택)</label>
        <select id="course-select" v-model="articleData.courseId" class="course-select-box">
          <option :value="null">-- 코스를 선택하지 않음 --</option>
          <option v-for="course in myCourses" :key="course.id" :value="course.id">
            [{{ course.region }}] {{ course.title }} ({{ course.start_date }} ~ {{ course.end_date }})
          </option>
        </select>
      </div>
      
      <div v-if="selectedCourse" class="selected-course-preview">
        <div class="preview-header">
          <span class="preview-badge">선택된 코스</span>
          <span class="preview-title">{{ selectedCourse.title }}</span>
        </div>
        <div class="preview-info">
          📍 {{ selectedCourse.region }} | 📅 {{ selectedCourse.start_date }} ~ {{ selectedCourse.end_date }}
        </div>
        
        <div class="preview-itinerary" v-if="selectedCourse.details && selectedCourse.details.length > 0">
          <div v-for="(spots, day) in groupedDetails" :key="day" class="day-row">
            <div class="day-label">Day {{ day }}</div>
            <div class="day-spots">
              <span v-for="(detail, idx) in spots" :key="detail.id" class="spot-item">
                {{ detail.trip_name || (detail.trip ? detail.trip.title : '여행지') }}
                <span v-if="idx < spots.length - 1" class="arrow">→</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="btn-group">
        <button type="button" class="cancel-btn" @click="goBack">취소</button>
        <button type="submit" class="submit-btn">수정 완료</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCommunityStore } from '@/stores/community';
import { useAccountStore } from '@/stores/accounts';
import { storeToRefs } from 'pinia';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const communityStore = useCommunityStore();
const accountStore = useAccountStore();
const { article } = storeToRefs(communityStore);

const articleId = route.params.id;
const API_URL = 'http://127.0.0.1:8000';

const articleData = ref({
  title: '',
  content: '',
  courseId: null,
});

const imageFile = ref(null);
const previewImage = ref(null);
const fileInput = ref(null);
const myCourses = ref([]);
const isImageCleared = ref(false); // 기존 이미지 삭제 여부

// 선택된 코스 정보 (원본 코스 목록에서 찾음)
const selectedCourse = computed(() => {
  return myCourses.value.find(c => c.id === articleData.value.courseId);
});

// 코스 상세 정보 그룹화
const groupedDetails = computed(() => {
  if (!selectedCourse.value || !selectedCourse.value.details) return {};
  const groups = {};
  selectedCourse.value.details.forEach(detail => {
    const day = detail.day;
    if (!groups[day]) groups[day] = [];
    groups[day].push(detail);
  });
  return Object.keys(groups).sort().reduce((acc, key) => {
    acc[key] = groups[key];
    return acc;
  }, {});
});

onMounted(async () => {
  // 1. 코스 목록 불러오기
  try {
    const res = await axios.get(`${API_URL}/api/planner/courses/`, {
      headers: { Authorization: `Bearer ${accountStore.token}` }
    });
    myCourses.value = res.data;
  } catch (err) {
    console.error('코스 목록 로드 실패:', err);
  }

  // 2. 게시글 상세 정보 불러오기 및 초기화
  if (!article.value || article.value.id != articleId) {
    await communityStore.getArticleDetail(articleId);
  }
  
  articleData.value.title = article.value.title;
  articleData.value.content = article.value.content;
  // 기존 코스가 있다면 초기값 설정
  articleData.value.courseId = article.value.course ? article.value.course.id : null;
});

// 파일 선택 시 미리보기 설정
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    imageFile.value = file;
    previewImage.value = URL.createObjectURL(file);
    isImageCleared.value = false;
  }
};

// 이미지 삭제 버튼 클릭 시
const clearImage = () => {
  imageFile.value = null;
  previewImage.value = null;
  isImageCleared.value = true;
  if (fileInput.value) {
    fileInput.value.value = ''; // input file 초기화
  }
};

const updateArticle = async () => {
  if(!articleData.value.title.trim() || !articleData.value.content.trim()) {
    alert('제목과 내용을 모두 입력해주세요.');
    return;
  }

  // FormData 객체 생성 (이미지 전송을 위해)
  const formData = new FormData();
  formData.append('title', articleData.value.title);
  formData.append('content', articleData.value.content);

  // 새 이미지가 선택되었으면 추가
  if (imageFile.value) {
    formData.append('image', imageFile.value);
  } 
  // 이미지를 삭제했으면 삭제 플래그 전송 (백엔드 처리 필요)
  else if (isImageCleared.value) {
    formData.append('image_clear', 'true');
  }

  // 코스 선택 여부 추가
  if (articleData.value.courseId) {
    formData.append('course', articleData.value.courseId);
  } else {
     // 코스 선택 해제 시 (null 값 전송) - 백엔드에서 처리 필요
     formData.append('course', ''); 
  }

  // Store 액션 대신 직접 Axios 호출 (FormData 전송을 위해)
  try {
    await axios.put(`${API_URL}/api/community/articles/${articleId}/`, formData, {
      headers: {
        Authorization: `Bearer ${accountStore.token}`,
        'Content-Type': 'multipart/form-data',
      }
    });
    alert('게시글이 수정되었습니다.');
    await communityStore.getArticleDetail(articleId); // 데이터 갱신
    router.push({ name: 'article-detail', params: { id: articleId } });
  } catch (error) {
    console.error('게시글 수정 실패:', error);
    alert('게시글 수정 중 오류가 발생했습니다.');
  }
};

const goBack = () => {
  router.back();
};
</script>

<style scoped>
/* ArticleCreateView와 동일한 스타일 적용 */
.update-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  font-family: 'Noto Sans KR', sans-serif;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.form-group input[type="text"],
.form-group textarea {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  border-color: #7B9DFF;
}

.form-group textarea {
  height: 300px;
  resize: none;
  line-height: 1.6;
}

/* 이미지 미리보기 스타일 */
.image-preview-container {
  margin-bottom: 10px;
  position: relative;
  display: inline-block;
}

.image-preview {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.clear-image-btn {
  margin-top: 5px;
  padding: 5px 10px;
  background-color: #ff6b6b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.help-text {
  font-size: 13px;
  color: #888;
  margin-top: 5px;
}

/* 코스 선택 및 미리보기 스타일 */
.course-select-box {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  background-color: white;
  outline: none;
  cursor: pointer;
}
.course-select-box:focus { border-color: #7B9DFF; }

.selected-course-preview {
  margin-top: 10px;
  background-color: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 8px;
  padding: 15px;
}
.preview-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.preview-badge { background-color: #2196f3; color: white; font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.preview-title { font-weight: bold; color: #1565c0; font-size: 16px; }
.preview-info { font-size: 14px; color: #555; margin-bottom: 10px; }
.preview-itinerary { margin-top: 15px; background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e1f5fe; }
.day-row { display: flex; align-items: baseline; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed #eee; }
.day-row:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.day-label { background-color: #7B9DFF; color: white; font-weight: 700; font-size: 13px; padding: 4px 10px; border-radius: 15px; margin-right: 15px; flex-shrink: 0; min-width: 60px; text-align: center; }
.day-spots { display: flex; flex-wrap: wrap; gap: 6px; font-size: 14px; color: #333; line-height: 1.6; }
.spot-item { display: inline-flex; align-items: center; }
.arrow { color: #bbb; margin: 0 6px; font-size: 12px; }

/* 버튼 그룹 스타일 */
.btn-group {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 10px;
}

.cancel-btn {
  padding: 12px 30px;
  background-color: #f1f3f5;
  color: #495057;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.cancel-btn:hover { background-color: #e9ecef; }

.submit-btn {
  padding: 12px 30px;
  background-color: #7B9DFF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.submit-btn:hover { background-color: #5c85ff; }

@media (max-width: 768px) {
  .update-container {
    margin: 20px;
    padding: 20px;
  }
}
</style>