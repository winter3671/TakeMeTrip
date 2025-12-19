<template>
  <div class="map-wrapper">
    <div class="sidebar">
      <div class="address-box">
        <span class="address-label">현재 위치</span>
        <h2 class="address-text">{{ currentAddress || '위치 찾는 중...' }}</h2>
      </div>

      <div class="category-box">
        <ul class="category-list">
          <li v-for="item in categories" :key="item.id">
            <button class="category-btn">
              <span class="icon">{{ item.icon }}</span>
              <span class="label">{{ item.name }}</span>
            </button>
          </li>
        </ul>
      </div>
    </div>

    <div id="map"></div>
    
    <div class="MapControlView">
      <button @click="moveToCurrentLocation" class="btn-location" title="현위치로 이동">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
          <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm8.94 3c-.46-4.17-3.77-7.48-7.94-7.94V1h-2v2.06C6.83 3.52 3.52 6.83 3.06 11H1v2h2.06c.46 4.17 3.77 7.48 7.94 7.94V23h2v-2.06c4.17-.46 7.48-3.77 7.94-7.94H23v-2h-2.06zM12 19c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';


let map = null;
let currentOverlay = null;
let geocoder = null;

const currentAddress = ref('');
const categories = [
  { id: 1, name: '주변 여행지', icon: '🚗' },
  { id: 2, name: '음식점', icon: '🍽️' },
  { id: 3, name: '카페', icon: '☕' },
  { id: 4, name: '숙소', icon: '🏠' },
  { id: 5, name: '주차장', icon: '🅿️' },
  { id: 6, name: '전기차충전', icon: '⚡' },
];

onMounted(() => {
  if (window.kakao && window.kakao.maps) {
    initMap();
  } else {
    const script = document.createElement('script');
    script.onload = () => kakao.maps.load(initMap);
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&libraries=services`;
    document.head.appendChild(script);
  }
});

const initMap = () => {
  const container = document.getElementById('map');
  const options = {
    center: new window.kakao.maps.LatLng(33.450701, 126.570667),
    level: 3,
  };

  map = new window.kakao.maps.Map(container, options);

  geocoder = new window.kakao.maps.services.Geocoder();

  moveToCurrentLocation();
};

const moveToCurrentLocation = () => {
  if (!map) return;

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const locPosition = new window.kakao.maps.LatLng(lat, lon);
        
        map.panTo(locPosition);

        displayUserLocation(locPosition);

        searchAddrFromCoords(lon, lat);
      },
      (error) => {
        console.error("Geolocation error:", error);
        alert('위치 정보를 가져올 수 없습니다.');
      }
    );
  } else {
    alert('이 브라우저에서는 위치 정보를 사용할 수 없습니다.');
  }
};

const displayUserLocation = (locPosition) => {
  if (currentOverlay) {
    currentOverlay.setPosition(locPosition);
  } else {
    const content = '<div class="user-location-dot"></div>';
    currentOverlay = new window.kakao.maps.CustomOverlay({
      map: map,
      position: locPosition,
      content: content,
      yAnchor: 1
    });
  }
};

const searchAddrFromCoords = (lng, lat) => {
  if (!geocoder) return;

  geocoder.coord2RegionCode(lng, lat, (result, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const region = result.find(r => r.region_type === 'H') || result[0];
      if (region) {
        currentAddress.value = `${region.region_1depth_name} ${region.region_2depth_name}`;
      }
    }
  });
};
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.user-location-dot {
  width: 16px;
  height: 16px;
  background-color: #4285F4;
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(0,0,0,0.5);
  transform: translate(-50%, -50%);
}
</style>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;
}

#map {
  width: 100%;
  height: 100%;
}

.sidebar {
  position: absolute;
  top: 0;
  left: 0;
  width: 350px;
  height: 100%;
  background-color: white;
  z-index: 20;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.address-box {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.address-label {
  font-size: 12px;
  color: #666;
  display: block;
  margin-bottom: 5px;
}

.address-text {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.category-box {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.category-btn {
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
  border-radius: 8px;
  transition: background 0.2s;
}

.category-btn:hover {
  background-color: #f5f5f5;
}

.category-btn .icon {
  font-size: 24px;
}

.category-btn .label {
  font-size: 13px;
  color: #333;
}

.MapControlView {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.btn-location {
  width: 45px;
  height: 45px;
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-location svg {
  fill: #333;
}
</style>