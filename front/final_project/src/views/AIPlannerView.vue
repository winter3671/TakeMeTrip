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
            <input type="date" v-model="formData.start_date" class="custom-input" />
          </div>
          <span class="tilde">~</span>
          <div class="input-wrapper">
            <span class="sub-label">오는 날</span>
            <input type="date" v-model="formData.end_date" class="custom-input" />
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
      <div class="result-header">
        <h2>🎉 여행 계획이 완성되었습니다!</h2>
        <p>총 {{ plannerStore.generatedPlan.duration }}일간의 여정</p>
        <button class="reset-btn" @click="resetPlanner">다시 만들기</button>
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

              <div class="content-col">
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
        <div class="place-card acc-card">
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

const router = useRouter();
const plannerStore = usePlannerStore();

// 폼 데이터 (백엔드 Serializer 필드명과 일치시킴)
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

// 시/군/구 목록 필터링
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

// 현재 위치 가져오기 (Promise)
const getCurrentPosition = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      resolve({ lat: 37.5665, lon: 126.9780 }); // 지원 안하면 서울 시청 기본값
    } else {
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        (err) => {
          console.warn("위치 정보를 가져올 수 없어 기본값 사용", err);
          resolve({ lat: 37.5665, lon: 126.9780 }); // 에러 시 서울 시청
        }
      );
    }
  });
};

const handleGenerate = async () => {
  if (!formData.value.start_date || !formData.value.end_date) return alert('일정을 선택해주세요.');
  if (!formData.value.region_id || !formData.value.city_id) return alert('여행지를 선택해주세요.');

  isGenerating.value = true;

  // 1. 현재 위치 확보
  const pos = await getCurrentPosition();
  formData.value.current_mapy = pos.lat; // 위도
  formData.value.current_mapx = pos.lon; // 경도

  // 2. API 호출
  const success = await plannerStore.generatePlan(formData.value);
  
  isGenerating.value = false;
  if (!success) {
    // 실패 처리는 store 내부에서 alert 했거나 여기서 추가 처리
  }
};

const resetPlanner = () => {
  plannerStore.generatedPlan = null;
};


const translateType = (type) => {
  const map = { 'spot': '관광', 'meal': '식사', 'accommodation': '숙소' };
  return map[type] || type;
};

onMounted(() => {
  // 컴포넌트 로드 시 지역 목록 가져오기
  plannerStore.getLocations();
});
</script>

<style scoped>
.planner-container { max-width: 600px; margin: 60px auto; padding: 0 20px; font-family: 'Noto Sans KR', sans-serif; min-height: 80vh; }
.planner-header { text-align: center; margin-bottom: 40px; }
.icon-wrapper { width: 60px; height: 60px; background: linear-gradient(135deg, #7B9DFF, #a1c4fd); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; box-shadow: 0 4px 15px rgba(123, 157, 255, 0.4); }
.header-emoji { font-size: 28px; }
.planner-header h1 { font-size: 28px; font-weight: 800; color: #333; margin-bottom: 8px; }
.planner-header p { color: #666; font-size: 15px; }

/* 폼 스타일 */
.form-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #f0f0f0; }
.form-group { margin-bottom: 20px; }
.form-label { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #333; margin-bottom: 12px; }
.date-inputs { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.input-wrapper { flex: 1; display: flex; flex-direction: column; gap: 5px; }
.sub-label { font-size: 12px; color: #888; font-weight: 500; }
.custom-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 10px; font-size: 14px; outline: none; background-color: #f9f9f9; }
.select-row { display: flex; gap: 10px; }
.custom-select { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 10px; font-size: 14px; outline: none; background-color: #fff; }
.people-counter { display: flex; align-items: center; justify-content: space-between; background-color: #f9f9f9; border-radius: 10px; padding: 5px; border: 1px solid #eee; }
.counter-btn { width: 40px; height: 40px; border: none; background-color: white; border-radius: 8px; font-size: 20px; color: #555; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.counter-btn:hover:not(:disabled) { background-color: #7B9DFF; color: white; }
.generate-btn { width: 100%; margin-top: 30px; padding: 16px; background: linear-gradient(90deg, #7B9DFF, #6b8cef); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; transition: transform 0.2s; display: flex; align-items: center; justify-content: center; }
.generate-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(123, 157, 255, 0.4); }
.loading-content { display: flex; align-items: center; gap: 10px; }
.spinner { width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite; }
.divider { border: none; border-top: 1px dashed #eee; margin: 20px 0; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ★ 결과 화면 스타일 (타임라인) */

.result-container { animation: fadeIn 0.5s ease; }
.result-header { text-align: center; margin-bottom: 30px; }
.reset-btn { background: none; border: 1px solid #ddd; padding: 5px 15px; border-radius: 20px; cursor: pointer; color: #666; margin-top: 10px; font-size: 12px; }

.day-section { margin-bottom: 40px; }
.day-badge { background-color: #333; color: white; display: inline-block; padding: 6px 15px; border-radius: 20px; font-weight: bold; margin-bottom: 20px; font-size: 14px; }
.day-date { font-weight: normal; opacity: 0.8; font-size: 12px; margin-left: 5px; }

.timeline { padding-left: 10px; }
.timeline-item { display: flex; min-height: 100px; }
.time-col { width: 50px; font-size: 12px; color: #888; text-align: right; padding-right: 15px; padding-top: 15px; font-weight: 600; }
.marker-col { width: 20px; position: relative; display: flex; flex-direction: column; align-items: center; }
.dot { width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 0 2px #ddd; background-color: #ddd; z-index: 2; margin-top: 15px; }
.line { width: 2px; background-color: #eee; flex: 1; position: absolute; top: 20px; bottom: -20px; left: 50%; transform: translateX(-50%); z-index: 1; }

.dot.spot { background-color: #7B9DFF; box-shadow: 0 0 0 2px #7B9DFF; }
.dot.meal { background-color: #FFB78B; box-shadow: 0 0 0 2px #FFB78B; }
.dot.accommodation { background-color: #92e6a6; box-shadow: 0 0 0 2px #92e6a6; }

.content-col { flex: 1; padding-left: 20px; padding-bottom: 20px; }
.place-card { display: flex; gap: 15px; background: white; padding: 15px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.03); cursor: pointer; transition: transform 0.2s; }
.place-card:hover { transform: translateY(-2px); border-color: #7B9DFF; }
.place-img { width: 60px; height: 60px; border-radius: 8px; object-fit: cover; }
.place-info { display: flex; flex-direction: column; justify-content: center; }
.place-type { font-size: 11px; color: #999; margin-bottom: 2px; }
.place-info h4 { margin: 0; font-size: 15px; color: #333; }
.place-info p { margin: 2px 0 0; font-size: 12px; color: #888; }

.acc-recommend { margin-top: 40px; border-top: 1px dashed #eee; padding-top: 20px; }
.acc-recommend h3 { font-size: 18px; margin-bottom: 15px; color: #333; }
.acc-card { background-color: #f0f8ff; border-color: #cce5ff; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>