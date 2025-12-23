<template>
  <div class="create-container">
    <h1 class="page-title">새 글 작성</h1>
    
    <form @submit.prevent="submitArticle" class="create-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input 
          type="text" 
          id="title" 
          v-model="title" 
          placeholder="제목을 입력해주세요"
          required
        >
      </div>

      <div class="form-group">
        <label for="content">내용</label>
        <textarea 
          id="content" 
          v-model="content" 
          placeholder="내용을 자유롭게 작성해주세요"
          required
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="image">사진 첨부</label>
        <input 
          type="file" 
          id="image" 
          @change="handleFileUpload" 
          accept="image/*"
        >
      </div>

      <div class="form-group">
        <label for="course-select">여행 코스 첨부 (선택)</label>
        <select id="course-select" v-model="courseId" class="course-select-box">
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
      </div> <div class="btn-group">
        <button type="button" class="cancel-btn" @click="goBack">취소</button>
        <button type="submit" class="submit-btn">등록하기</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAccountStore } from '@/stores/accounts'
import { useCommunityStore } from '@/stores/community';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const accountStore = useAccountStore();
const communityStore = useCommunityStore();

const title = ref('');
const content = ref('');
const imageFile = ref(null);
const courseId = ref(null);
const myCourses = ref([]);

const API_URL = 'http://127.0.0.1:8000';

const selectedCourse = computed(() => {
  return myCourses.value.find(c => c.id === courseId.value);
});

const groupedDetails = computed(() => {
  if (!selectedCourse.value || !selectedCourse.value.details) return {};

  const groups = {};
  selectedCourse.value.details.forEach(detail => {
    const day = detail.day;
    if (!groups[day]) {
      groups[day] = [];
    }
    groups[day].push(detail);
  });
  
  return Object.keys(groups).sort().reduce((acc, key) => {
    acc[key] = groups[key];
    return acc;
  }, {});
});

onMounted(async () => {
  try {
    const res = await axios.get(`${API_URL}/api/planner/courses/`, {
      headers: { Authorization: `Bearer ${accountStore.token}` }
    });
    myCourses.value = res.data;
  } catch (err) {
    console.error('코스 목록을 불러오지 못했습니다:', err);
  }
});

const getSelectedCourseTitle = () => {
  const selected = myCourses.value.find(c => c.id === courseId.value);
  return selected ? selected.title : '';
};

const handleFileUpload = (event) => {
  imageFile.value = event.target.files[0];
};

const submitArticle = async () => {
  if (!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 입력해주세요.');
    return;
  }

  const formData = new FormData();
  formData.append('title', title.value);
  formData.append('content', content.value);
  
  if (imageFile.value) {
    formData.append('image', imageFile.value);
  }
  
  if (courseId.value) {
    formData.append('course', courseId.value);
  }

  try {
    await axios.post(`${API_URL}/api/community/articles/`, formData, {
      headers: {
        Authorization: `Bearer ${accountStore.token}`,
        'Content-Type': 'multipart/form-data',
      },
    });
    
    router.push({ name: 'community' });
  } catch (err) {
    console.error(err);
    alert('게시글 작성 중 오류가 발생했습니다.');
  }
};

const goBack = () => {
  router.back();
};
</script>

<style scoped>
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

.course-select-box:focus {
  border-color: #7B9DFF;
}

.course-attachment {
  background-color: #e3f2fd;
  padding: 15px;
  border-radius: 8px;
  color: #1565c0;
  font-size: 15px;
  border: 1px solid #bbdefb;
  margin-top: -10px; /* form-group과의 간격 조절 */
}

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

.create-container {
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

.form-group input,
.form-group textarea {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #7B9DFF;
}

.form-group textarea {
  height: 300px;
  resize: none;
  line-height: 1.6;
}

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

.cancel-btn:hover {
  background-color: #e9ecef;
}

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

.submit-btn:hover {
  background-color: #5c85ff;
}

@media (max-width: 768px) {
  .create-container {
    margin: 20px;
    padding: 20px;
  }
}

.preview-itinerary {
  margin-top: 15px;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e1f5fe;
}

.day-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eee;
}

.day-row:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.day-label {
  background-color: #7B9DFF;
  color: white;
  font-weight: 700;
  font-size: 13px;
  padding: 4px 10px;
  border-radius: 15px;
  margin-right: 15px;
  flex-shrink: 0;
  min-width: 60px;
  text-align: center;
}

.day-spots {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.spot-item {
  display: inline-flex;
  align-items: center;
}

.arrow {
  color: #bbb;
  margin: 0 6px;
  font-size: 12px;
}
</style>