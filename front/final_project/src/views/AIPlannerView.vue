<template>
  <div class="planner-container" :class="{ 'wide': plannerStore.generatedPlan }">
    
    <div class="planner-header">
      <div class="icon-wrapper">
        <span class="header-emoji">✨</span>
      </div>
      <h1>취향 맞춤 여행 플래너</h1>
      <p>날짜와 장소만 알려주세요. 당신의 취향에 딱 맞는 여행 일정을 만들어드려요.</p>
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
              :max="maxEndDate"
            />
          </div>
        </div>
        <p class="limit-info">
          <span class="info-icon">💡</span>
          최적의 경로 계산을 위해 여행 기간은 최대 <strong>4박 5일</strong>까지만 설정 가능합니다.
        </p>
      </div>

      <hr class="divider" />

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

      <hr class="divider" />

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
        <span v-if="!isGenerating">맞춤형 여행 계획 만들기 ✨</span>
        <span v-else class="loading-content">
          <span class="spinner"></span>
          최적의 경로를 계산 중입니다...
        </span>
      </button>
    </div>

    <div v-else class="planner-result-view">
      
      <div v-if="isGenerating" class="loading-overlay">
        <div class="loading-box">
          <div class="spinner lg"></div>
          <p>새로운 경로를 찾고 있어요...</p>
        </div>
      </div>

      <!-- 좌측 사이드바: 일정 타임라인 -->
      <aside class="planner-sidebar" :class="{ 'closed': !isSidebarOpen }">
        <div class="sidebar-header">
          <div class="header-top">
             <h2>여행 일정</h2>
             <button class="close-btn" @click="toggleSidebar">
               <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6" /></svg>
             </button>
          </div>
          <div class="day-tabs">
            <button 
              v-for="dayPlan in plannerStore.generatedPlan.plan" 
              :key="dayPlan.day"
              class="day-tab"
              :class="{ 'active': selectedDay === dayPlan.day }"
              @click="selectDay(dayPlan.day)"
            >
              Day {{ dayPlan.day }}
            </button>
          </div>
        </div>

        <div class="sidebar-scroll-content">
          <div v-if="plannerStore.generatedPlan.plan.find(p => p.day === selectedDay)" class="day-timeline">
            <!-- 숙소를 제외하고 실제 여행 장소만 필터링해서 표시 -->
            <div 
              v-for="(item, idx) in getVisibleSchedule(selectedDay - 1)" 
              :key="idx" 
              class="timeline-item-horizontal"
              draggable="true"
              @dragstart="onDragStart(item, selectedDay - 1, idx)"
              @dragover.prevent
              @drop="onDropOnDay(selectedDay - 1, idx)"
              @click="focusPlace(item.data)"
            >
              <div class="time-mark">{{ item.time }}</div>
              <div class="marker-box">
                <div class="v-line" v-if="idx !== getVisibleSchedule(selectedDay - 1).length - 1"></div>
                <!-- UI 순서 번호 표시 -->
                <div class="order-number-badge">{{ idx + 1 }}</div>
              </div>
              <div class="item-card-mini">
                <img :src="item.data.thumbnail_image || '/src/assets/no_image.png'" class="mini-img" />
                <div class="mini-info">
                  <div class="info-header">
                    <span class="type-tag" :class="item.type">{{ translateType(item.type) }}</span>
                    <button class="delete-item-btn" @click.stop="removePlace(selectedDay - 1, idx)">×</button>
                  </div>
                  <h4>{{ item.data.title }}</h4>
                </div>
              </div>
            </div>

            <!-- 마지막 드롭 영역 -->
            <div 
              class="drop-zone-end"
              @dragover.prevent
              @drop="onDropOnDay(selectedDay - 1, getVisibleSchedule(selectedDay - 1).length)"
            >
              <div class="schedule-guide">
                <span class="guide-icon">❓</span>
                <div class="guide-tooltip">
                  <b>🕒 스케줄링 안내</b><br/>
                  출발시간은 09:00 고정, 점심(11~13시), 저녁(17~19시)로 식사 시간이 설정되어 있습니다. 
                  해당 시간대 사이에 너무 많은 일정을 추가하면 저장이 제한될 수 있습니다.
                </div>
              </div>
              여기에 장소를 추가하세요
            </div>
          </div>

          <div class="sidebar-footer">
            <button class="save-full-btn" @click="handleSaveCourse">이 코스로 확정 및 저장</button>
            <button class="reset-link-btn" @click="resetPlanner">조건 다시 설정</button>

            <!-- 숙소 전용 관리 섹션 -->
            <div class="accommodation-manager">
              <h3 class="section-title">🏘️ 숙소 정보 확인</h3>
              <div v-if="currentAccommodation" class="current-acc-card">
                <img :src="currentAccommodation.thumbnail_image || '/src/assets/no_image.png'" class="acc-mini-thumb" />
                <div class="acc-mini-info">
                  <h4>{{ currentAccommodation.title }}</h4>
                  <p>{{ currentAccommodation.destination }}</p>
                </div>
              </div>
              
              <div class="other-accs" v-if="accommodationRecs.length > 0">
                <h4 class="sub-title">추천 숙소 교체</h4>
                <div 
                  v-for="acc in accommodationRecs" 
                  :key="acc.id" 
                  class="acc-rec-item"
                  @click="changeAccommodation(acc)"
                >
                  <div class="acc-rec-info">
                    <h5>{{ acc.title }}</h5>
                    <span>가까운 숙소</span>
                  </div>
                  <button class="change-btn">교체</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <button v-if="!isSidebarOpen" class="sidebar-open-btn" @click="toggleSidebar">
        일정 보기
      </button>

      <!-- 중앙: 지도 영역 -->
      <main class="map-area">
        <div ref="mapContainer" class="full-map"></div>
        
        <!-- 우측 플로팅 패널: 추천 장소 -->
        <div class="recs-panel" :class="{ 'closed': !isRecsOpen }">
          <div class="recs-header" @click="toggleRecs">
            <span>💡 이런 장소는 어때요?</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :style="{ transform: isRecsOpen ? 'rotate(180deg)' : 'none' }"><polyline points="6 9 12 15 18 9" /></svg>
          </div>
          <div v-if="isRecsOpen" class="recs-list">
              <div 
                v-for="place in recommendedPlaces" 
                :key="place.id" 
                class="rec-item"
                draggable="true"
                @dragstart="onDragStart(place, null, null, true)"
                @click="previewPlace(place)"
              >
                <img :src="place.thumbnail_image || '/src/assets/no_image.png'" class="rec-thumb" />
                <div class="rec-info">
                  <h5>{{ place.title }}</h5>
                  <p>{{ place.category_name }}</p>
                </div>
                <div class="drag-handle">⋮⋮</div>
              </div>
            <p v-if="recommendedPlaces.length === 0" class="no-recs">추천할 장소가 더 없습니다.</p>
            <button class="reroll-btn" @click="fetchRecommendations">다른 추천 받기</button>
          </div>
        </div>
      </main>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { usePlannerStore } from '@/stores/planners';
import { useAccountStore } from '@/stores/accounts';
import { useTripStore } from '@/stores/trips';

// 지도 관련 변수
let map = null;
let markers = [];
let polylines = [];

const router = useRouter();
const plannerStore = usePlannerStore();
const accountStore = useAccountStore();
const tripStore = useTripStore();

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
const selectedDay = ref(1);
const mapContainer = ref(null);
const recommendedPlaces = ref([]);
const isSidebarOpen = ref(true);
const isRecsOpen = ref(true);

// 프리뷰 및 숙소 추천 관련
let previewMarker = null;
let previewOverlay = null;
const accommodationRecs = ref([]);
const currentAccommodation = computed(() => {
    const dayPlan = plannerStore.generatedPlan?.plan.find(p => p.day === selectedDay.value);
    return dayPlan?.schedule.find(item => item.type === 'accommodation')?.data;
});

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

const maxEndDate = computed(() => {
  if (!formData.value.start_date) return null;
  
  const start = new Date(formData.value.start_date);
  const max = new Date(start);
  max.setDate(start.getDate() + 4);
  
  const year = max.getFullYear();
  const month = String(max.getMonth() + 1).padStart(2, '0');
  const day = String(max.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
});
// 시작일이 바뀔 때 종료일이 범위를 벗어나면 자동 조정
watch(() => formData.value.start_date, (newStart) => {
  if (!newStart) return;

  // 종료일이 이미 선택되어 있는데,
  if (formData.value.end_date) {
    // 1) 종료일이 시작일보다 이전이면 -> 시작일로 맞춤
    if (formData.value.end_date < newStart) {
      formData.value.end_date = newStart;
    }
    // 2) 종료일이 최대 4박(maxEndDate)을 넘어가면 -> 최대일로 맞춤
    else if (maxEndDate.value && formData.value.end_date > maxEndDate.value) {
      alert("여행 기간은 최대 4박 5일까지만 설정 가능합니다.");
      formData.value.end_date = maxEndDate.value;
    }
  }
});

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

// --- 지도 로직 ---
const loadKakaoMap = () => {
    if (window.kakao && window.kakao.maps) {
        nextTick(() => {
            initMap();
        });
    } else {
        const script = document.createElement('script');
        script.onload = () => {
            window.kakao.maps.load(() => {
                nextTick(initMap);
            });
        };
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&libraries=services`;
        document.head.appendChild(script);
    }
};
const initMap = () => {
    if (!mapContainer.value) return;
    
    const plan = plannerStore.generatedPlan.plan;
    let initialCenter = new window.kakao.maps.LatLng(37.5665, 126.9780);
    
    if (plan && plan.length > 0 && plan[0].schedule.length > 0) {
        const first = plan[0].schedule[0].data;
        if (first.mapy && first.mapx) {
            initialCenter = new window.kakao.maps.LatLng(first.mapy, first.mapx);
        }
    }

    const options = {
        center: initialCenter,
        level: 5
    };
    map = new window.kakao.maps.Map(mapContainer.value, options);
    
    drawRoute(selectedDay.value);
};

// --- 지도 핀 디자인 개선 및 유틸리티 ---
const createMarkerLabel = (index, type) => {
    const color = type === 'meal' ? '#ff9f43' : '#7B9DFF';
    return `
        <div class="modern-pin" style="background-color: ${color};">
            <span class="pin-number">${index}</span>
        </div>
    `;
};

const createHotelMarker = () => {
    return `
        <div class="custom-hotel-badge">
            <svg viewBox="0 0 24 24" fill="white" width="20" height="20">
                <path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm0-4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM20 7h-7c-1.1 0-2 .9-2 2v5H9V8c0-.55-.45-1-1-1s-1 .45-1 1v10h2v-2h10v2h2v-7c0-2.21-1.79-4-4-4z"/>
            </svg>
        </div>
    `;
};

const drawRoute = (day) => {
    if (!map || !plannerStore.generatedPlan) return;

    markers.forEach(m => m.setMap(null));
    markers = [];
    if (polylines && polylines.length > 0) {
        polylines.forEach(p => p.setMap(null));
    }
    polylines = [];

    const dayPlan = plannerStore.generatedPlan.plan.find(p => p.day === day);
    if (!dayPlan) return;

    const bounds = new window.kakao.maps.LatLngBounds();
    const visibleSchedule = getVisibleSchedule(day - 1);
    const hotelItem = dayPlan.schedule.find(it => it.type === 'accommodation');

    // 1. 숙소 마커 표시
    if (hotelItem && hotelItem.data.mapy && hotelItem.data.mapx) {
        const hotelPos = new window.kakao.maps.LatLng(hotelItem.data.mapy, hotelItem.data.mapx);
        const hotelMarker = new window.kakao.maps.CustomOverlay({
            position: hotelPos,
            content: createHotelMarker(),
            yAnchor: 1.2
        });
        hotelMarker.setMap(map);
        markers.push(hotelMarker);
        // 숙소는 줌 범위에 포함하지 않음 (사용자 요청)
    }

    // 2. 일정 장소 마커 표시
    visibleSchedule.forEach((item, index) => {
        if (!item.data.mapy || !item.data.mapx) return;

        const pos = new window.kakao.maps.LatLng(item.data.mapy, item.data.mapx);
        bounds.extend(pos);

        const overlay = new window.kakao.maps.CustomOverlay({
            position: pos,
            content: createMarkerLabel(index + 1, item.type),
            yAnchor: 1.4
        });
        overlay.setMap(map);
        markers.push(overlay);

        // 선 그리기
        const prevItem = index === 0 ? hotelItem : visibleSchedule[index - 1];
        if (prevItem && prevItem.data.mapy && prevItem.data.mapx) {
            const prevPos = new window.kakao.maps.LatLng(prevItem.data.mapy, prevItem.data.mapx);
            const isDashed = index === 0; // 숙소에서 첫 장소로 가는 길은 점선
            
            const poly = new window.kakao.maps.Polyline({
                path: [prevPos, pos],
                strokeWeight: 5,
                strokeColor: isDashed ? '#ced4da' : '#7B9DFF', // 이동 경로는 시각적 피로를 줄이기 위해 통일
                strokeOpacity: 0.9,
                strokeStyle: isDashed ? 'dash' : 'solid'
            });
            poly.setMap(map);
            polylines.push(poly);
        }

        // 마지막 장소에서 다시 숙소로 (있다면)
        if (index === visibleSchedule.length - 1 && hotelItem) {
             const nextPos = new window.kakao.maps.LatLng(hotelItem.data.mapy, hotelItem.data.mapx);
             const endPoly = new window.kakao.maps.Polyline({
                path: [pos, nextPos],
                strokeWeight: 5,
                strokeColor: '#ced4da',
                strokeOpacity: 0.8,
                strokeStyle: 'dash'
            });
            endPoly.setMap(map);
            polylines.push(endPoly);
        }
    });

    if (!bounds.isEmpty()) {
        map.setBounds(bounds);
    }
};

const focusPlace = (place) => {
    if (!map || !place.mapy || !place.mapx) return;
    const moveLatLon = new window.kakao.maps.LatLng(place.mapy, place.mapx);
    map.panTo(moveLatLon);
};

const previewPlace = (place) => {
    if (!map || !place.mapy || !place.mapx) return;
    
    // 기존 프리뷰 제거
    if (previewMarker) previewMarker.setMap(null);
    if (previewOverlay) previewOverlay.setMap(null);

    const pos = new window.kakao.maps.LatLng(place.mapy, place.mapx);
    
    previewMarker = new window.kakao.maps.Marker({ position: pos });
    previewMarker.setMap(map);
    
    previewOverlay = new window.kakao.maps.CustomOverlay({
        position: pos,
        content: `<div class="preview-badge">?</div>`,
        yAnchor: 2.2
    });
    previewOverlay.setMap(map);
    
    map.panTo(pos);
    
    // 3초 후 제거
    setTimeout(() => {
        if (previewMarker) previewMarker.setMap(null);
        if (previewOverlay) previewOverlay.setMap(null);
    }, 3000);
};

const selectDay = (day) => {
    selectedDay.value = day;
    drawRoute(day);
    fetchRecommendations();
};

// --- 스케줄 보조 유틸 ---
const getVisibleSchedule = (dayIdx) => {
    const dayPlan = plannerStore.generatedPlan?.plan[dayIdx];
    if (!dayPlan) return [];
    return dayPlan.schedule.filter(item => item.type !== 'accommodation');
};

const fetchAccommodationRecs = async () => {
    const dayPlan = plannerStore.generatedPlan?.plan[selectedDay.value - 1];
    if (!dayPlan || dayPlan.schedule.length === 0) return;

    // 중간 지점 계산
    const visibleOnes = getVisibleSchedule(selectedDay.value - 1);
    if (visibleOnes.length === 0) return;

    let sumLat = 0, sumLng = 0;
    visibleOnes.forEach(it => {
        sumLat += it.data.mapy;
        sumLng += it.data.mapx;
    });
    const midLat = sumLat / visibleOnes.length;
    const midLng = sumLng / visibleOnes.length;

    try {
        const data = await tripStore.getAiRecommendations({
            count: 3,
            city_id: plannerStore.generatedPlan.city_id,
            lat: midLat,
            lng: midLng,
            category_name: '숙박'
        });
        accommodationRecs.value = data.filter(it => it.id !== currentAccommodation.value?.id);
    } catch (e) {
        console.error("숙소 추천 로드 실패", e);
    }
};

const changeAccommodation = (newPlace) => {
    if (!plannerStore.generatedPlan) return;

    // 모든 일차의 숙소를 변경
    plannerStore.generatedPlan.plan.forEach((day, idx) => {
        const accIdx = day.schedule.findIndex(it => it.type === 'accommodation');
        if (accIdx !== -1) {
            day.schedule[accIdx].data = newPlace;
        } else {
            // 숙소가 없는 경우 맨 앞에 추가
            day.schedule.unshift({ type: 'accommodation', time: '09:00', data: newPlace });
        }
        // 시간 및 경로 재계산
        recalculateSchedule(idx);
    });
    
    fetchAccommodationRecs();
};

// --- 추천 장소 로드 ---
const fetchRecommendations = async () => {
    try {
        const dayPlan = plannerStore.generatedPlan.plan.find(p => p.day === selectedDay.value);
        if (!dayPlan) return;

        const reference = dayPlan.schedule.find(item => item.data.city_id)?.data;
        
        const params = {
            count: 5,
            city_id: reference?.city_id || plannerStore.generatedPlan.city_id,
            lat: reference?.mapy,
            lng: reference?.mapx
        };

        const data = await tripStore.getAiRecommendations(params);
        const usedIds = new Set();
        plannerStore.generatedPlan.plan.forEach(day => {
            day.schedule.forEach(item => usedIds.add(item.data.id));
        });
        
        recommendedPlaces.value = data.filter(place => !usedIds.has(place.id) && !place.category_name?.includes('숙박')).slice(0, 5);
        fetchAccommodationRecs(); // 숙소 추천도 같이 로드
    } catch (error) {
        console.error("추천 장소 로드 실패", error);
    }
};

// --- 시간 재계산 로직 ---
const recalculateSchedule = (dayIdx) => {
    const dayPlan = plannerStore.generatedPlan.plan[dayIdx];
    if (!dayPlan || dayPlan.schedule.length === 0) return;

    let currentTime = new Date(`2025-01-01T09:00:00`);

    let mealCount = 0;

    dayPlan.schedule.forEach((item, idx) => {
        // 사용자 요구사항: 점심(11-13시) / 저녁(17-19시) 고정
        if (item.type === 'meal') {
            mealCount++;
            if (mealCount === 1) { // 첫 식사는 점심
                const lunchFixed = new Date(`2025-01-01T12:00:00`);
                // 이미 밀려서 12시를 넘었다면 현재 시간 유지, 아니면 12시로 고정
                if (currentTime < lunchFixed) currentTime = lunchFixed;
            } else if (mealCount === 2) { // 두 번째 식사는 저녁
                const dinnerFixed = new Date(`2025-01-01T18:00:00`);
                if (currentTime < dinnerFixed) currentTime = dinnerFixed;
            }
        }

        item.time = `${String(currentTime.getHours()).padStart(2, '0')}:${String(currentTime.getMinutes()).padStart(2, '0')}`;
        
        // 다음 장소까지의 소요 시간 계산
        if (idx < dayPlan.schedule.length - 1) {
            const nextItem = dayPlan.schedule[idx+1];
            const dist = getDistance(item.data.mapx, item.data.mapy, nextItem.data.mapx, nextItem.data.mapy);
            const moveMin = calculateMoveTime(dist);
            
            // 머무는 시간 (관광 90분, 식사 60분, 숙소는 이동만)
            let stayMin = 0;
            if (item.type === 'spot') stayMin = 90;
            else if (item.type === 'meal') stayMin = 60;
            
            currentTime.setMinutes(currentTime.getMinutes() + stayMin + moveMin);
        }
    });

    drawRoute(selectedDay.value);
};

const validateSchedule = (dayIdx, newSchedule) => {
    let currentTime = new Date(`2025-01-01T09:00:00`);
    let mealCount = 0;
    
    // 식사 인덱스 파악
    const meals = newSchedule.filter(item => item.type === 'meal');
    const lunchIdx = newSchedule.findIndex(item => item.type === 'meal');
    const dinnerIdx = newSchedule.slice(lunchIdx + 1).findIndex(item => item.type === 'meal');
    const finalDinnerIdx = dinnerIdx === -1 ? -1 : lunchIdx + 1 + dinnerIdx;

    for (let i = 0; i < newSchedule.length; i++) {
        const item = newSchedule[i];
        
        if (item.type === 'meal') {
            mealCount++;
            if (mealCount === 1) {
                if (currentTime > new Date(`2025-01-01T13:00:00`)) return false; // 점심 시작이 1시 넘으면 탈락
                currentTime = new Date(`2025-01-01T12:00:00`); // 점심 계산용 픽스
            } else if (mealCount === 2) {
                if (currentTime > new Date(`2025-01-01T19:00:00`)) return false; // 저녁 시작이 7시 넘으면 탈락
                currentTime = new Date(`2025-01-01T18:00:00`); // 저녁 계산용 픽스
            }
        }

        if (i < newSchedule.length - 1) {
            const nextItem = newSchedule[i+1];
            const dist = getDistance(item.data.mapx, item.data.mapy, nextItem.data.mapx, nextItem.data.mapy);
            const moveMin = calculateMoveTime(dist);
            let stayMin = item.type === 'spot' ? 90 : (item.type === 'meal' ? 60 : 0);
            currentTime.setMinutes(currentTime.getMinutes() + stayMin + moveMin);
        }
    }

    // 저녁 이후 활동 1개 제한
    if (finalDinnerIdx !== -1) {
        const postDinner = newSchedule.slice(finalDinnerIdx + 1).filter(it => it.type === 'spot');
        if (postDinner.length > 1) return false;
    }

    return true;
};

const getDistance = (x1, y1, x2, y2) => {
    if (!x1 || !y1 || !x2 || !y2) return 0;
    return Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2));
};

const calculateMoveTime = (dist) => {
    const km = dist * 111;
    const speed = 40; // 평균 시속 40km
    return Math.max(10, Math.floor((km / speed) * 60)); // 최소 10분
};

// --- 드래그앤드랍 핸들러 ---
let draggedItem = null;
let draggedFromDay = null;
let draggedFromIndex = null;
let isFromRecs = false;

const onDragStart = (item, dayIdx, itemIdx, fromRecs = false) => {
    draggedItem = JSON.parse(JSON.stringify(item));
    draggedFromDay = dayIdx;
    draggedFromIndex = itemIdx;
    isFromRecs = fromRecs;
};

const onDropOnDay = (dayIdx, targetIdxInFiltered) => {
    if (!draggedItem) return;

    // 필터링된 인덱스를 실제 스케줄 인덱스로 변환
    const realTargetIdx = getRealIndex(dayIdx, targetIdxInFiltered);

    const currentSchedule = [...plannerStore.generatedPlan.plan[dayIdx].schedule];
    let newSchedule = [...currentSchedule];

    // 만약 추천 목록에서 온 것이라면
    if (isFromRecs) {
        const newItem = {
            type: draggedItem.category_name?.includes('음식') ? 'meal' : 'spot',
            time: '00:00',
            data: draggedItem
        };
        newSchedule.splice(realTargetIdx, 0, newItem);
    } else {
        if (draggedFromDay === dayIdx) {
            // 같은 날 내이동
            const realFromIdx = getRealIndex(dayIdx, draggedFromIndex);
            newSchedule.splice(realFromIdx, 1);
            // targetIdx가 나중 위치면 보정
            const adjustIdx = (realFromIdx < realTargetIdx) ? realTargetIdx - 1 : realTargetIdx;
            newSchedule.splice(adjustIdx, 0, draggedItem);
        } else {
            newSchedule.splice(realTargetIdx, 0, draggedItem);
        }
    }

    if (!validateSchedule(dayIdx, newSchedule)) {
        alert("너무 많은 일정 설정은 제한됩니다.");
        draggedItem = null;
        return;
    }

    // 실제 반영
    if (isFromRecs) {
        plannerStore.generatedPlan.plan[dayIdx].schedule.splice(realTargetIdx, 0, {
            type: draggedItem.category_name?.includes('음식') ? 'meal' : 'spot',
            time: '00:00',
            data: draggedItem
        });
        recommendedPlaces.value = recommendedPlaces.value.filter(p => p.id !== draggedItem.id);
    } else {
        if (draggedFromDay === dayIdx) {
            const realFromIdx = getRealIndex(dayIdx, draggedFromIndex);
            plannerStore.generatedPlan.plan[dayIdx].schedule.splice(realFromIdx, 1);
            const adjustIdx = (realFromIdx < realTargetIdx) ? realTargetIdx - 1 : realTargetIdx;
            plannerStore.generatedPlan.plan[dayIdx].schedule.splice(adjustIdx, 0, draggedItem);
        } else {
            const realFromIdx = getRealIndex(draggedFromDay, draggedFromIndex);
            plannerStore.generatedPlan.plan[draggedFromDay].schedule.splice(realFromIdx, 1);
            plannerStore.generatedPlan.plan[dayIdx].schedule.splice(realTargetIdx, 0, draggedItem);
            recalculateSchedule(draggedFromDay);
        }
    }

    recalculateSchedule(dayIdx);
    draggedItem = null;
    draggedFromDay = null;
    draggedFromIndex = null;
    isFromRecs = false;
};

const removePlace = (dayIdx, filteredIdx) => {
    const realIdx = getRealIndex(dayIdx, filteredIdx);
    plannerStore.generatedPlan.plan[dayIdx].schedule.splice(realIdx, 1);
    recalculateSchedule(dayIdx);
};

const getRealIndex = (dayIdx, filteredIdx) => {
    const schedule = plannerStore.generatedPlan.plan[dayIdx].schedule;
    let count = 0;
    for (let i = 0; i < schedule.length; i++) {
        if (schedule[i].type !== 'accommodation') {
            if (count === filteredIdx) return i;
            count++;
        }
    }
    // 만약 끝에 드롭하는 경우 (visible length와 같은 경우)
    // 숙소가 맨 뒤에 있다면 그 바로 앞 인덱스 반환
    const lastAccIdx = schedule.findLastIndex(it => it.type === 'accommodation');
    return lastAccIdx !== -1 ? lastAccIdx : schedule.length;
};

const toggleSidebar = () => isSidebarOpen.value = !isSidebarOpen.value;
const toggleRecs = () => isRecsOpen.value = !isRecsOpen.value;

// 플랜 생성 완료 후 지도 로드 및 추천 로드
watch(() => plannerStore.generatedPlan, (newPlan) => {
    if (newPlan) {
        selectedDay.value = 1;
        fetchRecommendations();
        setTimeout(() => {
            loadKakaoMap();
        }, 100);
    }
});

onMounted(() => {
  plannerStore.getLocations();
});
</script>

<style scoped>
.planner-container { 
  max-width: 600px; 
  margin: 60px auto; 
  padding: 0 20px; 
  font-family: 'Noto Sans KR', sans-serif; 
  min-height: 80vh; 
  transition: max-width 0.5s ease;
}

.planner-container.wide {
  max-width: 1200px;
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

/* --- 결과 화면 (전체 화면 분할) 스타일 --- */
.planner-result-view {
  position: fixed;
  top: 70px; /* Navbar 높이 고려 */
  left: 0;
  width: 100vw;
  height: calc(100vh - 70px);
  display: flex;
  overflow: hidden;
  background-color: #f8f9fa;
  animation: fadeIn 0.4s ease;
  z-index: 100;
}

/* 좌측 사이드바 */
.planner-sidebar {
  width: 380px;
  height: 100%;
  background: white;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  z-index: 110;
  box-shadow: 2px 0 10px rgba(0,0,0,0.05);
}

.planner-sidebar.closed {
  transform: translateX(-100%);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.header-top h2 {
  font-size: 18px;
  font-weight: 800;
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
}

.day-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.day-tab {
  flex-shrink: 0;
  padding: 6px 15px;
  border-radius: 15px;
  border: 1px solid #eee;
  background: #f9f9f9;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.day-tab.active {
  background: #333;
  color: white;
  border-color: #333;
}

.sidebar-scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 타임라인 항목 (사이드바 버전) */
.timeline-item-horizontal {
  display: flex;
  gap: 15px;
  position: relative;
  margin-bottom: 0;
  padding-bottom: 15px;
}

.time-mark {
  width: 45px;
  font-size: 11px;
  font-weight: 700;
  color: #999;
  padding-top: 15px;
}

.marker-box {
  width: 12px;
  position: relative;
  display: flex;
  justify-content: center;
}

.v-line {
  position: absolute;
  top: 25px;
  bottom: -15px;
  width: 2px;
  background: #eee;
}

.dot-sm {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ddd;
  margin-top: 15px;
  z-index: 2;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #ddd;
}

.dot-sm.spot { background: #7B9DFF; box-shadow: 0 0 0 2px #7B9DFF; }
.dot-sm.meal { background: #FFB78B; box-shadow: 0 0 0 2px #FFB78B; }
.dot-sm.accommodation { background: #92e6a6; box-shadow: 0 0 0 2px #92e6a6; }

.item-card-mini {
  flex: 1;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 10px;
  display: flex;
  gap: 10px;
  cursor: grab;
  transition: all 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.item-card-mini:active { cursor: grabbing; }
.item-card-mini:hover { border-color: #7B9DFF; box-shadow: 0 4px 12px rgba(123, 157, 255, 0.1); }

.mini-img {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
}

.mini-info { flex: 1; }
.mini-info h4 { margin: 2px 0 0; font-size: 14px; color: #333; }
.info-header { display: flex; justify-content: space-between; align-items: center; }
.type-tag { font-size: 10px; color: #aaa; }
.delete-item-btn { background: none; border: none; color: #ccc; cursor: pointer; font-size: 16px; padding: 0 5px; }
.delete-item-btn:hover { color: #f44336; }

.drop-zone-end {
  position: relative;
  margin-top: 20px;
  padding: 20px;
  border: 2px dashed #eee;
  border-radius: 12px;
  text-align: center;
  font-size: 12px;
  color: #bbb;
  transition: all 0.2s;
}

.drop-zone-end:hover { background: #f0f7ff; border-color: #7B9DFF; color: #7B9DFF; }

.sidebar-footer { padding: 20px; border-top: 1px solid #f0f0f0; display: flex; flex-direction: column; gap: 10px; }
.save-full-btn { background: #7B9DFF; color: white; border: none; padding: 12px; border-radius: 10px; font-weight: 700; cursor: pointer; }
.reset-link-btn { background: none; border: none; color: #999; font-size: 12px; cursor: pointer; text-decoration: underline; }

/* 중앙 지도 영역 */
.map-area { flex: 1; position: relative; }
.full-map { width: 100%; height: 100%; }

.sidebar-open-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 105;
  background: white;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 700;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  cursor: pointer;
}

/* 우측 추천 패널 */
.recs-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 280px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.15);
  overflow: hidden;
  z-index: 105;
  transition: all 0.3s;
}

.recs-header { background: #fdfdfd; padding: 12px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; }
.recs-header span { font-size: 13px; font-weight: 700; color: #555; }
.recs-list { padding: 15px; max-height: 500px; overflow-y: auto; }

.rec-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: grab;
  transition: transform 0.2s;
}

.rec-item:hover { transform: translateX(-5px); background: #f0f7ff; }

.rec-thumb { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; }
.rec-info { flex: 1; }
.rec-info h5 { margin: 0; font-size: 12px; color: #333; }
.rec-info p { margin: 2px 0 0; font-size: 10px; color: #888; }
.drag-handle { color: #ddd; font-size: 14px; }

/* 디자인 포인트: 가로형 일정 카드 및 숫자 배지 */
.order-number-badge {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  background: #7B9DFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  z-index: 2;
  box-shadow: 0 2px 6px rgba(123, 157, 255, 0.4);
}

.item-card-mini {
  cursor: pointer;
  transition: transform 0.2s;
}
.item-card-mini:hover {
  transform: translateX(5px);
}

.type-tag.meal { background: #fff5eb; color: #ff9f43; }
.type-tag.spot { background: #eef2ff; color: #7B9DFF; }

/* 지도 커스텀 오버레이 스타일 (물방울 핀 디자인) */
.modern-pin {
    width: 32px;
    height: 32px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2.5px solid white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
.pin-number {
    transform: rotate(45deg);
    color: white;
    font-weight: 800;
    font-size: 14px;
    margin-bottom: 2px;
    margin-right: 2px;
}
.custom-hotel-badge {
    width: 36px;
    height: 36px;
    background: #333;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid white;
    box-shadow: 0 3px 10px rgba(0,0,0,0.3);
}
.preview-badge {
    background: #f39c12;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid white;
    font-weight: bold;
}

/* 숙소 관리 섹션 스타일 */
.accommodation-manager {
  margin-top: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #eee;
}
.section-title { font-size: 14px; font-weight: 800; margin-bottom: 12px; color: #333; }
.current-acc-card {
  display: flex;
  gap: 12px;
  background: white;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 15px;
}
.acc-mini-thumb { width: 50px; height: 50px; border-radius: 6px; object-fit: cover; }
.acc-mini-info h4 { font-size: 13px; margin: 0 0 4px 0; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px; }
.acc-mini-info p { font-size: 11px; color: #888; margin: 0; }

.other-accs { margin-top: 15px; }
.sub-title { font-size: 12px; color: #666; font-weight: 700; margin-bottom: 8px; }
.acc-rec-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 6px;
  border: 1px solid #eee;
  cursor: pointer;
}
.acc-rec-item:hover { border-color: #7B9DFF; background: #f0f7ff; }
.acc-rec-info { flex: 1; min-width: 0; margin-right: 12px; }
.acc-rec-info h5 { 
  font-size: 12px; 
  margin: 0; 
  color: #444; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  white-space: nowrap; 
}
.acc-rec-info span { font-size: 10px; color: #7B9DFF; }
.change-btn {
  font-size: 11px;
  padding: 4px 8px;
  background: #7B9DFF;
  color: white;
  border: none;
  border-radius: 4px;
}

/* 스케줄 규칙 가이드 스타일 */
.schedule-guide {
  position: absolute;
  top: 10px;
  right: 15px;
  cursor: help;
}
.guide-icon {
  width: 18px;
  height: 18px;
  background: #eee;
  color: #999;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}
.guide-tooltip {
  visibility: hidden;
  position: absolute;
  bottom: 125%;
  right: 0;
  width: 240px;
  background-color: #333;
  color: #fff;
  text-align: center;
  border-radius: 8px;
  padding: 10px;
  font-size: 11px;
  line-height: 1.5;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.guide-tooltip::after {
  content: "";
  position: absolute;
  top: 100%;
  right: 5px;
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}
.schedule-guide:hover .guide-tooltip {
  visibility: visible;
  opacity: 1;
}
</style>

<!-- 지도 오버레이용 전역 스타일 (Scoped CSS 영향을 피하기 위함) -->
<style>
.modern-pin {
    width: 34px !important;
    height: 34px !important;
    border-radius: 50% 50% 50% 0 !important;
    transform: rotate(-45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid white !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    z-index: 10;
}
.pin-number {
    transform: rotate(45deg);
    color: white !important;
    font-weight: 900 !important;
    font-size: 15px !important;
    margin-bottom: 3px;
    margin-right: 3px;
}
.custom-hotel-badge {
    width: 38px !important;
    height: 38px !important;
    background: #333 !important;
    border-radius: 50% !important;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid white !important;
    box-shadow: 0 3px 12px rgba(0,0,0,0.4) !important;
}
.preview-badge {
    background: #f39c12 !important;
    color: white !important;
    width: 26px !important;
    height: 26px !important;
    border-radius: 50% !important;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid white !important;
    font-weight: bold !important;
}

.reroll-btn {
  width: 100%;
  margin-top: 15px;
  padding: 10px;
  background: #f0f7ff;
  border: 1px dashed #7B9DFF;
  color: #7B9DFF;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.reroll-btn:hover {
  background: #7B9DFF;
  color: white;
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