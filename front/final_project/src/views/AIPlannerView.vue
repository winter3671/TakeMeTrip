<template>
  <div class="planner-container">
    
    <div class="planner-header">
      <div class="icon-wrapper">
        <span class="header-emoji">✨</span>
      </div>
      <h1>AI 여행 플래너</h1>
      <p>날짜와 장소만 알려주세요. 나머지는 AI가 완벽하게 계획해 드릴게요.</p>
    </div>

    <div v-if="!plannerStore.generatedPlan" class="form-card">
      
      <div class="form-group">
        <label class="form-label"><span class="icon">📅</span> 여행 일정</label>
        <div class="date-inputs">
          <div class="input-wrapper">
            <span class="sub-label">가는 날</span>
            <input 
              type="date" 
              v-model="formData.start_date" 
              class="custom-input" 
              :min="minDate"
            />
          </div>
          <span class="tilde">~</span>
          <div class="input-wrapper">
            <span class="sub-label">오는 날</span>
            <input 
              type="date" 
              v-model="formData.end_date" 
              class="custom-input" 
              :min="minEndDate"
            />
          </div>
        </div>
      </div>

      <hr class="divider">

      <div class="form-group">
        <label class="form-label"><span class="icon">📍</span> 여행지 선택</label>
        <div class="select-row">
          <select v-model="formData.region_id" @change="handleRegionChange" class="custom-select">
            <option :value="null">시/도 선택</option>
            <option v-for="region in plannerStore.regions" :key="region.id" :value="region.id">
              {{ region.name }}
            </option>
          </select>
          
          <select v-model="formData.city_id" class="custom-select" :disabled="!formData.region_id">
            <option :value="null">군/구 선택</option>
            <option v-for="city in availableCities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
        </div>
      </div>

      <hr class="divider">

      <div class="form-group">
        <label class="form-label"><span class="icon">👥</span> 여행 인원</label>
        <div class="people-counter">
          <button @click="decrementPeople" class="counter-btn" :disabled="formData.num_people <= 1">-</button>
          <span class="people-display">{{ formData.num_people }}명</span>
          <button @click="incrementPeople" class="counter-btn">+</button>
        </div>
      </div>

      <button 
        class="generate-btn" 
        :class="{ 'loading': isGenerating }" 
        @click="handleGenerate"
        :disabled="isGenerating"
      >
        <span v-if="!isGenerating">AI 여행 계획 만들기 ✨</span>
        <span v-else class="loading-content">
          <span class="spinner"></span>
          AI가 최적의 경로를 계산 중입니다...
        </span>
      </button>
    </div>

    <div v-else class="result-container">
      
      <div v-if="isGenerating" class="loading-overlay">
        <div class="loading-box">
          <div class="spinner lg"></div>
          <p>새로운 경로를 찾고 있어요...</p>
        </div>
      </div>

      <div class="result-header">
        <h2>🎉 여행 계획이 완성되었습니다!</h2>
        <p>총 {{ plannerStore.generatedPlan.duration }}일간의 여정</p>
        
        <div class="header-actions">
          <button class="refresh-btn" @click="refreshPlan" :disabled="isGenerating">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"/>
              <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"/>
            </svg>
            다른 코스 추천받기
          </button>
          
          <button class="save-btn" @click="handleSaveCourse" :disabled="isGenerating">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7.5 9.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1z"/>
            </svg>
            내 코스로 저장
          </button>
          
          <button class="reset-btn" @click="resetPlanner" :disabled="isGenerating">조건 다시 설정</button>
        </div>
      </div>

      <div class="timeline-wrapper">
        <div v-for="dayPlan in plannerStore.generatedPlan.plan" :key="dayPlan.day" class="day-section">
          <div class="day-badge">Day {{ dayPlan.day }} <span class="day-date">{{ dayPlan.date }}</span></div>
          
          <div class="timeline">
            <div v-for="(item, idx) in dayPlan.schedule" :key="idx" class="timeline-item">
              <div class="time-col">{{ item.time }}</div>
              
              <div class="marker-col">
                <div class="line" v-if="idx !== dayPlan.schedule.length - 1"></div>
                <div class="dot" :class="item.type"></div>
              </div>

              <div class="content-col" @click="goToDetail(item.data.id)">
                <div class="place-card">
                  <img :src="item.data.thumbnail_image || '/src/assets/no_image.png'" class="place-img">
                  <div class="place-info">
                    <span class="place-type">{{ translateType(item.type) }}</span>
                    <h4>{{ item.data.title }}</h4>
                    <p>{{ item.data.region_name }} {{ item.data.city_name }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="plannerStore.generatedPlan.recommended_accommodation" class="acc-recommend">
        <h3>🏠 추천 숙소</h3>
        <div class="place-card acc-card" @click="goToDetail(plannerStore.generatedPlan.recommended_accommodation.id)">
           <img :src="plannerStore.generatedPlan.recommended_accommodation.thumbnail_image || '/src/assets/no_image.png'" class="place-img">
           <div class="place-info">
             <h4>{{ plannerStore.generatedPlan.recommended_accommodation.title }}</h4>
             <p>이 코스에 가장 최적화된 숙소입니다.</p>
           </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { usePlannerStore } from '@/stores/planners';
import { useAccountStore } from '@/stores/accounts'; // ★ 추가: 로그인 체크용

const router = useRouter();
const plannerStore = usePlannerStore();
const accountStore = useAccountStore(); // ★ 추가

const formData = ref({
  start_date: '',
  end_date: '',
  region_id: null,
  city_id: null,
  num_people: 2,
  current_mapx: 0.0,
  current_mapy: 0.0
});

const isGenerating = ref(false);

// 날짜 제한 계산
const getTodayDate = () => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};
const minDate = getTodayDate();
const minEndDate = computed(() => formData.value.start_date || minDate);

const availableCities = computed(() => {
  if (!formData.value.region_id) return [];
  const region = plannerStore.regions.find(r => r.id === formData.value.region_id);
  return region ? region.cities : [];
});

const handleRegionChange = () => {
  formData.value.city_id = null;
};

const incrementPeople = () => formData.value.num_people++;
const decrementPeople = () => { if (formData.value.num_people > 1) formData.value.num_people--; };

const getCurrentPosition = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      resolve({ lat: 37.5665, lon: 126.9780 }); 
    } else {
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        (err) => {
          console.warn("위치 정보 실패", err);
          resolve({ lat: 37.5665, lon: 126.9780 }); 
        }
      );
    }
  });
};

const handleGenerate = async () => {
  if (!formData.value.start_date || !formData.value.end_date) return alert('일정을 선택해주세요.');
  if (formData.value.start_date > formData.value.end_date) return alert('오는 날은 가는 날보다 빠를 수 없습니다.');
  if (!formData.value.region_id || !formData.value.city_id) return alert('여행지를 선택해주세요.');

  isGenerating.value = true;

  if (formData.value.current_mapx === 0.0) {
    const pos = await getCurrentPosition();
    formData.value.current_mapy = pos.lat; 
    formData.value.current_mapx = pos.lon; 
  }

  await plannerStore.generatePlan(formData.value);
  isGenerating.value = false;
};

// 새로고침
const refreshPlan = () => {
  handleGenerate();
};

// ★ [추가] 코스 저장 핸들러
const handleSaveCourse = async () => {
  if (!accountStore.isLogin) {
    alert("로그인이 필요합니다.");
    router.push({ name: 'login' });
    return;
  }

  // 코스 제목 입력받기
  const defaultTitle = `${formData.value.start_date} ${availableCities.value.find(c=>c.id === formData.value.city_id)?.name || '여행'}`;
  const title = prompt("이 여행 코스의 이름을 입력해주세요.", defaultTitle);
  
  if (title) {
    const success = await plannerStore.saveCourse(title, formData.value);
    if (success) {
      if (confirm("저장된 코스를 확인하시겠습니까?")) {
        router.push({ name: 'profile' });
      }
    }
  }
};

const resetPlanner = () => {
  plannerStore.generatedPlan = null;
};

const goToDetail = (id) => {
  router.push({ name: 'detail', params: { id } });
};

const translateType = (type) => {
  const map = { 'spot': '관광', 'meal': '식사', 'accommodation': '숙소' };
  return map[type] || type;
};

onMounted(() => {
  plannerStore.getLocations();
});
</script>

<style scoped>
.planner-container { 
  max-width: 600px; 
  margin: 60px auto; 
  padding: 0 20px; 
  font-family: 'Noto Sans KR', 
  sans-serif; 
  min-height: 80vh; 
}

.planner-header { 
  text-align: center; 
  margin-bottom: 40px; 
}

.icon-wrapper { 
  width: 60px; 
  height: 60px; 
  background: linear-gradient(135deg, #7B9DFF, #a1c4fd); 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  margin: 0 auto 15px; 
  box-shadow: 0 4px 15px rgba(123, 157, 255, 0.4); 
}

.header-emoji { 
  font-size: 28px; 
}

.planner-header h1 { 
  font-size: 28px; 
  font-weight: 800; 
  color: #333; 
  margin-bottom: 8px; 
}

.planner-header p { 
  color: #666; 
  font-size: 15px; 
}

.form-card { 
  background: white; 
  padding: 30px; 
  border-radius: 20px; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
  border: 1px solid #f0f0f0; 
}

.form-group { 
  margin-bottom: 20px; 
}

.form-label { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  font-size: 16px; 
  font-weight: 700; 
  color: #333; 
  margin-bottom: 12px; 
}

.date-inputs { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  gap: 10px; 
}

.input-wrapper { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  gap: 5px; 
}

.sub-label { 
  font-size: 12px; 
  color: #888; 
  font-weight: 500; 
}

.custom-input { 
  width: 100%; 
  padding: 12px; 
  border: 1px solid #ddd; 
  border-radius: 10px; 
  font-size: 14px; 
  outline: none; 
  background-color: #f9f9f9; 
}

.select-row { 
  display: flex; 
  gap: 10px; 
}

.custom-select { 
  flex: 1; 
  padding: 12px; 
  border: 1px solid #ddd; 
  border-radius: 10px; 
  font-size: 14px; 
  outline: none; 
  background-color: #fff; 
}

.people-counter { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  background-color: #f9f9f9; 
  border-radius: 10px; 
  padding: 5px; 
  border: 1px solid #eee; 
}

.counter-btn { 
  width: 40px; 
  height: 40px; 
  border: none; 
  background-color: white; 
  border-radius: 8px; 
  font-size: 20px; 
  color: #555; 
  cursor: pointer; 
  box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
}

.counter-btn:hover:not(:disabled) { 
  background-color: #7B9DFF; 
  color: white; 
}

.generate-btn { 
  width: 100%; 
  margin-top: 30px; 
  padding: 16px; 
  background: linear-gradient(90deg, #7B9DFF, #6b8cef); 
  color: white; 
  border: none; 
  border-radius: 12px; 
  font-size: 16px; 
  font-weight: 700; 
  cursor: pointer; 
  transition: transform 0.2s; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
}

.generate-btn:hover:not(:disabled) { 
  transform: translateY(-2px); 
  box-shadow: 0 8px 20px rgba(123, 157, 255, 0.4); 
}

.loading-content { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
}

.spinner { 
  width: 18px; 
  height: 18px; 
  border: 3px solid rgba(255,255,255,0.3); 
  border-top-color: white; 
  border-radius: 50%; 
  animation: spin 1s linear infinite; 
}

.divider { 
  border: none; 
  border-top: 1px dashed #eee; 
  margin: 20px 0; 
}

@keyframes spin { 
  to { 
    transform: rotate(360deg); 
  } 
}

.result-container { 
  animation: fadeIn 0.5s ease; 
}

.result-header { 
  text-align: center; 
  margin-bottom: 30px; 
}

.save-btn {
  background-color: #FFB78B; /* 포인트 컬러 */
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}
.save-btn:hover { 
  background-color: #ffa06d; 
}

.save-btn:disabled { 
  opacity: 0.6; 
  cursor: not-allowed; 
}

.header-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.refresh-btn {
  background-color: #7B9DFF;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}
.refresh-btn:hover { 
  background-color: #5c85ff; 
}

.refresh-btn:disabled { 
  opacity: 0.6; 
  cursor: not-allowed;
}

.reset-btn { 
  background: none; 
  border: 1px solid #ddd; 
  padding: 5px 15px; 
  border-radius: 20px; 
  cursor: pointer; 
  color: #666; 
  margin-top: 10px; 
  font-size: 12px; 
}

.reset-btn:hover { 
  border-color: #999; 
  color: #333; 
}
.loading-overlay {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.loading-box { 
  text-align: center; 
  color: #7B9DFF; 
  font-weight: bold; 
}

.spinner.lg { 
  width: 40px; 
  height: 40px; 
  border-width: 4px; 
  border-top-color: #7B9DFF; 
  border-right-color: transparent; 
  border-bottom-color: transparent; 
  border-left-color: transparent; 
  margin: 0 auto 10px; 
}

.day-section { 
  margin-bottom: 40px; 
}

.day-badge { 
  background-color: #333; 
  color: white; 
  display: inline-block; 
  padding: 6px 15px; 
  border-radius: 20px; 
  font-weight: bold; 
  margin-bottom: 20px; 
  font-size: 14px; 
}

.day-date { 
  font-weight: normal; 
  opacity: 0.8; 
  font-size: 12px; 
  margin-left: 5px; 
}

.timeline { 
  padding-left: 10px; 
}

.timeline-item { 
  display: flex; 
  min-height: 100px; 
}

.time-col {
  width: 50px; 
  font-size: 12px; 
  color: #888; 
  text-align: right; 
  padding-right: 15px; 
  padding-top: 15px; 
  font-weight: 600; 
}

.marker-col { 
  width: 20px; 
  position: relative; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
}

.dot { 
  width: 12px; 
  height: 12px; 
  border-radius: 50%; 
  border: 2px solid white; 
  box-shadow: 0 0 0 2px #ddd; 
  background-color: #ddd; 
  z-index: 2; 
  margin-top: 15px; 
}

.line { 
  width: 2px; 
  background-color: #eee; 
  flex: 1; 
  position: absolute; 
  top: 20px; 
  bottom: -20px; 
  left: 50%; 
  transform: translateX(-50%); 
  z-index: 1; 
}

.dot.spot { 
  background-color: #7B9DFF; 
  box-shadow: 0 0 0 2px #7B9DFF; 
}

.dot.meal { 
  background-color: #FFB78B; 
  box-shadow: 0 0 0 2px #FFB78B; 
}

.dot.accommodation { 
  background-color: #92e6a6; 
  box-shadow: 0 0 0 2px #92e6a6; 
}

.content-col { 
  flex: 1; 
  padding-left: 20px; 
  padding-bottom: 20px; 
}

.place-card { 
  display: flex; 
  gap: 15px; 
  background: white; 
  padding: 15px; 
  border-radius: 12px; 
  border: 1px solid #eee; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.03); 
  cursor: pointer; 
  transition: transform 0.2s; 
}

.place-card:hover { 
  transform: translateY(-2px); 
  border-color: #7B9DFF; 
}

.place-img { 
  width: 60px; 
  height: 60px; 
  border-radius: 8px; 
  object-fit: cover; 
}

.place-info { 
  display: flex; 
  flex-direction: column; 
  justify-content: center; 
}

.place-type { 
  font-size: 11px; 
  color: #999; 
  margin-bottom: 2px; 
}

.place-info h4 { 
  margin: 0; 
  font-size: 15px; 
  color: #333; 
}

.place-info p { 
  margin: 2px 0 0; 
  font-size: 12px; 
  color: #888; 
}

.acc-recommend { 
  margin-top: 40px; 
  border-top: 1px dashed #eee; 
  padding-top: 20px; 
}

.acc-recommend h3 { 
  font-size: 18px; 
  margin-bottom: 15px; 
  color: #333; 
}

.acc-card { 
  background-color: #f0f8ff; 
  border-color: #cce5ff; 
}

@keyframes fadeIn { 
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  } 
  to { 
    opacity: 1; transform: translateY(0); 
  } 
}
</style>