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
                <div class="slide-info">
                  <span>{{ trip.title }}</span>
                </div>
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
      <div v-if="localCategories.length === 0" class="loading-text">로딩 중...</div>
      <div v-else class="category-list">
        <div v-for="item in localCategories" :key="item.id" class="category-item">
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

      <div class="rec-slider-container">
        <div v-if="isLoading" class="no-data">데이터를 불러오는 중...</div>
        
        <div v-else-if="tabData.length === 0" class="no-data">
          {{ currentTab === 'wishlist' ? '찜한 여행지가 없습니다. ❤️를 눌러 담아보세요!' : '추천 여행지가 없습니다.' }}
        </div>

        <div v-else class="slider-wrapper rec-slider-wrapper">
          <button class="nav-btn prev" @click="prevRecSlide" :disabled="recIndex === 0">&lt;</button>
          
          <div class="slider-window rec-slider-window">
            <div 
              class="slider-track"
              :style="{ transform: `translateX(-${recIndex * (260 + 20)}px)` }"
            >
              <div 
                v-for="trip in tabData" 
                :key="trip.id" 
                class="card-item slider-card" 
                @click="goToDetail(trip.id)"
              >
                <img :src="trip.thumbnail_image || noImage" alt="여행지" class="card-img" />
                <button class="heart-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                </button>
                <div class="card-overlay">
                  <h3 class="card-title">{{ trip.title }}</h3>
                  <p class="card-location">{{ trip.region_name }} {{ trip.city_name }}</p>
                </div>
              </div>
            </div>
          </div>

          <button class="nav-btn next" @click="nextRecSlide" :disabled="isRecEnd">&gt;</button>
        </div>
      </div>

      <div class="action-btn-area">
        <button class="ai-full-btn" @click="refreshData">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg> 새로고침
        </button>
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
import { useRouter } from 'vue-router';
import { useTripStore } from '@/stores/trips';
import { useAccountStore } from '@/stores/accounts';
import { storeToRefs } from 'pinia';

import banner1 from '@/assets/banner1.png';
import banner2 from '@/assets/banner2.png';
import banner3 from '@/assets/banner3.png';
import noImage from '@/assets/no_image.png';

const tripStore = useTripStore();
const accountStore = useAccountStore();
const router = useRouter();

const localCategories = ref([]);
const tabData = ref([]);
const currentTab = ref('recommend');
const bannerTrips = ref([]);
const selectedCategory = ref(null);
const isLoading = ref(false);

const currentIndex = ref(0);
const prevSlide = () => { if (currentIndex.value > 0) currentIndex.value--; };
const nextSlide = () => { if (currentIndex.value < bannerTrips.value.length - 3) currentIndex.value++; };
const isEnd = computed(() => currentIndex.value >= bannerTrips.value.length - 3);

const recIndex = ref(0);
const visibleRecCount = 4;
const prevRecSlide = () => { if (recIndex.value > 0) recIndex.value--; };
const nextRecSlide = () => { 
  if (recIndex.value < tabData.value.length - visibleRecCount) recIndex.value++; 
};
const isRecEnd = computed(() => recIndex.value >= tabData.value.length - visibleRecCount);

const infoBanners = ref([ { img: banner1 }, { img: banner2 }, { img: banner3 } ]);
const iconMap = { '관광지': '🚗', '문화시설': '🏛️', '축제/공연': '🎉', '여행코스': '🗺️', '레포츠': '⚽', '숙박': '🏠', '쇼핑': '🛍️', '음식점': '🍽️' };

const shuffleArray = (array) => {
  let _array = [...array];
  for (let i = _array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [_array[i], _array[j]] = [_array[j], _array[i]];
  }
  return _array;
};

const fetchTabData = async () => {
  isLoading.value = true;
  tabData.value = [];
  recIndex.value = 0;

  try {
    if (currentTab.value === 'recommend') {
      const data = await tripStore.getRandomTrips(selectedCategory.value);
      tabData.value = data; 

    } else if (currentTab.value === 'ai') {
      const data = await tripStore.getRandomTrips(null);
      tabData.value = data;

    } else if (currentTab.value === 'wishlist') {
      if (!accountStore.isLogin) {
        tabData.value = [];
      } else {
        const fullWishlist = await tripStore.getMyWishlist();
        if (fullWishlist && fullWishlist.length > 0) {
           const shuffled = shuffleArray(fullWishlist);
           tabData.value = shuffled.slice(0, 10);
        } else {
           tabData.value = [];
        }
      }
    }
  } catch (error) {
    console.error("Data load failed:", error);
  } finally {
    isLoading.value = false;
  }
};

const fetchBannerTrips = async () => {
  try {
    const data = await tripStore.getRandomBannerTrips();
    if (data && data.length > 0) {
      bannerTrips.value = data;
    }
  } catch (error) {
    console.error("Banner load failed:", error);
  }
};

const fetchCategories = async () => {
  const data = await tripStore.getCategories();
  localCategories.value = data.map(item => ({
    id: item.id, 
    name: item.name, 
    icon: iconMap[item.name] || '📍'
  }));
};

const selectCategory = (categoryId) => {
  if (selectedCategory.value === categoryId) {
    selectedCategory.value = null;
  } else {
    selectedCategory.value = categoryId;
  }
  
  if (currentTab.value !== 'recommend') {
    currentTab.value = 'recommend';
  }
  fetchTabData();
};

const switchTab = async (tabName) => {
  currentTab.value = tabName;
  if (tabName !== 'recommend') selectedCategory.value = null;
  fetchTabData();
};

const refreshData = () => {
  fetchTabData();
};

const goToDetail = (id) => { 
    router.push({ name: 'detail', params: { id } });
};

onMounted(() => {
  fetchBannerTrips();
  fetchCategories();
  fetchTabData();
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

.rec-slider-wrapper {
  position: relative;
  bottom: auto;
  width: 100%;
  max-width: 1060px;
  height: 320px; 
  margin: 0 auto;
}

.slider-window { 
  width: 100%; 
  height: 100%; 
  overflow: hidden; 
  border-radius: 16px; 
  position: relative;
}

.rec-slider-window {
  width: 100%;
}

.slider-track { 
  display: flex; 
  gap: 20px; 
  transition: transform 0.4s ease-in-out; 
  height: 100%;
  padding-left: 0; 
}

.slider-card {
  width: 260px; 
  min-width: 260px;
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
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
  font-size: 20px;
  color: #333;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.nav-btn:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 1);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 6px 14px rgba(0,0,0,0.2);
}

.nav-btn:disabled {
  opacity: 0;
  cursor: default;
  pointer-events: none;
}

.nav-btn.prev {
  left: 15px;
}

.nav-btn.next {
  right: 15px;
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

.rec-slider-container {
  width: 100%;
  display: flex;
  justify-content: center;
  min-height: 320px;
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

.card-item { 
  position: relative; 
  height: 300px; 
  border-radius: 4px; 
  overflow: hidden; 
  cursor: pointer; 
  box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
  transition: transform 0.2s; 
  flex-shrink: 0;
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
  text-align: center; 
  padding: 40px; 
  color: #888; 
  width: 100%;
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
  .bottom-banners { 
    grid-template-columns: 1fr; 
  }

  .slider-window, .slider-wrapper { 
    width: 100%; 
  }
}
</style>