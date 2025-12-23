<template>
  <div class="search-page-container">
    
    <section class="result-section">
      <div class="header-group">
        <h2 class="section-title">
          "{{ keyword }}" 검색 결과
          <span class="count" v-if="trips.length > 0">({{ displayTotalCount }})</span>
        </h2>
        
        <p v-if="isOverMaxLimit" class="limit-warning">
          * 검색 결과는 최대 120개까지만 확인 가능합니다.
        </p>
      </div>

      <div v-if="loading" class="loading-msg">
        열심히 찾고 있어요... 🕵️‍♂️
      </div>

      <div v-else-if="trips.length > 0">
        <div class="card-grid">
          <CourseCard 
            v-for="trip in visibleTrips" 
            :key="trip.id" 
            :trip="trip" 
            @click="goDetail(trip.id)"
          />
        </div>

        <div class="load-more-box">
          <button 
            v-if="hasMoreItems && !isLimitReached" 
            class="load-more-btn" 
            @click="showMore"
          >
            결과 더 보기
          </button>

          <button 
            v-if="isLimitReached" 
            class="redirect-btn" 
            @click="goToRegionPage"
          >
            더 많은 여행정보 보기
          </button>
        </div>
      </div>

      <div v-else class="no-result">
        <div class="emoji">😢</div>
        <p>검색 결과가 없어요.</p>
        <p class="sub-text">철자가 정확한지 확인하거나 다른 검색어로 시도해 보세요.</p>
      </div>
    </section>

    <hr class="divider" />
    
    <section class="recommend-section">
      <h3 class="section-subtitle">
        <span class="highlight">이런 곳은 어때요?</span> 
      </h3>
      <div class="card-grid">
        <CourseCard 
          v-for="trip in recommendedTrips" 
          :key="trip.id" 
          :trip="trip" 
          @click="goDetail(trip.id)"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTripStore } from '@/stores/trips'
import CourseCard from '@/components/CourseCard.vue'

const INITIAL_VIEW = 12  // 초기 12개
const LOAD_STEP = 6      // 6개씩 추가
const MAX_LIMIT = 120    // 최대 120개 제한

const route = useRoute()
const router = useRouter()
const tripStore = useTripStore()

const keyword = ref('')
const trips = ref([])
const recommendedTrips = ref([])
const loading = ref(false)

// 화면에 보여줄 개수 상태
const visibleCount = ref(INITIAL_VIEW)

// 실제 화면에 뿌려줄 데이터
const visibleTrips = computed(() => {
  return trips.value.slice(0, visibleCount.value)
})

// 전체 개수 표시 텍스트
const displayTotalCount = computed(() => {
  const total = trips.value.length
  return total > MAX_LIMIT ? `${MAX_LIMIT}+` : total
})

// 전체 데이터가 120개를 넘는지
const isOverMaxLimit = computed(() => {
  return trips.value.length > MAX_LIMIT
})

// 더 보여줄 데이터가 남아있는지
const hasMoreItems = computed(() => {
  return visibleCount.value < trips.value.length
})

// 현재 보여주는 개수가 제한(120)에 도달했는지
const isLimitReached = computed(() => {
  return visibleCount.value >= MAX_LIMIT
})

// 더 보기 버튼 클릭
const showMore = () => {
  visibleCount.value += LOAD_STEP
  if (visibleCount.value > MAX_LIMIT) {
    visibleCount.value = MAX_LIMIT
  }
}

const goToRegionPage = () => {
  router.push('/location')
}

const goDetail = (id) => {
  router.push({ name: 'trip-detail', params: { id } })
}

const fetchSearchData = async () => {
  keyword.value = route.query.search || ''
  if (!keyword.value) return

  loading.value = true
  
  // 검색 결과 가져오기
  await tripStore.getTrips({ search: keyword.value, page_size: 150 }) 
  trips.value = [...tripStore.trips]
  
  // 검색할 때마다 보여줄 개수 초기화 (12개)
  visibleCount.value = INITIAL_VIEW

  // 추천 데이터
  const recData = await tripStore.getRandomTrips() 
  if (recData && recData.length > 0) {
    recommendedTrips.value = recData.slice(0, 6) 
  } else {
    recommendedTrips.value = []
  }
  
  loading.value = false
}

onMounted(() => {
  fetchSearchData()
})

watch(() => route.query.search, () => {
  fetchSearchData()
})
</script>

<style scoped>
.search-page-container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
.header-group { margin-bottom: 30px; }
.section-title { font-size: 28px; font-weight: 800; color: #333; margin-bottom: 5px; }
.count { font-size: 20px; color: #7B9DFF; margin-left: 5px; }

/* 안내 문구 스타일 */
.limit-warning { font-size: 14px; color: #888; margin-top: 5px; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }
.loading-msg { text-align: center; padding: 50px; font-size: 18px; color: #888; }
.no-result { text-align: center; padding: 80px 0; background: #f9f9f9; border-radius: 12px; margin-bottom: 30px; }
.divider { border: 0; height: 1px; background: #eee; margin: 60px 0; }
.section-subtitle { font-size: 22px; font-weight: 700; margin-bottom: 20px; color: #555; }
.highlight { box-shadow: inset 0 -10px 0 #e6eeff; }

/* 버튼 영역 스타일 */
.load-more-box { text-align: center; margin-top: 40px; }

/* 기존 더 보기 버튼 */
.load-more-btn {
  background-color: white;
  border: 1px solid #ddd;
  padding: 12px 40px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.load-more-btn:hover {
  background-color: #f9f9f9;
  border-color: #ccc;
  transform: translateY(-2px);
}

/* 이동 버튼 스타일 (강조) */
.redirect-btn {
  background-color: #7B9DFF;
  border: none;
  padding: 12px 40px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 700;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 10px rgba(123, 157, 255, 0.3);
}
.redirect-btn:hover {
  background-color: #6a8ce0;
  transform: translateY(-2px);
}
</style>