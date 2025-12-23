<template>
  <div class="festival-container">
    
    <div class="festival-header">
      <h1 class="title"># 축제지 검색</h1>
      
      <div class="filter-box">
        <select v-model="selectedCity" @change="handleCityChange" class="custom-select">
          <option value="">시/도 선택</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>

        <select v-model="selectedDistrict" @change="handleDistrictChange" class="custom-select" :disabled="!selectedCity">
          <option value="">군/구 선택</option>
          <option v-for="dist in districtList" :key="dist" :value="dist">
            {{ dist }}
          </option>
        </select>
      </div>
    </div>

    <div class="festival-content">
      <div v-if="isLoading" class="msg">로딩 중...</div>
      
      <div v-else-if="store.trips.length === 0" class="msg">
        조건에 맞는 축제 정보가 없습니다.
      </div>

      <div v-else>
        <div class="festival-grid">
          <div 
            v-for="trip in store.trips" 
            :key="trip.id" 
            class="festival-card"
            @click="goDetail(trip.id)"
          >
            <div class="card-thumb">
              <img :src="trip.thumbnail_image || '/src/assets/no_image.png'" :alt="trip.title" />
            </div>
            <div class="card-body">
              <h3 class="card-title">{{ trip.title }}</h3>
              <p class="card-date" v-if="trip.start_date && trip.end_date">
                {{ trip.start_date }} ~ {{ trip.end_date }}
              </p> 
              <p class="card-loc">{{ trip.region_name }} {{ trip.city_name }}</p>
            </div>
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
    </div>

  </div>
</template>

<script setup>
import { useTripStore } from '@/stores/trips';
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router'

const router = useRouter()

const store = useTripStore();
const isLoading = ref(false);

const selectedCity = ref('');
const selectedDistrict = ref('');

const currentPage = ref(1);

const fetchFestivals = async () => {
  isLoading.value = true;
  try {
    const categories = await store.getCategories();
    const target = categories.find(c => c.name === '축제/공연' || c.name === '축제');
    
    if (!target) {
      console.error("'축제/공연' 카테고리를 찾을 수 없습니다.");
      return;
    }

    const params = {
      category: target.id,
      page: currentPage.value,
      ordering: '-created_at'
    };

    if (selectedDistrict.value) {
      params.area = selectedDistrict.value;
    } else if (selectedCity.value) {
      params.area = selectedCity.value;
    }

    await store.getTrips(params);

  } catch (e) {
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

const totalPages = computed(() => Math.ceil(store.totalCount / 10));

const visiblePages = computed(() => {
  const pageLimit = 5;
  const currentGroup = Math.ceil(currentPage.value / pageLimit);
  const start = (currentGroup - 1) * pageLimit + 1;
  const end = Math.min(start + pageLimit - 1, totalPages.value);
  const pages = [];
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchFestivals();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

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

const cities = Object.keys(subRegionData);

const districtList = computed(() => {
  return selectedCity.value ? subRegionData[selectedCity.value] : [];
});

const handleCityChange = () => {
  selectedDistrict.value = '';
  currentPage.value = 1;
  fetchFestivals();
};

const handleDistrictChange = () => {
  currentPage.value = 1;
  fetchFestivals();
};

const goDetail = (id) => {
  router.push({ name: 'trip-detail', params: { id } })
}

onMounted(() => {
  fetchFestivals();
});
</script>

<style scoped>
.festival-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.festival-header {
  margin-bottom: 40px;
}

.title {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 20px;
  color: #333;
}

.filter-box {
  display: flex;
  gap: 10px;
}

.custom-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  min-width: 120px;
  outline: none;
  cursor: pointer;
}

.custom-select:focus {
  border-color: #333;
}

.festival-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); 
  gap: 30px;
}

.festival-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s;
}

.festival-card:hover {
  transform: translateY(-5px);
}

.card-thumb {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
  background-color: #f0f0f0;
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-body {
  padding: 0 4px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
  line-height: 1.3;
  color: #333;
  
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-date {
  font-size: 13px;
  color: #888;
  margin: 0 0 4px 0;
}

.card-loc {
  font-size: 13px;
  color: #888;
  margin: 0;
}

.msg {
  text-align: center;
  padding: 80px 0;
  color: #888;
  font-size: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 50px;
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