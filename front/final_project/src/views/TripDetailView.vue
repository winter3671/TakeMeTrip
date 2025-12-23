<template>
  <div class="detail-container" v-if="trip">
    <div class="image-section">
      <div v-if="trip.images && trip.images.length > 0" class="image-wrapper">
         <img :src="trip.images[0].image_url" :alt="trip.title" class="main-img" />
      </div>
      <div v-else class="image-wrapper">
         <img :src="trip.thumbnail_image || '/images/no-image.png'" class="main-img" />
      </div>
    </div>

    <div class="content-section">
      <div class="header-box">
        <span class="category-badge">{{ trip.category_name || '여행지' }}</span>
        <h1 class="title">{{ trip.title }}</h1>
        <p class="location-text">
          📍 {{ trip.destination || trip.address || '주소 정보 없음' }}
        </p>
      </div>

      <hr class="divider" />

      <div class="info-grid">
        <div class="info-item" v-if="trip.tel">
          <span class="label">📞 전화번호</span>
          <span class="value">{{ trip.tel }}</span>
        </div>
        
        <div class="info-item" v-if="trip.homepage">
          <span class="label">🌐 홈페이지</span>
          <span class="value link" v-html="trip.homepage"></span>
        </div>

        <div class="info-item" v-if="trip.use_time">
          <span class="label">⏰ 이용시간</span>
          <span class="value" v-html="trip.use_time"></span>
        </div>

        <div class="info-item" v-if="trip.rest_date">
          <span class="label">📅 휴무일</span>
          <span class="value" v-html="trip.rest_date"></span>
        </div>

        <div class="info-item" v-if="trip.parking">
          <span class="label">🚗 주차시설</span>
          <span class="value" v-html="trip.parking"></span>
        </div>
      </div>

      <hr class="divider" />

      <div class="overview-section" v-if="trip.overview">
        <h3>상세 소개</h3>
        <p class="overview-text">{{ trip.overview }}</p>
      </div>

      <div class="map-section">
        <h3>위치 보기</h3>
        <div id="detail-map" class="detail-map"></div>
      </div>
    </div>
  </div>
  
  <div v-else class="loading">
    데이터를 불러오는 중입니다...
  </div>
</template>

<script setup>
import { onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useTripStore } from '@/stores/trips'

const route = useRoute()
const tripStore = useTripStore()

const trip = computed(() => tripStore.tripDetail)

onMounted(async () => {
  const tripId = route.params.id
  await tripStore.getTripDetail(tripId)
  
  if (trip.value) {
    await nextTick()
    // 데이터 로드 후 지도 그리기 시작
    loadKakaoMap(trip.value.mapy, trip.value.mapx)
  }
})

const loadKakaoMap = (lat, lng) => {
  if (!window.kakao || !window.kakao.maps) {
    setTimeout(() => loadKakaoMap(lat, lng), 100)
    return
  }

  // 지도 컨테이너 확인
  const container = document.getElementById('detail-map')
  if (!container) return 

  // 좌표 유효성 검사
  const y = parseFloat(lat)
  const x = parseFloat(lng)
  
  // 좌표가 없거나 0이면 지도 생성 중단
  if (!y || !x) return

  const options = {
    center: new window.kakao.maps.LatLng(y, x),
    level: 3
  }
  
  const map = new window.kakao.maps.Map(container, options)

  const markerPosition = new window.kakao.maps.LatLng(y, x)
  const marker = new window.kakao.maps.Marker({
    position: markerPosition
  })

  marker.setMap(map)
  
  // 레이아웃 깨짐 방지
  setTimeout(() => map.relayout(), 100)
}
</script>

<style scoped>
.detail-container { max-width: 800px; margin: 0 auto; background: #fff; padding-bottom: 50px; }
.image-wrapper { width: 100%; height: 400px; background: #eee; }
.main-img { width: 100%; height: 100%; object-fit: cover; }
.content-section { padding: 30px 20px; }
.category-badge { background: #7B9DFF; color: white; padding: 5px 12px; border-radius: 15px; font-size: 13px; font-weight: bold; }
.title { font-size: 28px; font-weight: 800; margin: 10px 0; color: #333; }
.location-text { color: #666; font-size: 16px; margin-bottom: 20px; }
.divider { border: 0; height: 1px; background: #eee; margin: 30px 0; }
.info-grid { display: grid; gap: 15px; background: #f9f9f9; padding: 20px; border-radius: 12px; }
.info-item { display: flex; font-size: 15px; line-height: 1.6; }
.label { width: 100px; font-weight: 700; color: #555; flex-shrink: 0; }
.value { color: #333; word-break: break-all; }
.value :deep(a) { color: #7B9DFF; text-decoration: underline; }
.overview-text { line-height: 1.8; color: #444; font-size: 16px; white-space: pre-line; }
.detail-map {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  margin-top: 15px;
  background-color: #eee;
}
.loading { text-align: center; padding: 50px; color: #888; }
@media (min-width: 768px) { .info-grid { grid-template-columns: 1fr 1fr; } }
</style>