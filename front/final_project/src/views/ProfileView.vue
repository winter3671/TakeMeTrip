<template>
  <div class="profile-container">
    
    <div class="profile-header">
      <div class="profile-avatar">
        <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" fill="#7B9DFF" viewBox="0 0 16 16">
          <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0"/>
          <path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1"/>
        </svg>
      </div>
      <div class="profile-info">
        <h2 class="username">{{ accountStore.user?.username || 'Guest' }}</h2>
        <p class="email">{{ accountStore.user?.email || '이메일 정보 없음' }}</p>
      </div>
    </div>

    <div class="profile-tabs">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'articles' }"
        @click="activeTab = 'articles'"
      >
        내가 쓴 글
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'comments' }"
        @click="activeTab = 'comments'"
      >
        내가 쓴 댓글
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'wishlist' }"
        @click="activeTab = 'wishlist'"
      >
        찜한 여행지 ❤️
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'courses' }"
        @click="activeTab = 'courses'"
      >
        내 여행 경로 🗺️
      </button>
    </div>

    <div class="tab-content">
      
      <div v-if="activeTab === 'articles'" class="content-section">
        <div v-if="myArticles.length === 0" class="no-data">작성한 게시글이 없습니다.</div>
        <ul v-else class="list-group">
          <li v-for="article in myArticles" :key="article.id" class="list-item" @click="goToArticle(article.id)">
            <div class="item-main">
              <span class="item-title">{{ article.title }}</span>
              <span class="item-date">{{ formatDate(article.created_at) }}</span>
            </div>
            <div class="item-meta">
              <span>조회 {{ article.hits }}</span>
              <span>좋아요 {{ article.like_count }}</span>
            </div>
          </li>
        </ul>
      </div>

      <div v-if="activeTab === 'comments'" class="content-section">
        <div v-if="myComments.length === 0" class="no-data">작성한 댓글이 없습니다.</div>
        <ul v-else class="list-group">
          <li v-for="comment in myComments" :key="comment.id" class="list-item" @click="goToArticle(comment.article)">
            <div class="item-main">
              <span class="item-text">{{ comment.content }}</span>
              <span class="item-date">{{ formatDate(comment.created_at) }}</span>
            </div>
            <div class="item-sub">
              게시글 보러가기 &gt;
            </div>
          </li>
        </ul>
      </div>

      <div v-if="activeTab === 'wishlist'" class="content-section">
        <div v-if="myWishlist.length === 0" class="no-data">
          찜한 여행지가 없습니다. <br> 마음에 드는 곳에 하트(❤️)를 눌러보세요!
        </div>
        <div v-else>
          <div class="card-grid">
            <div 
              v-for="trip in paginatedWishlist" 
              :key="trip.id" 
              class="card-item"
            >
              <img :src="trip.thumbnail_image || noImage" alt="여행지" class="card-img" />
              <button 
                class="heart-btn active" 
                @click.stop="handleToggleLike(trip)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#FF6B6B" viewBox="0 0 16 16">
                  <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
                </svg>
              </button>
              <div class="card-overlay" @click="goToTripDetail(trip.id)">
                <h3 class="card-title">{{ trip.title }}</h3>
                <p class="card-location">{{ trip.region_name }} {{ trip.city_name }}</p>
              </div>
            </div>
          </div>
          <div class="pagination" v-if="totalPages > 1">
            <button class="page-btn" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">&lt;</button>
            <button v-for="page in totalPages" :key="page" class="page-btn" :class="{ active: currentPage === page }" @click="changePage(page)">{{ page }}</button>
            <button class="page-btn" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">&gt;</button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'courses'" class="content-section">
        <div v-if="!myCourses || myCourses.length === 0" class="no-data">
          저장된 여행 경로가 없습니다. <br> AI 플래너로 나만의 여행을 만들어보세요!
        </div>
        <ul v-else class="list-group">
          <li 
            v-for="course in myCourses" 
            :key="course.id" 
            class="list-item course-item" 
            @click="goToCourseDetail(course.id)"
          >
            <div class="item-main">
              <span class="course-title">🗺️ {{ course.title || '제목 없음' }}</span>
              <span class="item-date">
                생성일: {{ course.created_at ? formatDate(course.created_at) : '-' }}
              </span>
            </div>
            <div class="item-sub">
              <span>{{ course.details ? course.details.length : 0 }}개의 장소</span>
              <span>상세보기 &gt;</span>
            </div>
          </li>
        </ul>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAccountStore } from '@/stores/accounts';
import { useCommunityStore } from '@/stores/community';
import { useTripStore } from '@/stores/trips';
import noImage from '@/assets/no_image.png';

const router = useRouter();
const accountStore = useAccountStore();
const communityStore = useCommunityStore();
const tripStore = useTripStore();

const activeTab = ref('articles');
const myArticles = ref([]);
const myComments = ref([]);
const myWishlist = ref([]);
const myCourses = ref([]);

const currentPage = ref(1);
const itemsPerPage = 10;

const totalPages = computed(() => Math.ceil(myWishlist.value.length / itemsPerPage));

const paginatedWishlist = computed(() => {
  if (!myWishlist.value || myWishlist.value.length === 0) {
    return [];
  }
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return myWishlist.value.slice(start, end).filter(trip => trip && trip.id);
});

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    window.scrollTo(0, 0);
  }
};

const handleToggleLike = async (trip) => {
  if (!confirm(`'${trip.title}' 찜을 취소하시겠습니까?`)) return;
  
  const newStatus = await tripStore.toggleLike(trip.id);
  
  if (newStatus === false) {
    myWishlist.value = myWishlist.value.filter(t => t.id !== trip.id);
    if (paginatedWishlist.value.length === 0 && currentPage.value > 1) {
      currentPage.value--;
    }
  }
};

const fetchData = async () => {
  if (!accountStore.isLogin) {
    alert("로그인이 필요합니다.");
    router.push({ name: 'login' });
    return;
  }

  // 1. 내 글
  try {
    const params = { condition: 'author', search: accountStore.user.username };
    await communityStore.getArticles(params);
    myArticles.value = communityStore.articles || [];
  } catch (e) { 
    console.error("내 글 로드 실패", e); 
    myArticles.value = [];
  }

  // 2. 찜 목록
  try {
    const wishes = await tripStore.getMyWishlist();
    myWishlist.value = Array.isArray(wishes) ? wishes.filter(w => w && w.id) : [];
  } catch (e) { 
    console.error("찜 목록 로드 실패", e); 
    myWishlist.value = [];
  }

  // 3. 내 댓글
  try {
    const comments = await communityStore.getMyComments();
    myComments.value = Array.isArray(comments) ? comments : [];
  } catch (e) { 
    console.error("내 댓글 로드 실패", e); 
    myComments.value = [];
  }

  // 4. 내 여행 경로
  try {
    const courses = await tripStore.getMyCourses();
    myCourses.value = Array.isArray(courses) ? courses.filter(c => c && c.id) : [];
    
    if (myCourses.value.length > 0) {
    }
  } catch (e) { 
    console.error("코스 목록 로드 실패", e); 
    myCourses.value = [];
  }
};

onMounted(async () => {
  if (!accountStore.isLogin) {
    alert("로그인이 필요합니다.");
    router.push({ name: 'login' });
    return;
  }
  
  if (accountStore.token) {
    await accountStore.getUserInfo();
  }
  
  await fetchData();
});

const goToArticle = (id) => router.push({ name: 'article-detail', params: { id } });
const goToTripDetail = (id) => router.push({ name: 'detail', params: { id } });

const goToCourseDetail = (id) => {
  if (!id) {
    console.error('잘못된 코스 ID:', id);
    alert('코스 정보를 찾을 수 없습니다.');
    return;
  }
  
  alert(`코스 ID ${id}의 상세 페이지로 이동합니다.\n(상세 페이지는 아직 구현 전입니다.)`);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ko-KR');
};
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
  min-height: 80vh;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #f0f4ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-info .username {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0 0 5px 0;
}

.profile-info .email {
  font-size: 14px;
  color: #888;
  margin: 0;
}

.profile-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  font-size: 16px;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background-color: #f8f9fa;
  color: #555;
}

.tab-btn.active {
  background-color: #333;
  color: white;
}

.content-section {
  min-height: 300px;
}

.no-data {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 15px;
  background-color: #f9f9f9;
  border-radius: 12px;
}

.list-group {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}

.list-item:first-child {
  border-top: 1px solid #eee;
}

.list-item:hover {
  background-color: #f8f9fa;
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.item-text {
  font-size: 15px;
  color: #555;
}

.item-date {
  font-size: 12px;
  color: #999;
}

.item-meta, .item-sub {
  font-size: 13px;
  color: #888;
  display: flex;
  gap: 10px;
}

.course-title { 
  font-size: 16px; 
  font-weight: 700; 
  color: #2c3e50; 
}

.course-item:hover { 
  background-color: #f0f8ff; 
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.card-item {
  position: relative;
  height: 300px;
  border-radius: 12px;
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
  z-index: 10;
}

.card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 20px 15px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: white;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-location {
  font-size: 13px;
  opacity: 0.9;
  margin: 0;
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

@media (max-width: 1024px) {
  .card-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-tabs {
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style>