# ✈️ TakeMeTrip (TMT) - 알고리즘 기반 맞춤형 여행 코스 플래너 & 커뮤니티

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=flat&logo=vue.js&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pinia-3.0-FFD11B?style=flat&logo=pinia&logoColor=black"/>
  <img src="https://img.shields.io/badge/Vite-7.3-646CFF?style=flat&logo=vite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Kakao_Map-FFCD00?style=flat&logo=kakao&logoColor=black"/>
</div>

<br/>

**TakeMeTrip**은 사용자의 위시리스트 데이터와 여행지 인기도를 분석하여 **자체 알고리즘이 최적의 여행 코스를 자동으로 생성**해주고, 이를 커뮤니티에 공유하여 여행의 경험을 확장하는 **올인원 여행 플랫폼**입니다.

단순한 랜덤 추천이 아닌, **거리 기반 최단 경로 알고리즘(TSP 근사)**과 **사용자 선호도 가중치 시스템**을 적용하여 실제 여행 가능한 동선을 제공하며, **소셜 로그인**과 **반응형 UI**로 사용자 편의성을 극대화했습니다.

---

## 📅 프로젝트 개요
* **프로젝트명**: TakeMeTrip (TMT)
* **개발 기간**: 2025.12.19 ~ 2025.12.25
* **핵심 가치**: 사용자 주도적 데이터(Wishlist)를 활용한 **초개인화 여행 경험 제공**

---

## 🛠️ 기술 스택 (Tech Stack)

### Backend
* **Framework**: Django REST Framework (DRF)
* **Language**: Python 3.11
* **Database**: SQLite (Development)
* **Auth**: dj-rest-auth, simple-jwt (JWT Cookie Auth), django-allauth (Social Login)
* **Data Collection**: Public Data Portal (TourAPI 4.0), `requests`, `python-decouple`
* **Algorithm**: Custom Heuristic Algorithm (Weighted Scoring + Nearest Neighbor)

### Frontend
* **Framework**: Vue 3 (Composition API)
* **Build Tool**: Vite 7.3
* **State Management**: Pinia (+ pinia-plugin-persistedstate)
* **Routing**: Vue Router
* **Networking**: Axios
* **Styling**: Custom CSS (Responsive Design), Bootstrap 5
* **Map**: Kakao Map API

### Collaboration & Tools
* **Version Control**: Git, GitLab
* **Communication**: Notion, Mattermost, Discord
* **Design**: Figma

---

## ✨ 핵심 기능 (Key Features)

### 1. 📍 스마트 코스 플래너 (Smart Planner)
* **알고리즘 기반 코스 생성**
    * **가중치 시스템**: `기본 점수` + `위시리스트 가중치(150점)` + `인기도(좋아요) 점수` + `랜덤 노이즈`를 합산하여 최적의 장소를 선정합니다.
    * **권역 분리**: 여행 일수에 따라 지역을 권역(Anchor)으로 나누어 일자별 이동 동선을 최적화합니다.
    * **Nearest Neighbor**: 현재 위치에서 가장 가깝고 점수가 높은 장소를 찾아가는 탐욕(Greedy) 알고리즘으로 이동 시간을 최소화합니다.
* **숙소/식당 자동 배정**
    * 여행 경로의 중심점(Centroid)을 계산하여 최적의 위치에 있는 숙소를 추천합니다.
    * 점심/저녁 시간대에 맞춰 동선 상에 있는 맛집을 자동으로 일정에 포함합니다.
* **이동 시간 예측**: 사용자의 현재 위치부터 여행지까지의 거리와 지역 간 이동 시간을 계산하여 타임라인에 표시합니다.

### 2. 🗺️ 관광 데이터 및 추천 시스템 (Trips)
* **방대한 데이터베이스**: 한국관광공사 TourAPI를 연동하여 전국 **수만 개의 관광지, 식당, 숙소 정보**를 구축했습니다.
* **하이브리드 추천**
    * **콘텐츠 기반**: 내가 찜한 장소와 같은 카테고리/지역의 장소를 추천합니다.
    * **소셜 프루프**: 다른 유저들의 좋아요 수가 많은 장소를 가중치에 반영하여 추천 품질을 높였습니다.
* **상세 정보 & 지도**: Kakao Map을 통해 위치를 직관적으로 확인하고, 상세 설명 및 이미지를 제공합니다.

### 3. 📝 여행 커뮤니티 (Community)
* **코스 연동 글쓰기**: 게시글 작성 시, **내가 생성한 여행 코스(Planner 결과)를 원클릭으로 첨부**할 수 있습니다.
* **일정 시각화 UI**: 상세 페이지에서 `Day 1` / `Day 2` 탭으로 구분된 타임라인 카드 UI를 통해 복잡한 일정을 한눈에 보여줍니다.
* **소셜 인터랙션**: 좋아요(Like), 조회수(Hits), 댓글(Comment) 기능을 통해 여행 정보를 활발히 공유합니다.
* **검색 필터**: 제목, 내용, 작성자 등 다양한 조건으로 게시글을 검색할 수 있습니다.

### 4. 🔐 사용자 인증 (Authentication)
* **소셜 로그인**: Kakao, Naver, Google 계정을 연동한 원터치 로그인을 지원합니다. (OAuth2.0)
* **계정 통합**: 이메일이 같을 경우, 소셜 계정과 일반 계정을 자동으로 연동하여 사용자 경험을 개선했습니다.
* **JWT 보안**: Access/Refresh Token 방식을 사용하여 안전한 인증 환경을 구축했습니다.

---

## 📂 프로젝트 구조 (Directory Structure)

```text
TMT/
├── back/
│   ├── community/       # 게시글, 댓글, 좋아요 및 여행 코스 첨부 로직
│   ├── planner/         # 자체 알고리즘 기반 여행 코스 생성 및 저장
│   ├── trips/           # 관광지 데이터 관리, TourAPI 수집 스크립트, 추천 API
│   ├── users/           # 커스텀 유저 모델, 소셜 로그인 어댑터(Adapter)
│   ├── TMT/             # Django 프로젝트 설정 (Settings, JWT, CORS)
│   └── manage.py
└── front/
    └── final_project/
        ├── src/
        │   ├── components/  # KakaoLogin, Navbar 등 재사용 컴포넌트
        │   ├── stores/      # Pinia Stores (accounts, community, trips)
        │   ├── views/       # AIPlannerView, ArticleCreateView, LoginView 등
        │   ├── App.vue      # 메인 레이아웃
        │   └── main.js
        └── vite.config.js
```

---

## 💾 ERD 설계 (Database Design)

* **User - Course**: `1:N` 관계 (한 유저가 여러 개의 여행 코스를 생성 및 저장)
* **Course - Trip**: `N:M` 관계 (하나의 코스는 여러 관광지를 포함하며, CourseDetail 모델이 순서(order)와 일차(day) 정보를 중계)
* **Article - Course**: `N:1` 관계 (게시글 작성 시 Planner에서 만든 Course를 참조)
* **User - Trip**: `N:M` 관계 (Wishlist - 찜하기 기능)
* **Trip - Region/City/Category**: `FK` 관계 (체계적인 관광지 분류)

---

## 🚀 설치 및 실행 방법 (Installation)

### Backend (Django)

```bash
# 1. 이동 및 가상환경 설정
cd back
python -m venv venv
source venv/Scripts/activate  # Windows

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env 파일 생성)
# SECRET_KEY, TOUR_API_KEY, SOCIAL_AUTH_KEYS 등 설정

# 4. 데이터베이스 마이그레이션
python manage.py migrate

# 5. 관광 데이터 수집 (최초 1회)
python manage.py import_tourapi

# 6. 서버 실행
python manage.py runserver
```

### Frontend (Vue 3)

```bash
# 1. 이동 및 패키지 설치
cd front/final_project
npm install

# 2. 환경 변수 설정 (.env)
# VITE_API_URL, VITE_KAKAO_JS_KEY 등 설정

# 3. 개발 서버 실행
npm run dev
```

---

## 🔧 트러블 슈팅 (Troubleshooting)
> 프로젝트 개발 과정에서 발생한 주요 이슈와 해결 과정입니다.

### 1. 추천 알고리즘의 편향성 및 '같은 장소' 추천 문제
* **문제**: 초기 알고리즘이 인기 있는 장소만 반복 추천하거나, 같은 건물(백화점 등) 내의 장소를 중복 추천하는 문제 발생.
* **해결**:
    * `views.py`의 점수 산정 로직에 **Random Noise**를 추가하고 **Top-K Sampling** 방식을 도입하여 다양성 확보.
    * `exclude_id` 로직을 추가하여 현재 보고 있는 장소는 추천 목록에서 제외.
    * 좌표 기반 거리 계산 시 동일 좌표(같은 건물) 내 장소는 허용하되 본인만 제외하도록 정교화.

### 2. 소셜 로그인 인증 흐름 (OAuth2 + JWT)
* **문제**: 프론트엔드(Vite)와 백엔드(Django) 포트가 달라 발생하는 CORS 문제 및 소셜 로그인 콜백(Callback) 처리의 복잡성.
* **해결**:
    * `django-cors-headers` 설정 및 `dj-rest-auth`의 `SocialLoginView`를 상속받은 커스텀 뷰 구현.
    * `allauth`와 `dj-rest-auth` 간의 버전 호환성 문제(scope 인자 오류)를 해결하기 위해 **CustomOAuth2Client**를 직접 구현하여 해결.
    * 프론트엔드에 `SocialCallback.vue`를 두어 인가 코드를 받아 백엔드로 전달하는 표준 OAuth 흐름 완성.

### 3. 게시글과 여행 코스 데이터 연동 (Nested Serializer)
* **문제**: 게시글(Article) 조회 시 연결된 코스(Course)의 ID만 출력되고, 상세 일정(CourseDetail)이 보이지 않음.
* **해결**: 
    * DRF의 `ArticleDetailSerializer` 내부에 `CourseSerializer`를, 그 내부에 `CourseDetailSerializer`를 중첩(Nested)시켜 계층적인 JSON 응답을 구성. 
    * 프론트엔드에서는 이를 `computed` 속성으로 받아 Day별로 그룹화하여 렌더링.

---

## 👨‍💻 개발자 (Contributors)
* **팀장**: 김민재 - FE 메인 구현, 커뮤니티 기능 및 지도 연동
* **팀원**: 박정훈 - BE 아키텍처, 추천 알고리즘 및 플래너 로직 구현