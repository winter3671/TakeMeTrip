<template>
  <div class="map-wrapper">
    <div class="sidebar" :class="{ 'closed': !isSidebarOpen }">
      
      <div class="sidebar-content">
        <div class="address-box">
          <span class="address-label">현재 위치</span>
          <h2 class="address-text">{{ currentAddress || '위치 확인 중...' }}</h2>
        </div>

        <div class="category-box">
          <ul class="category-list">
            <li v-for="item in localCategories" :key="item.id">
              <button 
                class="category-btn" 
                :class="{ 'active': selectedCategory === item.id }"
                @click="selectCategory(item.id)"
              >
                <span class="icon">{{ item.icon }}</span> 
                <span class="label">{{ item.name }}</span>
              </button>
            </li>
          </ul>
        </div>

        <div class="place-list-box">
          <div v-if="isLoading" class="status-msg">
            데이터를 불러오는 중...
          </div>

          <ul v-else-if="places.length > 0" class="place-list">
            <li v-for="place in places" :key="place.id" class="place-item" @click="moveToPlace(place)">
              <div class="place-thumb">
                <img v-if="place.thumbnail_image" :src="place.thumbnail_image" alt="img" />
                <div v-else class="no-img">No Image</div>
              </div>
              <div class="place-info">
                <div class="info-top">
                  <strong class="place-title">{{ place.title }}</strong>
                  <span class="place-cat">{{ place.category_name }}</span>
                </div>
                <span class="place-dist" v-if="myLocation">
                  내 위치로부터 {{ getDistanceFromLatLon(myLocation.lat, myLocation.lng, place.mapy, place.mapx) }}
                </span>
                <div class="bookmark-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
              </div>
            </li>
          </ul>

          <div v-else class="status-msg empty">
            <span class="empty-icon">😢</span>
            <p>이 주변에는 여행지가 없네요.</p>
          </div>
        </div>
      </div>

      <button class="sidebar-toggle-btn" @click="toggleSidebar" title="사이드바 토글">
        <svg v-if="isSidebarOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline> </svg>
        <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline> </svg>
      </button>

    </div>

    <div id="map"></div>
    
    <div class="search-btn-container" v-if="showSearchBtn">
      <button class="btn-redo-search" @click="searchInCurrentMap">
        <span class="redo-icon">↻</span> 현 지도에서 검색
      </button>
    </div>

    <div class="MapControlView">
      <button @click="moveToCurrentLocation" class="btn-location" title="내 위치로 가기">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm8.94 3c-.46-4.17-3.77-7.48-7.94-7.94V1h-2v2.06C6.83 3.52 3.52 6.83 3.06 11H1v2h2.06c.46 4.17 3.77 7.48 7.94 7.94V23h2v-2.06c4.17-.46 7.48-3.77 7.94-7.94H23v-2h-2.06zM12 19c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/></svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
// ★ Axios 제거하고 Pinia Store Import
import { useTripStore } from '@/stores/trips';

const tripStore = useTripStore();

let map = null;
let currentOverlay = null;
let geocoder = null;
let markers = [];

const currentAddress = ref('');
const currentRegionName = ref(''); 
const localCategories = ref([]); // Store 데이터를 받아와서 아이콘을 입힐 로컬 변수
const places = ref([]);
const showSearchBtn = ref(false);
const selectedCategory = ref(null);
const isLoading = ref(false);
const myLocation = ref(null);

const isSidebarOpen = ref(true);

const iconMap = {
  '관광지': '🚗', '문화시설': '🏛️', '축제/공연': '🎉',
  '여행코스': '🗺️', '레포츠': '⚽', '숙박': '🏠',
  '쇼핑': '🛍️', '음식점': '🍽️'
};

onMounted(async () => {
  await fetchCategories();
  if (window.kakao && window.kakao.maps) {
    initMap();
  } else {
    const script = document.createElement('script');
    script.onload = () => kakao.maps.load(initMap);
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&libraries=services`;
    document.head.appendChild(script);
  }
});

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

// ★ Store Action 사용: 카테고리 데이터
const fetchCategories = async () => {
  try {
    // axios 대신 store의 getCategories 사용
    const data = await tripStore.getCategories();
    
    // 아이콘 매핑
    localCategories.value = data.map(item => ({
      id: item.id,
      name: item.name,
      icon: iconMap[item.name] || '📍'
    }));
  } catch (error) {
    console.log("카테고리 로드 실패");
  }
};

// ★ Store Action 사용: 장소(여행지) 데이터
const fetchPlaces = async () => {
  if (!currentRegionName.value) return;

  isLoading.value = true;
  places.value = [];

  try {
    const params = {
      area: currentRegionName.value
    };
    if (selectedCategory.value) {
      params.category = selectedCategory.value;
    }

    // axios 대신 store의 getTrips 사용
    const data = await tripStore.getTrips(params);
    places.value = data;

    updateMarkers();
    
  } catch (error) {
    console.error("장소 로드 실패", error);
  } finally {
    isLoading.value = false;
  }
};

const updateMarkers = () => {
  if (markers.length > 0) {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
  }

  if (!places.value || places.value.length === 0) return;

  places.value.forEach(place => {
    if (!place.mapy || !place.mapx) return;

    const position = new window.kakao.maps.LatLng(place.mapy, place.mapx);

    const marker = new window.kakao.maps.Marker({
      position: position,
      map: map,
      title: place.title
    });

    window.kakao.maps.event.addListener(marker, 'click', () => {
      map.panTo(position);
      if (!isSidebarOpen.value) {
        isSidebarOpen.value = true;
      }
    });

    markers.push(marker);
  });
}

const selectCategory = (categoryId) => {
  if (selectedCategory.value === categoryId) {
    selectedCategory.value = null;
  } else {
    selectedCategory.value = categoryId;
  }
  fetchPlaces();
};

const initMap = () => {
  const container = document.getElementById('map');
  const options = { center: new window.kakao.maps.LatLng(33.450701, 126.570667), level: 3 };
  map = new window.kakao.maps.Map(container, options);
  geocoder = new window.kakao.maps.services.Geocoder();

  window.kakao.maps.event.addListener(map, 'dragend', () => { showSearchBtn.value = true; });
  moveToCurrentLocation();
};

const searchInCurrentMap = () => {
  if (!map) return;
  const center = map.getCenter();
  searchAddrFromCoords(center.getLng(), center.getLat());
  showSearchBtn.value = false;
};

const moveToCurrentLocation = () => {
  if (!map) return;
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const locPosition = new window.kakao.maps.LatLng(lat, lon);

        myLocation.value = { lat, lng: lon };

        map.panTo(locPosition);
        displayUserLocation(locPosition);
        searchAddrFromCoords(lon, lat);
        showSearchBtn.value = false;
      },
      (error) => alert('위치 정보를 가져올 수 없습니다.')
    );
  } else {
    alert('GPS를 사용할 수 없습니다.');
  }
};

const displayUserLocation = (locPosition) => {
  if (currentOverlay) {
    currentOverlay.setPosition(locPosition);
  } else {
    const content = '<div class="user-location-dot"></div>';
    currentOverlay = new window.kakao.maps.CustomOverlay({
      map: map, position: locPosition, content: content, yAnchor: 1
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

        const newRegionName = region.region_2depth_name;
        
        if (currentRegionName.value !== newRegionName) {
           currentRegionName.value = newRegionName;
           selectedCategory.value = null; 
           fetchPlaces();
        }
      }
    }
  });
};

const getDistanceFromLatLon = (lat1, lon1, lat2, lon2) => {
  if (!lat1 || !lon1 || !lat2 || !lon2) return "";
  const R = 6371;
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const d = R * c; 
  if (d < 1) return (d * 1000).toFixed(0) + "m";
  return d.toFixed(1) + "km";
}

const deg2rad = (deg) => { return deg * (Math.PI/180); }

const moveToPlace = (place) => {
  if(!map) return;
  const moveLatLon = new window.kakao.maps.LatLng(place.mapy, place.mapx);
  map.panTo(moveLatLon);
};
</script>

<style>
body, html { margin: 0; padding: 0; width: 100%; height: 100%;}
.user-location-dot { width: 16px; height: 16px; background: #4285F4; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.5); }
</style>

<style scoped>
.map-wrapper { position: relative; width: 100%; height: 100vh; }
#map { width: 100%; height: 100%; }

.sidebar {
  position: absolute; top: 0; left: 0;
  width: 360px; height: 100%;
  background-color: white; z-index: 20;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
  transition: transform 0.3s ease-in-out;
  transform: translateX(0);
}

.sidebar.closed {
  transform: translateX(-100%);
}

.sidebar-content {
  width: 100%; height: 100%;
  display: flex; flex-direction: column;
}

.sidebar-toggle-btn {
  position: absolute;
  top: 50%;
  right: -24px;
  width: 24px;
  height: 48px;
  transform: translateY(-50%);
  background-color: white;
  border: 1px solid #ddd;
  border-left: none;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 2px 0 4px rgba(0,0,0,0.1);
  z-index: 21;
}
.sidebar-toggle-btn:hover { background-color: #f7f7f7; }

.address-box { padding: 24px 20px; border-bottom: 1px solid #f0f0f0; flex-shrink: 0; }
.address-label { font-size: 13px; color: #888; display: block; margin-bottom: 4px; }
.address-text { font-size: 20px; font-weight: 700; margin: 0; color: #333; }

.category-box { padding: 15px; border-bottom: 1px solid #f0f0f0; flex-shrink: 0; }
.category-list { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; list-style: none; padding: 0; margin: 0; }
.category-btn {
  background: none; border: none; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 5px;
}
.category-btn .icon { font-size: 24px; }
.category-btn .label { font-size: 11px; color: #666; font-weight: 500; }
.category-btn.active .label { color: #4285F4; font-weight: 700; }

.place-list-box { flex: 1; overflow-y: auto; background-color: #fff; }
.place-list { list-style: none; padding: 0; margin: 0; }

.place-item {
  display: flex; padding: 16px 20px; border-bottom: 1px solid #f5f5f5; cursor: pointer; transition: background 0.2s;
}
.place-item:hover { background-color: #f9f9f9; }

.place-thumb {
  width: 72px; height: 72px; border-radius: 12px; overflow: hidden; margin-right: 16px; flex-shrink: 0; background-color: #eee; border: 1px solid #f0f0f0;
}
.place-thumb img { width: 100%; height: 100%; object-fit: cover; }
.no-img { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #aaa; }

.place-info { flex: 1; display: flex; flex-direction: column; position: relative; justify-content: center; }
.info-top { margin-bottom: 4px; }
.place-title { font-size: 16px; font-weight: 700; color: #333; margin-right: 6px; }
.place-cat { font-size: 12px; color: #999; }
.place-dist { font-size: 13px; color: #666; margin-top: 4px; }
.bookmark-icon { position: absolute; bottom: 0; right: 0; }

.status-msg { padding: 40px; text-align: center; color: #999; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.status-msg.empty .empty-icon { font-size: 32px; }

.search-btn-container { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 15; }
.btn-redo-search { background: white; color: #4285F4; border: 1px solid #ddd; border-radius: 20px; padding: 10px 20px; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; display: flex; align-items: center; gap: 5px; }
.MapControlView { position: absolute; top: 20px; right: 20px; z-index: 10; }
.btn-location { width: 45px; height: 45px; background: white; border: 1px solid #ddd; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>