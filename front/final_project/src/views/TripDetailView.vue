<template>
  <div class="detail-container" v-if="trip">
    <div class="image-section">
      <div class="image-wrapper">
        <div v-if="trip.images && trip.images.length > 0" class="img-box">
           <img :src="trip.images[0].image_url" :alt="trip.title" class="main-img" />
        </div>
        <div v-else class="img-box">
           <img :src="trip.thumbnail_image || '/images/no-image.png'" class="main-img" />
        </div>

        <button 
          class="like-overlay-btn" 
          :class="{ 'liked': trip.is_liked }" 
          @click.stop="handleLike"
        >
          <span class="heart-icon" v-if="trip.is_liked">❤️</span>
          <span class="heart-icon" v-else>🤍</span>
        </button>
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
import { useAccountStore } from '@/stores/accounts'

const route = useRoute()
const tripStore = useTripStore()
const accountStore = useAccountStore()

const trip = computed(() => tripStore.tripDetail)

onMounted(async () => {
  const tripId = route.params.id
  await tripStore.getTripDetail(tripId)
  
  if (trip.value) {
    await nextTick()
    loadKakaoMap(trip.value.mapy, trip.value.mapx)
  }
})

const loadKakaoMap = (lat, lng) => {
  if (!window.kakao || !window.kakao.maps) {
    setTimeout(() => loadKakaoMap(lat, lng), 100)
    return
  }

  const container = document.getElementById('detail-map')
  if (!container) return 

  const y = parseFloat(lat)
  const x = parseFloat(lng)
  
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
  setTimeout(() => map.relayout(), 100)
}

const handleLike = async () => {
  if (!accountStore.isLogin) {
    alert('로그인이 필요한 서비스입니다.')
    return
  }
  
  const newStatus = await tripStore.toggleLike(trip.value.id)
  
  if (newStatus !== null) {
    trip.value.is_liked = newStatus
  }
}
</script>

<style scoped>
.detail-container { max-width: 800px; margin: 0 auto; background: #fff; padding-bottom: 50px; }

/* 이미지 섹션: 하트 버튼 배치를 위해 relative 설정 */
.image-section { 
  width: 100%; 
  height: 400px; 
  margin-top: 5%;
  background: #eee; 
}
.image-wrapper {
  width: 100%;
  height: 100%;
  position: relative; /* ★ 자식 요소(하트)의 기준점 */
}
.img-box { width: 100%; height: 100%; }
.main-img { width: 100%; height: 100%; object-fit: cover; }

.like-overlay-btn {
  position: absolute;
  top: 20px;   /* 사진 상단에서 20px */
  right: 20px; /* 사진 우측에서 20px */
  
  background: none; /* 배경 없음 (투명) */
  border: none;
  cursor: pointer;
  z-index: 10;
  padding: 0;
  
  transition: transform 0.2s ease;
}

.like-overlay-btn:hover {
  transform: scale(1.15); /* 마우스 올리면 살짝 커짐 */
}

/* 하트 아이콘 스타일: 그림자*/
.heart-icon {
  font-size: 32px; /* 크기 조절 */
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); /* ★ 핵심: 그림자 */
  display: block; 
}

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
.detail-map { width: 100%; height: 400px; border-radius: 12px; margin-top: 15px; background-color: #eee; }
.loading { text-align: center; padding: 50px; color: #888; }

@media (min-width: 768px) { .info-grid { grid-template-columns: 1fr 1fr; } }
</style>