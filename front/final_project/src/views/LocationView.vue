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
            :userLocation="userLocation"
            @click="goDetail(trip.id)"
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
        <button class="refresh-btn" @click="resetFilters" title="필터 초기화">
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

      <Transition name="slide">
        <div v-if="subRegionList.length > 0" class="sub-tag-box">
          <button 
            class="sub-tag-btn"
            :class="{ active: selectedSubTag === '전체' || !selectedSubTag }"
            @click="selectSubTag('전체')"
          >
            전체
          </button>
          <button 
            v-for="subTag in subRegionList" 
            :key="subTag" 
            class="sub-tag-btn"
            :class="{ active: selectedSubTag === subTag }"
            @click="selectSubTag(subTag)"
          >
            {{ subTag }}
          </button>
        </div>
      </Transition>

      <hr>
      <div class="tag-list category-list">
        <button
        v-for="tag in categoryTags"
        :key="tag"
        class="tag-btn"
        :class="{ active: selectedCategoryTag === tag }"
        @click="selectCategoryTag(tag)"
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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter()

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

const subRegionData = {
  '서울': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
  '인천': ['강화군', '계양구', '남동구', '동구', '미추홀구', '부평구', '서구', '연수구', '옹진군', '중구'],
  '대전': ['대덕구', '동구', '서구', '유성구', '중구'],
  '대구': ['군위군', '남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구'],
  '광주': ['광산구', '남구', '동구', '북구', '서구'],
  '부산': ['강서구', '기장군', '금정구', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
  '울산': ['남구', '동구', '북구', '울주군', '중구'],
  '세종': ['세종시'],
  '경기': ['가평군', '고양시', '과천시', '광명시', '광주시', '구리시', '군포시', '김포시', '남양주시', '동두천시', '부천시', '성남시', '수원시', '시흥시', '안산시', '안성시', '안양시', '양주시', '양평군', '여주시', '연천군', '오산시', '용인시', '의왕시', '의정부시', '이천시', '파주시', '평택시', '포천시', '하남시', '화성시'],
  '강원': ['강릉시', '고성군', '동해시', '삼척시', '속초시', '양구군', '양양군', '영월군', '원주시', '인제군', '정선군', '철원군', '춘천시', '태백시', '평창군', '홍천군', '화천군', '횡성군'],
  '충북': ['괴산군', '단양군', '보은군', '영동군', '옥천군', '음성군', '제천시', '증평군', '진천군', '청주시', '충주시'],
  '충남': ['계룡시', '공주시', '금산군', '논산시', '당진시', '보령시', '부여군', '서산시', '서천군', '아산시', '예산군', '천안시', '청양군', '태안군', '홍성군'],
  '경북': ['경산시', '경주시', '고령군', '구미시', '김천시', '문경시', '봉화군', '상주시', '성주군', '안동시', '영덕군', '영양군', '영주시', '영천시', '예천군', '울릉군', '울진군', '의성군', '청도군', '청송군', '칠곡군', '포항시'],
  '경남': ['거제시', '거창군', '고성군', '김해시', '남해군', '밀양시', '사천시', '산청군', '양산시', '의령군', '진주시', '창녕군', '창원시', '통영시', '하동군', '함안군', '함양군', '합천군'],
  '전북': ['고창군', '군산시', '김제시', '남원시', '무주군', '부안군', '순창군', '완주군', '익산시', '임실군', '장수군', '전주시', '정읍시', '진안군'],
  '전남': ['강진군', '고흥군', '곡성군', '광양시', '구례군', '나주시', '담양군', '목포시', '무안군', '보성군', '순천시', '신안군', '여수시', '영광군', '영암군', '완도군', '장성군', '장흥군', '진도군', '함평군', '해남군', '화순군'],
  '제주': ['제주시', '서귀포시']
};

const categoryTags = [
  '관광지', '문화시설', '축제/공연', '여행코스',
  '레포츠', '음식점', '숙박', '쇼핑'
]

const selectedTag = ref('전체');
const selectedSubTag = ref(null);
const selectedCategoryTag = ref(null)

const subRegionList = computed(() => {
  if (selectedTag.value === '전체' || !subRegionData[selectedTag.value]) {
    return [];
  }
  return subRegionData[selectedTag.value];
});

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
    const params = {
      page: page,
      ordering: currentSort.value
    };

    if (selectedTag.value !== '전체') {
      if (selectedSubTag.value && selectedSubTag.value !== '전체') {
        params.area = selectedSubTag.value;
      } 
      else {
        params.area = selectedTag.value;
      }
    }

    // 카테고리 필터
    if (selectedCategoryTag.value) {
      const categories = await store.getCategories();
      const target = categories.find(c => c.name === selectedCategoryTag.value);
      if (target) {
        params.category = target.id;
      } else {
        store.trips = []; 
        store.totalCount = 0;
        isLoading.value = false;
        return;
      }
    }

    // 거리순 정렬
    if (!params.ordering || (params.ordering === 'distance' && !userLocation.value)) {
         params.ordering = '-created_at';
    }
    if (params.ordering === 'distance' && userLocation.value) {
      params.lat = userLocation.value.lat;
      params.lon = userLocation.value.lon;
    }

    await store.getTrips(params);

  } catch (e) {
    console.error(e);
    store.trips = [];
    store.totalCount = 0;
  } finally {
    isLoading.value = false;
  }
};

const selectTag = (tag) => {
  if (selectedTag.value === tag) return;
  selectedTag.value = tag;
  selectedSubTag.value = '전체';
  currentPage.value = 1;
  loadData(1);
};

const selectSubTag = (subTag) => {
  if (selectedSubTag.value === subTag) return;
  selectedSubTag.value = subTag;
  currentPage.value = 1;
  loadData(1);
}

const selectCategoryTag = (tagName) => {
  if (selectedCategoryTag.value === tagName) {
    selectedCategoryTag.value = null;
  } else {
    selectedCategoryTag.value = tagName;
  }
  
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

const resetFilters = () => {
  selectedTag.value = '전체';
  selectedSubTag.value = null;
  selectedCategoryTag.value = null;
  currentPage.value = 1;
  loadData(1);
}

const goDetail = (id) => {
  router.push({ name: 'trip-detail', params: { id } })
}

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

.sub-tag-box {
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 15px;
  margin-top: 15px;
  
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.sub-tag-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  padding: 6px 0;
  transition: all 0.2s;
}

.sub-tag-btn:hover {
  background-color: #e0e0e0;
  color: #555;
  font-weight: 600;
}

.sub-tag-btn.active {
  color: white;
  font-weight: 600;
  background-color: #333;
  border-radius: 20px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.4s ease;
  overflow: hidden;
  max-height: 500px;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  padding-top: 0;    
  padding-bottom: 0;
}
</style>