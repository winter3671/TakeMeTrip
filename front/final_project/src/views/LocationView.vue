<template>
  <div class="course-container">
    <div class="course-section">
      
      <div class="list-header">
        <h2 class="header-title">#{{ selectedTag }}</h2>
        <div class="header-utils">
          <span class="total-count">총 {{ store.totalCount }} 건</span>
          <div class="sort-options">
            <span :class="{ active: currentSort === '-created_at' }" @click="changeSort('-created_at')">최신순</span> 
            | 
            <span :class="{ active: currentSort === 'distance' }" @click="changeSort('distance')">거리순</span>
            |
            <span :class="{ active: currentSort === '-recommendation_score' }" @click="changeSort('-recommendation_score')">인기순</span>
          </div>
        </div>
      </div>
      <hr class="header-line" />

      <div class="course-list">
        <div v-if="isLoading" class="status-msg">로딩 중...</div>
        
        <div v-else-if="store.trips.length === 0" class="status-msg empty">
          등록된 여행코스가 없습니다.
        </div>

        <div v-else>
          <LocationCard 
            v-for="trip in store.trips" 
            :key="trip.id" 
            :trip="trip" 
          />
        </div>
      </div>

      <div class="pagination" v-if="totalPages > 0">
        
        <button 
          class="page-btn move" 
          :disabled="currentPage === 1" 
          @click="changePage(1)"
        >
          &lt;&lt;
        </button>

        <button 
          class="page-btn move" 
          :disabled="currentPage === 1" 
          @click="changePage(currentPage - 1)"
        >
          &lt;
        </button>

        <button 
          v-for="page in visiblePages" 
          :key="page" 
          class="page-btn number"
          :class="{ active: currentPage === page }"
          @click="changePage(page)"
        >
          {{ page }}
        </button>

        <button 
          class="page-btn move" 
          :disabled="currentPage === totalPages" 
          @click="changePage(currentPage + 1)"
        >
          &gt;
        </button>

        <button 
          class="page-btn move" 
          :disabled="currentPage === totalPages" 
          @click="changePage(totalPages)"
        >
          &gt;&gt;
        </button>

      </div>

    </div>

    <section class="tag-bar">
      <div class="tag-header">
        <button class="refresh-btn" @click="selectTag('전체')" title="필터 초기화">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
        </button>
      </div>

      <div class="tag-list">
        <button 
          v-for="tag in regionTags" 
          :key="tag" 
          class="tag-btn"
          :class="{ active: selectedTag === tag }"
          @click="selectTag(tag)"
        >
          #{{ tag }}
        </button>
      </div>
      <hr>
      <div class="tag-list category-list">
        <button
        v-for="tag in categoryTags"
        :key="tag"
        class="tag-btn"
      >
        #{{ tag }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import LocationCard from '@/components/LocationCard.vue';
import { useTripStore } from '@/stores/trips';
import { ref, onMounted, computed } from 'vue'

const store = useTripStore()
const isLoading = ref(false)
const currentPage = ref(1)
const currentCategoryId = ref(null)
const currentSort = ref('-created_at')

const userLocation = ref(null)

const regionTags = [
  '전체', '서울', '인천', '대전', 
  '대구', '광주', '부산', '울산', 
  '세종', '경기', '강원', '충북', 
  '충남', '경북', '경남', '전북', 
  '전남', '제주'
];

const categoryTags = [
  '관광지', '문화시설', '축제/공연', '여행코스',
  '레포츠', '음식점', '숙박', '쇼핑'
]

const selectedTag = ref('전체');

const totalPages = computed(() => Math.ceil(store.totalCount / 10));

const visiblePages = computed(() => {
  const pageLimit = 5;
  const currentGroup = Math.ceil(currentPage.value / pageLimit);
  const start = (currentGroup - 1) * pageLimit + 1;
  const end = Math.min(start + pageLimit - 1, totalPages.value);
  const pages = [];
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
})

const getUserLocation = () => {
  if (!navigator.geolocation) {
    console.log("이 브라우저는 위치 정보를 지원하지 않습니다.");
    return;
  }
  navigator.geolocation.getCurrentPosition((position) => {
    userLocation.value = {
      lat: position.coords.latitude,
      lon: position.coords.longitude
    };
  }, (err) => {
    console.error("위치 정보를 가져올 수 없습니다:", err);
  });
}

const loadData = async (page) => {
  isLoading.value = true;
  try {
    if (!currentCategoryId.value) {
      const categories = await store.getCategories();
      const target = categories.find(c => c.name === '여행코스');
      if (target) currentCategoryId.value = target.id;
    }

    if (currentCategoryId.value) {
      const params = {
        category: currentCategoryId.value,
        page: page,
        ordering: currentSort.value
      };

      if (selectedTag.value !== '전체') {
        params.area = selectedTag.value;
      }

      if (currentSort.value === 'distance' && userLocation.value) {
        params.lat = userLocation.value.lat;
        params.lon = userLocation.value.lon;
      }

      await store.getTrips(params);
    }
  } catch (e) {
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

const selectTag = (tag) => {
  if (selectedTag.value === tag) return;
  selectedTag.value = tag;
  currentPage.value = 1;
  loadData(1);
};

const changeSort = (sortType) => {
  if (currentSort.value === sortType) return;

  if (sortType === 'distance' && !userLocation.value) {
    alert("위치 정보를 확인하는 중입니다. 잠시 후 다시 시도해주세요.\n(위치 권한을 허용해야 합니다)");
    getUserLocation();
    return;
  }

  currentSort.value = sortType;
  currentPage.value = 1; 
  loadData(1);
};

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  loadData(page);
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

onMounted(() => {
  getUserLocation();
  loadData(1);
});
</script>

<style scoped>
.course-container {
  display: flex; 
  width: 100%; 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 40px 20px; 
  gap: 40px;
  min-height: 100vh;
  overflow: visible;
}

.course-section { 
  flex: 2; 
}

.tag-bar { 
  flex: 1;
  min-width: 200px;
}

.tag-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.refresh-btn {
  background: none; border: none; cursor: pointer; color: #333;
  transition: transform 0.3s;
}
.refresh-btn:hover { transform: rotate(180deg); }

.tag-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.tag-btn {
  background-color: #f0f0f0;
  border: none;
  border-radius: 20px;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-btn:hover {
  background-color: #e0e0e0;
}

.tag-btn.active {
  background-color: #333;
  color: white;
}

.list-header { 
  margin-bottom: 10px; 
}

.header-title { 
  font-size: 28px; 
  font-weight: 800; 
  margin-bottom: 10px; 
  color: #333; 
}

.header-utils { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  font-size: 14px; 
  color: #666; 
}

.header-line { 
  border: 0; 
  height: 2px; 
  background-color: #333; 
  margin-bottom: 0; 
}

.sort-options span { 
  cursor: pointer; 
  margin: 0 5px; 
}

.sort-options span.active { 
  font-weight: bold; 
  color: #333; 
}

.status-msg { 
  padding: 60px 0; 
  text-align: center; 
  color: #888; 
  font-size: 16px; 
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 40px;
  margin-bottom: 40px;
}

.page-btn {
  background-color: white;
  border: 1px solid #ddd;
  color: #666;
  min-width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #333;
  color: #333;
}

.page-btn.active {
  background-color: #333;
  color: white;
  border-color: #333;
  font-weight: bold;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.category-list { 
  margin-top: 20px; 
}
</style>