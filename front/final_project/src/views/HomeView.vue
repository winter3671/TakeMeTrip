<template>
  <div class="home-container">
    <div class="top-bar">
      <section class="banner">
        <div class="slider-wrapper" v-if="bannerTrips.length > 0">
          <button class="nav-btn prev" @click="prevSlide" :disabled="currentIndex === 0">&lt;</button>
          <div class="slider-window">
            <div 
              class="slider-track"
              :style="{ transform: `translateX(-${currentIndex * (280 + 20)}px)` }"
            >
              <div 
                v-for="trip in bannerTrips" 
                :key="trip.id" 
                class="slide-item"
                @click="goToDetail(trip.id)"
              >
                <img :src="trip.thumbnail_image" :alt="trip.title" />
                <div class="slide-info"></div>
              </div>
            </div>
          </div>
          <button class="nav-btn next" @click="nextSlide" :disabled="isEnd">&gt;</button>
        </div>
        <div v-else class="loading-msg">추천 여행지를 불러오는 중...</div>
      </section>
    </div>

    <div class="categories_recommend">
      <h2 class="section-title">카테고리</h2>
      <div v-if="categories.length === 0" class="loading-text">로딩 중...</div>
      <div v-else class="category-list">
        <div v-for="item in categories" :key="item.id" class="category-item">
          <button 
            class="category-circle" 
            :class="{ 'active': selectedCategory === item.id }"
            @click="selectCategory(item.id)"
          >
            <span class="emoji">{{ item.icon }}</span>
          </button>
          <span class="label" :class="{ 'active-label': selectedCategory === item.id }">
            {{ item.name }}
          </span>
        </div>
      </div>
    </div>

    <div class="recommendation-section">
      <div class="tabs-container">
        <div class="tab-item" :class="{ active: currentTab === 'recommend' }" @click="switchTab('recommend')">
          카테고리별 추천<div v-if="currentTab === 'recommend'" class="triangle"></div>
        </div>
        <div class="tab-divider">|</div>
        <div class="tab-item" :class="{ active: currentTab === 'ai' }" @click="switchTab('ai')">
          AI 기반 플래너<div v-if="currentTab === 'ai'" class="triangle"></div>
        </div>
        <div class="tab-divider">|</div>
        <div class="tab-item" :class="{ active: currentTab === 'wishlist' }" @click="switchTab('wishlist')">
          내가 찜한 장소<div v-if="currentTab === 'wishlist'" class="triangle"></div>
        </div>
      </div>

      <div class="card-grid">
        <div v-if="tabData.length === 0" class="no-data">
          {{ selectedCategory ? '해당 카테고리의 여행지가 없습니다.' : '데이터를 불러오는 중입니다...' }}
        </div>
        <div v-for="trip in tabData.slice(0, 4)" :key="trip.id" class="card-item" @click="goToDetail(trip.id)">
          <img :src="trip.thumbnail_image" alt="여행지 사진" class="card-img" />
          <button class="heart-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
          </button>
          <div class="card-overlay">
            <h3 class="card-title">{{ trip.title }}</h3>
            <p class="card-location">{{ trip.region_name }} {{ trip.city_name }}</p>
          </div>
        </div>
      </div>

      <div class="action-btn-area">
        <button class="ai-full-btn">오늘의 AI 추천</button>
      </div>

      <div class="bottom-banners">
        <div v-for="(banner, index) in infoBanners" :key="index" class="banner-item">
          <img :src="banner.img" alt="정보 배너" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import banner1 from '@/assets/banner1.png';
import banner2 from '@/assets/banner2.png';
import banner3 from '@/assets/banner3.png';

const router = useRouter();
const categories = ref([]);
const tabData = ref([]);
const currentTab = ref('recommend');
const bannerTrips = ref([]);
const currentIndex = ref(0);

const selectedCategory = ref(null);

const infoBanners = ref([ { img: banner1 }, { img: banner2 }, { img: banner3 } ]);
const iconMap = { '관광지': '🚗', '문화시설': '🏛️', '축제/공연': '🎉', '여행코스': '🗺️', '레포츠': '⚽', '숙박': '🏠', '쇼핑': '🛍️', '음식점': '🍽️' };

const prevSlide = () => { if (currentIndex.value > 0) currentIndex.value--; };
const nextSlide = () => { if (currentIndex.value < bannerTrips.value.length - 3) currentIndex.value++; };
const isEnd = computed(() => currentIndex.value >= bannerTrips.value.length - 3);

const fetchBannerTrips = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/trips/'); 
    let allTrips = response.data.results ? response.data.results : response.data;
    bannerTrips.value = allTrips.slice(0, 10);
  } catch (e) { console.error(e); }
};

const fetchCategories = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/trips/categories/');
    categories.value = response.data.map(item => ({
      id: item.id, name: item.name, icon: iconMap[item.name] || '📍'
    }));
  } catch (e) { console.error(e); }
};

const selectCategory = (categoryId) => {
  if (selectedCategory.value === categoryId) {
    selectedCategory.value = null;
  } else {
    selectedCategory.value = categoryId;
  }
  
  switchTab('recommend');
};

const switchTab = async (tabName) => {
  currentTab.value = tabName;
  tabData.value = [];

  try {
    let url = 'http://127.0.0.1:8000/api/trips/';
    let params = {};

    if (tabName === 'recommend') {
      params = { sort: 'recommendation_score' };
      
      if (selectedCategory.value) {
        params.category = selectedCategory.value;
      }
      
    } else if (tabName === 'ai') {
      params = { sort: 'latest' };
    } else if (tabName === 'wishlist') {
      params = {}; 
    }

    const response = await axios.get(url, { params });
    tabData.value = response.data.results ? response.data.results : response.data;
    
  } catch (e) {
    console.error("탭 데이터 로드 실패", e);
  }
};

const goToDetail = (id) => { console.log(id); };

onMounted(() => {
  fetchBannerTrips();
  fetchCategories();
  switchTab('recommend');
});
</script>

<style scoped>
.home-container {
  width: 100%; 
  height: calc(100vh - 80px); 
  overflow-y: auto;
  background-color: #fff; 
  scroll-behavior: smooth; 
  padding-bottom: 120px;
}

.home-container::-webkit-scrollbar { 
  display: none; 
}

.home-container { 
  -ms-overflow-style: none; 
  scrollbar-width: none; 
}

.top-bar { 
  padding-bottom: 0; 
}

.banner { 
  width: 100%; 
  height: 260px; 
  background-color: #FFB78B8F; 
  display: flex; 
  justify-content: center; 
  overflow: visible; 
  position: relative; 
  margin-bottom: 60px; 
}

.slider-wrapper { 
  position: absolute; 
  bottom: -40px; 
  width: 1000px; 
  height: 280px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
}

.slider-window { 
  width: 880px; 
  height: 100%; 
  overflow: hidden; 
  border-radius: 16px; 
}

.slider-track { 
  display: flex; 
  gap: 20px; 
  transition: transform 0.4s ease-in-out; 
  height: 100%; 
}

.slide-item { 
  width: 280px; 
  height: 100%; 
  flex-shrink: 0; 
  border-radius: 16px; 
  overflow: hidden; 
  position: relative; 
  cursor: pointer; 
  box-shadow: 0 10px 20px rgba(0,0,0,0.15); 
  background-color: #fff; 
  transition: transform 0.3s; 
}

.slide-item:hover { 
  transform: translateY(-5px); 
}

.slide-item img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
}

.slide-info { 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  width: 100%; 
  padding: 20px; 
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent); 
  color: white; 
  font-weight: bold; 
  font-size: 18px; 
}

.nav-btn { 
  background-color: white; 
  border: 1px solid #ddd; 
  width: 40px; 
  height: 40px; 
  border-radius: 50%; 
  cursor: pointer; 
  font-size: 20px; 
  color: #333; 
  box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
  z-index: 10; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  transition: all 0.2s; 
}

.nav-btn:hover:not(:disabled) { 
  background-color: #333; 
  color: white; 
}

.nav-btn:disabled { 
  opacity: 0.5; 
  cursor: not-allowed; 
}

.nav-btn.prev { 
  margin-right: 15px; 
}

.nav-btn.next { 
  margin-left: 15px; 
}

.loading-msg { 
  color: white; 
  font-weight: bold; 
  margin-top: 150px; 
}

.categories_recommend { 
  margin: 50px 0; 
  text-align: center; 
  padding: 0 20px; 
}

.section-title { 
  font-size: 20px; 
  font-weight: 700; 
  margin-bottom: 30px; 
  color: #333; 
}

.category-list { 
  display: flex; 
  justify-content: center; 
  gap: 20px; 
  flex-wrap: wrap; 
  max-width: 1000px; 
  margin: 0 auto; 
}

.category-item { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  gap: 10px; 
}

.category-circle {
  width: 70px; 
  height: 70px; 
  border-radius: 50%; 
  background-color: #fff;
  border: 1px solid #eee; 
  box-shadow: 0 4px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  font-size: 28px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  transition: all 0.2s;
}

.category-circle:hover { 
  transform: translateY(-3px); 
  box-shadow: 0 6px 12px rgba(0,0,0,0.12); 
}

.category-circle.active {
  background-color: #FFB78B;
  border-color: #FFB78B;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(255, 183, 139, 0.4);
}

.label { 
  font-size: 13px;
   color: #666; 
   font-weight: 500; 
}

.label.active-label { 
  color: #FFB78B; 
  font-weight: 700;
}

.recommendation-section { 
  max-width: 1000px; 
  margin: 0 auto; 
  padding: 0 20px; 
}

.tabs-container { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  background-color: #7B9DFF; 
  padding: 20px 0; 
  color: rgba(255, 255, 255, 0.7); 
  font-size: 16px; 
  position: relative; 
  margin-bottom: 30px; 
}

.tab-item { 
  cursor: pointer; 
  padding: 0 30px; 
  position: relative; 
  font-weight: 500; 
  transition: color 0.2s; 
}

.tab-item.active { 
  color: #fff; 
  font-weight: 700; 
}

.tab-divider { 
  color: rgba(255, 255, 255, 0.3); 
  font-size: 14px; 
}

.triangle { 
  position: absolute; 
  bottom: -28px; 
  left: 50%; 
  transform: translateX(-50%); 
  width: 0; 
  height: 0; 
  border-left: 10px solid transparent; 
  border-right: 10px solid transparent; 
  border-top: 10px solid #7B9DFF; 
}

.card-grid { 
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 15px; 
  margin-bottom: 40px; 
}

.card-item { 
  position: relative; 
  height: 300px; 
  border-radius: 4px; 
  overflow: hidden; 
  cursor: pointer; 
  box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
  transition: transform 0.2s; 
}

.card-item:hover { 
  transform: translateY(-5px); 
}

.card-img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
}

.heart-btn { 
  position: absolute;
  top: 10px; 
  right: 10px; 
  background: none; 
  border: none; 
  cursor: pointer; 
  padding: 5px; 
}

.card-overlay { 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  width: 100%; 
  padding: 20px 15px; 
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); 
  color: white; 
  text-align: left; 
}

.card-title { 
  font-size: 18px; 
  font-weight: 700; 
  margin: 0 0 5px 0; 
  text-shadow: 0 1px 3px rgba(0,0,0,0.5); 
}
.card-location { 
  font-size: 13px; 
  opacity: 0.9; 
  margin: 0; 
}

.action-btn-area { 
  text-align: center; 
  margin-top: 20px; 
}

.ai-full-btn { 
  background-color: white; 
  border: 1px solid #333; 
  color: #333; 
  padding: 15px 50px; 
  border-radius: 30px; 
  font-size: 16px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.2s; 
}

.ai-full-btn:hover { 
  background-color: #333; 
  color: white; 
}

.no-data { 
  grid-column: span 4; 
  text-align: center;
  padding: 40px; 
  color: #888; 
}

.bottom-banners { 
  margin-top: 60px; 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px; 
}

.banner-item { 
  width: 100%; 
  height: 120px; 
  border-radius: 12px; 
  overflow: hidden; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
  cursor: pointer; 
  transition: transform 0.2s; 
}

.banner-item:hover { 
  transform: translateY(-3px); 
}

.banner-item img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
}

@media (max-width: 768px) {
  .card-grid { 
    grid-template-columns: repeat(2, 1fr); 
  }

  .bottom-banners { 
    grid-template-columns: 1fr; 
  }

  .slider-window { 
    width: 100%; 
  } 

  .slider-wrapper { 
    width: 100%; 
  }
}
</style>