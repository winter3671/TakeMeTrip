<template>
  <div>
    <nav class="navbar">
      <div class="container-fluid">
        <RouterLink :to="{ name: 'home' }" class="navbar-brand">
          <img class="logo-image" src="/logo.png" alt="TakeMeTrip">
        </RouterLink>
        
        <div class="search-wrapper">
          <input 
            type="text" 
            class="search-input" 
            placeholder="검색어를 입력하세요."
            v-model="keyword" 
            @keyup.enter="onSearch"
          >
          <button class="search-btn" @click="onSearch">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>
            </svg>
          </button>
        </div>
        
        <div class="desktop-menu">
          <div class="nav-menu">
            <RouterLink :to="{ name: 'home' }" class="nav-link"><span>홈</span></RouterLink>
            <RouterLink :to="{ name: 'information' }" class="nav-link"><span>여행정보</span></RouterLink>
            <RouterLink :to="{ name: 'location' }" class="nav-link"><span>여행지역</span></RouterLink>
            
            <a href="#" @click.prevent="goPlanner" class="nav-link" :class="{ 'router-link-active': $route.name === 'planner' }">
              <span>스마트플래너</span>
            </a>

            <RouterLink :to="{ name: 'community' }" class="nav-link"><span>커뮤니티</span></RouterLink>
          </div>
          
          <div class="icon-menu">
            <button @click="gotoMap" class="icon-btn" title="지도">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M15.817.113A.5.5 0 0 1 16 .5v14a.5.5 0 0 1-.402.49l-5 1a.5.5 0 0 1-.196 0L5.5 15.01l-4.902.98A.5.5 0 0 1 0 15.5v-14a.5.5 0 0 1 .402-.49l5-1a.5.5 0 0 1 .196 0L10.5.99l4.902-.98a.5.5 0 0 1 .415.103M10 1.91l-4-.8v12.98l4 .8zm1 12.98 4-.8V1.11l-4 .8zm-6-.8V1.11l-4 .8v12.98z"/>
              </svg>
            </button>

            <div class="profile-container">
              <button @click="handleProfileClick" class="icon-btn" title="프로필">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/>
                </svg>
              </button>
              <div v-if="showProfileMenu && store.isLogin" class="toggle-menu desktop-pos">
                <button class="menu-item" @click="goToMyPage">마이페이지</button>
                <button class="menu-item logout" @click="handleLogout">로그아웃</button>
              </div>
            </div>

            <button @click="gotoGame" class="icon-btn" title="게임">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                <path d="M10 2a2 2 0 0 1-1.5 1.937v5.087c.863.083 1.5.377 1.5.726 0 .414-.895.75-2 .75s-2-.336-2-.75c0-.35.637-.643 1.5-.726V3.937A2 2 0 1 1 10 2z"/>
                <path d="M0 9.665v1.717a1 1 0 0 0 .553.894l6.553 3.277a2 2 0 0 0 1.788 0l6.553-3.277a1 1 0 0 0 .553-.894V9.665c0-.1-.06-.19-.152-.23L9.5 6.715v.993l5.227 2.178a.125.125 0 0 1 .001.23l-5.94 2.546a2 2 0 0 1-1.576 0l-5.94-2.546a.125.125 0 0 1 .001-.23L6.5 7.708l-.013-.988L.152 9.435a.25.25 0 0 0-.152.23z"/>
              </svg>
            </button>       
          </div>
        </div>

        <button class="hamburger-btn" @click="toggleMenu">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"/>
          </svg>
        </button>
      </div>

      <div class="mobile-menu" :class="{ active: isMenuOpen }">
        <div class="mobile-menu-content">
          <RouterLink :to="{ name: 'home' }" class="mobile-nav-link" @click="closeMenu">홈</RouterLink>
          <RouterLink :to="{ name: 'information' }" class="mobile-nav-link" @click="closeMenu">여행정보</RouterLink>
          <RouterLink :to="{ name: 'location' }" class="mobile-nav-link" @click="closeMenu">여행지역</RouterLink>
          
          <a href="#" @click.prevent="goPlanner" class="mobile-nav-link">스마트플래너</a>

          <RouterLink :to="{ name: 'community' }" class="mobile-nav-link" @click="closeMenu">커뮤니티</RouterLink>
          
          <div class="mobile-icon-menu">
            <button class="mobile-icon-btn" @click="gotoMap">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M15.817.113A.5.5 0 0 1 16 .5v14a.5.5 0 0 1-.402.49l-5 1a.5.5 0 0 1-.196 0L5.5 15.01l-4.902.98A.5.5 0 0 1 0 15.5v-14a.5.5 0 0 1 .402-.49l5-1a.5.5 0 0 1 .196 0L10.5.99l4.902-.98a.5.5 0 0 1 .415.103M10 1.91l-4-.8v12.98l4 .8zm1 12.98 4-.8V1.11l-4 .8zm-6-.8V1.11l-4 .8v12.98z"/>
              </svg>
              <span>지도</span>
            </button>
            
            <div class="profile-container">
              <button class="mobile-icon-btn" @click="handleProfileClick">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/>
                </svg>
                <span>{{ store.isLogin ? '내정보' : '프로필' }}</span>
              </button>

              <div v-if="showProfileMenu && store.isLogin" class="toggle-menu mobile-pos">
                <button class="menu-item" @click="goToMyPage">마이페이지</button>
                <button class="menu-item logout" @click="handleLogout">로그아웃</button>
              </div>
            </div>
              <button @click="gotoGame" class="icon-btn" title="게임">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M10 2a2 2 0 0 1-1.5 1.937v5.087c.863.083 1.5.377 1.5.726 0 .414-.895.75-2 .75s-2-.336-2-.75c0-.35.637-.643 1.5-.726V3.937A2 2 0 1 1 10 2z"/>
                  <path d="M0 9.665v1.717a1 1 0 0 0 .553.894l6.553 3.277a2 2 0 0 0 1.788 0l6.553-3.277a1 1 0 0 0 .553-.894V9.665c0-.1-.06-.19-.152-.23L9.5 6.715v.993l5.227 2.178a.125.125 0 0 1 .001.23l-5.94 2.546a2 2 0 0 1-1.576 0l-5.94-2.546a.125.125 0 0 1 .001-.23L6.5 7.708l-.013-.988L.152 9.435a.25.25 0 0 0-.152.23z"/>
                </svg>
              </button>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/accounts' 

const keyword = ref('')

const store = useAccountStore()
const router = useRouter()

const onSearch = () => {
  if (!keyword.value.trim()) {
    alert('검색어를 입력해주세요!')
    return
  }
  
  router.push({ 
    name: 'search', 
    query: { search: keyword.value } 
  })
}

const isMenuOpen = ref(false)
const showProfileMenu = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
  showProfileMenu.value = false
}

const gotoMap = () => {
  router.push({ name: 'map' })
  closeMenu()
}
const gotoGame = () => {
  router.push({ name: 'game'})
  closeMenu()
}

const goPlanner = () => {
  if (!store.isLogin) {
    alert('로그인이 필요합니다.')
    router.push({ name: 'login' })
  } else {
    router.push({ name: 'planner' })
  }
  closeMenu()
}

const handleProfileClick = () => {
  if (store.isLogin) {
    showProfileMenu.value = !showProfileMenu.value
  } else {
    router.push({ name: 'login' })
    closeMenu()
  }
}

const goToMyPage = () => {
  showProfileMenu.value = false
  closeMenu()
  router.push({ name: 'profile' }) 
}

const handleLogout = () => {
  showProfileMenu.value = false
  closeMenu()
  store.logOut()
}
</script>

<style scoped>
.navbar {
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.75rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.container-fluid {
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: nowrap;
}

.navbar-brand {
  text-decoration: none;
  display: inline-block;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.navbar-brand:hover {
  transform: scale(1.05);
}

.logo-image {
  width: 180px;
  height: auto;
  max-height: 50px;
  display: block;
  object-fit: contain;
}

.search-wrapper {
  position: relative;
  width: 350px;
  flex-shrink: 1;
  min-width: 200px;
  margin-right: auto;
}

.search-input {
  width: 100%;
  padding: 0.7rem 3rem 0.7rem 1.2rem;
  border: 2px solid #e5e7eb;
  border-radius: 25px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-btn {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 50%;
  background: white;
  color: black;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover {
  background: #f3f4f6;
}

.search-btn:active {
  transform: translateY(-50%) scale(0.95);
}

.desktop-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.nav-link {
  text-decoration: none;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s;
  white-space: nowrap;
  position: relative;
}

.nav-link:hover {
  color: #3b82f6;
}

.nav-link.router-link-active {
  color: #3b82f6;
  font-weight: 600;
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -0.75rem;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}

.icon-menu {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.icon-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.icon-btn:hover {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.hamburger-btn {
  display: none;
  background: none;
  border: none;
  color: #374151;
  cursor: pointer;
  padding: 0.5rem;
  margin-left: auto;
  flex-shrink: 0;
}

.hamburger-btn:hover {
  background: #f3f4f6;
  border-radius: 8px;
}

.mobile-menu {
  display: none;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.mobile-menu.active {
  max-height: 500px;
}

.mobile-menu-content {
  padding: 1rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mobile-nav-link {
  text-decoration: none;
  color: #374151;
  font-size: 1rem;
  font-weight: 500;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
  transition: color 0.2s;
}

.mobile-nav-link:hover {
  color: #3b82f6;
}

.mobile-nav-link.router-link-active {
  color: #3b82f6;
  font-weight: 600;
}

.mobile-icon-menu {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.mobile-icon-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.mobile-icon-btn:hover {
  background: #f9fafb;
  border-color: #3b82f6;
  color: #3b82f6;
}

.profile-container {
  position: relative;
  display: inline-block;
}

.toggle-menu {
  position: absolute;
  width: 120px;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.toggle-menu.desktop-pos {
  top: 120%; 
  left: 50%;
  transform: translateX(-50%);
}

.toggle-menu.mobile-pos {
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
}

.menu-item {
  padding: 12px 0;
  border: none;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f0f0f0;
  width: 100%;
  text-align: center;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background-color: #f9f9f9;
}

.menu-item.logout {
  color: #e74c3c;
}

@media (max-width: 1024px) {
  .desktop-menu {
    display: none;
  }

  .hamburger-btn {
    display: block;
  }

  .mobile-menu {
    display: block;
  }

  .search-wrapper {
    width: 300px;
    margin-right: 0;
  }
}

@media (max-width: 768px) {
  .search-wrapper {
    width: 250px;
  }

  .logo-image {
    width: 150px;
  }
}

@media (max-width: 576px) {
  .container-fluid {
    padding: 0 1rem;
  }

  .search-wrapper {
    width: 200px;
  }

  .logo-image {
    width: 120px;
  }
}
</style>