<template>
  <div class="game-container">
    <h1 class="game-title">🎯 운명의 다트 던지기</h1>
    <p class="game-desc">어디로 떠날지 모르겠다면? 다트를 던져보세요!</p>

    <div class="board-area">
      <div class="map-container">
        <img 
          src="@/assets/korea_map.png" 
          alt="대한민국 지도" 
          class="korea-map"
        />

        <div 
          v-if="hitPosition" 
          class="hit-marker" 
          :style="hitPosition"
        ></div>

        <div 
          class="dart" 
          :class="{ 'flying': isFlying }"
          :style="dartStyle"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" style="filter: drop-shadow(2px 5px 3px rgba(0,0,0,0.4));">
            <path fill="#333" d="M12,2 L14,16 L10,16 Z"/>
            <path fill="#C0C0C0" d="M11,16 L13,16 L12,22 Z"/>
            <path fill="#FF4500" d="M12,2 L16,6 L12,7 L8,6 Z"/>
          </svg>
        </div>
      </div>

      <div v-if="showResult" class="result-card">
        <h3>🎉 당첨! 떠나볼까요?</h3>
        <div class="result-content">
          <span class="result-region">{{ selectedRegion.name }}</span>
        </div>
        <p class="result-desc">{{ selectedRegion.desc }}</p>
        <div class="btn-group">
          <button @click="resetGame" class="retry-btn">다시 하기</button>
          <button @click="goToRecommend" class="go-btn">추천 장소 보기</button>
        </div>
      </div>
    </div>

    <div class="control-area">
      <button 
        class="throw-btn" 
        @click="throwDart" 
        :disabled="isFlying || showResult"
      >
        <span v-if="!isFlying">다트 던지기! 🚀</span>
        <span v-else>날아가는 중... 💨</span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const isFlying = ref(false);
const showResult = ref(false);
const selectedRegion = ref(null);
const hitPosition = ref(null);

const initialPos = { top: '85%', left: '50%', transform: 'translate(-50%, -100%) scale(1.2)' };
const dartPos = ref({ ...initialPos });

const dartStyle = computed(() => ({
  top: dartPos.value.top,
  left: dartPos.value.left,
  transform: dartPos.value.transform,
  width: '32px',
  height: '32px'
}));

const regions = [
  { id: 1, name: '서울', desc: '대한민국의 심장, 역사와 현대의 공존', top: '28%', left: '34%' },
  { id: 2, name: '부산', desc: '해운대, 광안리! 열정의 항구 도시', top: '72%', left: '75%' },
  { id: 3, name: '강릉', desc: '푸른 동해 바다와 향긋한 커피 거리', top: '27%', left: '72%' },
  { id: 4, name: '제주', desc: '천혜의 자연, 환상의 섬', top: '83%', left: '85%' },
  { id: 5, name: '경주', desc: '도시 전체가 박물관, 천년 고도', top: '63%', left: '80%' },
  { id: 6, name: '전주', desc: '맛과 멋의 고장, 한옥마을 먹방 투어', top: '58%', left: '32%' },
  { id: 7, name: '여수', desc: '낭만 가득 여수 밤바다~', top: '78%', left: '42%' },
  { id: 8, name: '대전', desc: '국토의 중심, 과학과 성심당의 도시', top: '50%', left: '40%' },
  { id: 9, name: '춘천', desc: '호반의 도시, 닭갈비와 막국수', top: '22%', left: '50%' },
  { id: 10, name: '안동', desc: '한국 정신문화의 수도, 하회마을', top: '46%', left: '70%' },
  { id: 11, name: '광주', desc: '빛고을, 문화예술과 맛의 중심지', top: '70%', left: '25%' },
];

const throwDart = () => {
  if (isFlying.value) return;

  const randomIndex = Math.floor(Math.random() * regions.length);
  const target = regions[randomIndex];
  selectedRegion.value = target;

  isFlying.value = true;
  showResult.value = false;
  hitPosition.value = null; 

  // 1. 다트 출발
  setTimeout(() => {
    dartPos.value = {
      top: target.top,
      left: target.left,
      transform: 'translate(-50%, -100%) scale(1)' 
    };
  }, 50);

  // 2. 다트 도착 (0.8초 후)
  setTimeout(() => {
    // 쾅! 파동 효과 표시
    hitPosition.value = { top: target.top, left: target.left };
    isFlying.value = false;

    setTimeout(() => {
      showResult.value = true;
    }, 700); 

  }, 800);
};

const resetGame = () => {
  showResult.value = false;
  selectedRegion.value = null;
  hitPosition.value = null;
  dartPos.value = { ...initialPos };
};

const goToRecommend = () => {
  router.push({ 
    name : 'location',
    query: { category: selectedRegion.value.name }
  })
};
</script>

<style scoped>
.game-container { 
  max-width: 600px; 
  margin: 100px auto; 
  text-align: center; 
  font-family: 'Noto Sans KR', sans-serif; 
  padding: 0 20px; 
}

.game-title { 
  font-size: 2rem; 
  font-weight: 800; 
  color: #333; 
  margin-bottom: 5px; 
}

.game-desc { 
  color: #666; 
  margin-bottom: 30px; 
}

.board-area {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  border-radius: 20px;
  border: 4px solid #7B9DFF;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.map-container {
  position: relative;
  width: 100%;
  padding-bottom: 145%; 
}

.korea-map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.hit-marker {
  position: absolute;
  width: 20px;
  height: 20px;
  background-color: rgba(255, 69, 0, 0.6);
  border-radius: 50%;
  transform: translate(-50%, -100%);
  z-index: 5;
  animation: ripple 1.5s infinite;
}

@keyframes ripple {
  0% { box-shadow: 0 0 0 0 rgba(255, 69, 0, 0.7); }
  70% { box-shadow: 0 0 0 20px rgba(255, 69, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 69, 0, 0); }
}

.dart {
  position: absolute;
  z-index: 10;
  transition: all 0.8s ease-out;
  pointer-events: none;
}

.dart.flying svg {
  filter: drop-shadow(5px 10px 5px rgba(0,0,0,0.2));
}

.result-card { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(255, 255, 255, 0.95); padding: 25px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); width: 80%; z-index: 20; animation: popIn 0.3s ease-out; text-align: center; }
@keyframes popIn { from { transform: translate(-50%, -50%) scale(0.8); opacity: 0; } to { transform: translate(-50%, -50%) scale(1); opacity: 1; } }
.result-content { margin: 15px 0; }
.result-region { font-size: 2rem; font-weight: 800; color: #7B9DFF; display: block; }
.result-desc { color: #555; margin-bottom: 20px; font-size: 14px; }
.btn-group { display: flex; gap: 10px; justify-content: center; }
.retry-btn { background: #f1f3f5; color: #333; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.go-btn { background: #7B9DFF; color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: 600; }
.control-area { margin-top: 30px; margin-bottom: 50px; }
.throw-btn { background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white; border: none; padding: 15px 40px; font-size: 1.2rem; font-weight: 800; border-radius: 50px; cursor: pointer; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4); transition: transform 0.1s, box-shadow 0.1s; }
.throw-btn:active { transform: scale(0.95); }
.throw-btn:disabled { background: #ccc; cursor: not-allowed; box-shadow: none; }
</style>