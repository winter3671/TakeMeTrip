<template>
  <div class="course-container">
    <div class="course-section">
      
      <div class="list-header">
        <h2 class="header-title">#전체</h2>
        <div class="header-utils">
          <span class="total-count">총 {{ store.totalCount }} 건</span>
          
          <div class="sort-options">
            <span 
              :class="{ active: currentSort === '-created_at' }"
              @click="changeSort('-created_at')"
            >
              최신순
            </span> 
            | 
            <span 
              :class="{ active: currentSort === '-recommendation_score' }"
              @click="changeSort('-recommendation_score')"
            >
              인기순
            </span>
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
          <CourseCard 
            v-for="trip in store.trips" 
            :key="trip.id" 
            :trip="trip" 
          />
        </div>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn prev" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">&lt;</button>
        <button 
          v-for="page in totalPages" 
          :key="page" 
          class="page-btn number"
          :class="{ active: currentPage === page }"
          @click="changePage(page)"
        >
          {{ page }}
        </button>
        <button class="page-btn next" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">&gt;</button>
      </div>

    </div>

    <section class="tag-bar">
      </section>
  </div>
</template>

<script setup>
import CourseCard from '@/components/CourseCard.vue';
import { useTripStore } from '@/stores/trips';
import { ref, onMounted, computed } from 'vue'

const store = useTripStore()
const isLoading = ref(false)
const currentPage = ref(1)
const currentCategoryId = ref(null)

const currentSort = ref('-created_at')

const totalPages = computed(() => {
  return Math.ceil(store.totalCount / 10);
})

const loadData = async (page) => {
  isLoading.value = true;
  try {
    if (!currentCategoryId.value) {
      const categories = await store.getCategories();
      const target = categories.find(c => c.name === '여행코스');
      if (target) currentCategoryId.value = target.id;
    }

    if (currentCategoryId.value) {
      await store.getTrips({ 
        category: currentCategoryId.value, 
        page: page,
        ordering: currentSort.value
      });
    }
  } catch (e) {
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

const changeSort = (sortType) => {
  if (currentSort.value === sortType) return;
  
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
  background-color: #f9f9f9; 
  height: 500px; 
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
</style>