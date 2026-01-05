import requests
import time
from urllib.parse import unquote
from django.core.management.base import BaseCommand
from trips.models import Trip, TripImage, Region, City, Category, Tag, TripTag
from decouple import config
from datetime import datetime

class Command(BaseCommand):
    help = 'Import data from TourAPI'

    # python manage.py import_tourapi --area-code=1 --full

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-code',
            type=str,
            nargs='?', 
            help='Area code (If empty, imports ALL regions)',
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Fetch detailed info (overview, tel, etc.) via additional API calls',
        )

    # 공통 정보 (개요, 홈페이지, 전화번호)
    def get_detail_common(self, content_id, api_key):
        url = "https://apis.data.go.kr/B551011/KorService2/detailCommon2"
        params = {
            "serviceKey": api_key,
            "MobileOS": "ETC",
            "MobileApp": "TMT",
            "_type": "json",
            "contentId": content_id,
        }
        try:
            res = requests.get(url, params=params).json()
            items = res.get("response", {}).get("body", {}).get("items", {})
            
            if not items: return {}
            
            item = items.get("item")
            data = {}
            
            if isinstance(item, list) and len(item) > 0:
                data = item[0]
            elif isinstance(item, dict):
                data = item
                
            return data 
            
        except:
            return {}

    def get_detail_intro(self, content_id, content_type_id, api_key):
        url = "https://apis.data.go.kr/B551011/KorService2/detailIntro2"
        params = {
            "serviceKey": api_key,
            "MobileOS": "ETC",
            "MobileApp": "TMT",
            "_type": "json",
            "contentId": content_id,
            "contentTypeId": content_type_id
        }
        
        try:
            res = requests.get(url, params=params).json()
            items = res.get("response", {}).get("body", {}).get("items", {})
            
            if not items: return {}

            item = items.get("item")
            data = {}
            if isinstance(item, list) and len(item) > 0:
                data = item[0]
            elif isinstance(item, dict):
                data = item
            
            # 전화번호(infocenter) 및 기타 정보 파싱
            infocenter = (
                data.get('infocenter') or 
                data.get('infocenterfood') or 
                data.get('infocenterlodging') or
                data.get('infocentershopping') or
                data.get('infocenterculture') or
                data.get('infocenterleports') or ''
            )

            parking = (
                data.get('parking') or data.get('parkingfood') or 
                data.get('parkinglodging') or data.get('parkingshopping') or 
                data.get('parkingculture') or data.get('parkingleports') or ''
            )
            
            rest_date = (
                data.get('restdate') or data.get('restdatefood') or 
                data.get('restdateshopping') or data.get('restdateculture') or 
                data.get('restdateleports') or ''
            )
            
            use_time = (
                data.get('usetime') or data.get('opentimefood') or 
                data.get('opentime') or data.get('usetimeculture') or 
                data.get('usetimeleports') or ''
            )
            
            return {
                'infocenter': infocenter,
                'parking': parking,
                'rest_date': rest_date,
                'use_time': use_time
            }
        except:
            return {}
        
    def handle(self, *args, **options):
        raw_key = config('TOUR_API_KEY')
        API_KEY = unquote(raw_key)
        BASE_URL = 'https://apis.data.go.kr/B551011/KorService2'
        
        full_mode = options.get('full', False)
        today_str = datetime.now().strftime('%Y%m%d')

        ALL_REGIONS = {
            '1': '서울', '2': '인천', '3': '대전', '4': '대구', '5': '광주', 
            '6': '부산', '7': '울산', '8': '세종', '31': '경기', '32': '강원', 
            '33': '충북', '34': '충남', '35': '경북', '36': '경남', '37': '전북', 
            '38': '전남', '39': '제주'
        }

        input_code = options.get('area_code')
        if input_code:
            target_regions = {input_code: ALL_REGIONS.get(input_code, 'Unknown')}
        else:
            target_regions = ALL_REGIONS

        content_types = {
            '12': '관광지', '14': '문화시설', '15': '축제/공연',
            '28': '레포츠', '32': '숙박', '38': '쇼핑', '39': '음식점'
        }

        self.stdout.write(self.style.SUCCESS(f'Target Regions: {list(target_regions.values())}'))

        for area_code, area_name in target_regions.items():
            self.stdout.write(self.style.WARNING(f'\n\n🚀 Starting Region: {area_name} (Code: {area_code})'))
            
            for c_id, c_name in content_types.items():
                self.stdout.write(f'\n  Category: {c_name} (Code: {c_id})')
                
                page = 1
                total_imported_in_category = 0

                if c_id == '15':
                    endpoint = '/searchFestival2'
                    base_params = {'eventStartDate': today_str, 'arrange': 'A'}
                    self.stdout.write(f'   -> (Mode: Festival Search from {today_str})')
                else:
                    endpoint = '/areaBasedList2'
                    base_params = {'arrange': 'A', 'contentTypeId': c_id}

                while True:
                    params = {
                        'serviceKey': API_KEY,
                        'numOfRows': 100,
                        'pageNo': page,
                        'MobileOS': 'ETC',
                        'MobileApp': 'TripPlanner',
                        'areaCode': area_code,
                        '_type': 'json',
                    }
                    params.update(base_params)
                    
                    # 재시도(Retry)
                    max_retries = 3  # 최대 3번까지 재시도
                    response = None
                    success = False

                    for attempt in range(max_retries):
                        try:
                            response = requests.get(f'{BASE_URL}{endpoint}', params=params, timeout=30)
                            
                            if response.status_code == 200:
                                success = True
                                break 
                            elif response.status_code == 502:
                                # 502 에러면 잠시 쉬었다가 재시도
                                self.stdout.write(self.style.WARNING(f'    ⚠️ 502 Bad Gateway. Retrying... ({attempt+1}/{max_retries})'))
                                time.sleep(3) 
                            else:
                                self.stdout.write(self.style.ERROR(f'API Error: {response.status_code}'))
                                break
                        except requests.exceptions.RequestException as e:
                            self.stdout.write(self.style.WARNING(f'    ⚠️ Connection Error. Retrying... ({attempt+1}/{max_retries})'))
                            time.sleep(3)

                    if not success or response is None or response.status_code != 200:
                        self.stdout.write(self.style.ERROR(f'    ❌ Failed to fetch page {page} after retries. Moving to next category.'))
                        break

                    try:
                        data = response.json()
                        items = []
                        
                        if 'response' in data and 'body' in data['response']:
                            body = data['response']['body']
                            if 'items' in body and body['items']:
                                items = body['items']['item']
                                if not isinstance(items, list):
                                    items = [items]
                            
                            if not items:
                                break 
                        else:
                            break

                        count = 0
                        for item in items:
                            if self.process_item(item, area_code, full_mode):
                                count += 1
                                total_imported_in_category += 1
                        
                        self.stdout.write(f'    - {area_name} | {c_name} | p.{page}: Saved {count} items')
                        
                        if len(items) < 100:
                            break 
                        
                        page += 1
                        time.sleep(0.5)

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error processing data: {str(e)}'))
                        break
                
                self.stdout.write(self.style.SUCCESS(f'  -> Finished {c_name} in {area_name}: {total_imported_in_category} items'))    

    def process_item(self, item, area_code, full_mode=False):
        try:
            content_id = item.get('contentid')
            # [필터링] 필수 데이터 검증: ID, 제목, 그리고 사진(firstimage)이 있어야 함
            if not content_id or not item.get('title') or not item.get('firstimage'):
                return False
            
            # 이미 존재하는지 확인
            existing_trip = Trip.objects.filter(external_id=content_id).first()
            
            region = self.get_or_create_region(item.get('areacode', '1'))
            city = None
            if item.get('sigungucode'):
                city = self.get_or_create_city(item.get('sigungucode'), area_code, region)
            
            content_type_id = item.get('contenttypeid', '12')
            cat3 = item.get('cat3', '')
            category = self.get_or_create_category(content_type_id, cat3)
            
            start_date = self.parse_date(item.get('eventstartdate'))
            end_date = self.parse_date(item.get('eventenddate'))

            api_key = unquote(config('TOUR_API_KEY'))

            common_data = {}
            intro_data = {}

            # [핵심] full_mode가 켜져있고, 상세 정보가 없는 경우에만 API 호출
            if full_mode:
                if not existing_trip or not existing_trip.overview:
                    common_data = self.get_detail_common(content_id, api_key)
                    intro_data = self.get_detail_intro(content_id, content_type_id, api_key)

            # 기본 데이터 매핑 (상세 API 호출 안 할 경우 item 데이터 활용)
            update_defaults = {
                'title': item.get('title', '')[:200],
                'description': item.get('addr1', '')[:1000], # overview 없을 때 대용
                'destination': item.get('addr1', '')[:100],
                'region': region,
                'city': city,
                'category': category,
                'thumbnail_image': item.get('firstimage', ''),
                'price': 0,
                'duration': 1,
                'status': 'active',
                'recommendation_score': self.calculate_score(item),
                'start_date': start_date,
                'end_date': end_date,
                'mapx': float(item.get('mapx', 0.0) or 0.0),
                'mapy': float(item.get('mapy', 0.0) or 0.0),
            }

            # 상세 정보가 있는 경우에만 필드 업데이트
            if common_data.get('overview'):
                update_defaults['overview'] = common_data.get('overview')
            if common_data.get('tel') or intro_data.get('infocenter'):
                update_defaults['tel'] = common_data.get('tel') or intro_data.get('infocenter')
            if common_data.get('homepage'):
                update_defaults['homepage'] = common_data.get('homepage')
            if intro_data.get('parking'):
                update_defaults['parking'] = intro_data.get('parking')
            if intro_data.get('rest_date'):
                update_defaults['rest_date'] = intro_data.get('rest_date')
            if intro_data.get('use_time'):
                update_defaults['use_time'] = intro_data.get('use_time')

            # [추가] 이용시간 규격화 (Normalization) 로직
            use_time_source = intro_data.get('use_time') or (existing_trip.use_time if existing_trip else '')
            ot, ct = self.parse_business_hours(use_time_source)
            if ot: update_defaults['open_time'] = ot
            if ct: update_defaults['close_time'] = ct

            trip, created = Trip.objects.update_or_create(
                external_id=content_id,
                defaults=update_defaults
            )
            
            self.create_tags(trip, item, common_data, intro_data)

            if created or not trip.images.exists():
                self.fetch_images(trip, item['contentid'])
            return True
            
        except Exception as e:
            return False

    def parse_date(self, date_str):
        if not date_str or len(str(date_str)) != 8:
            return None
        try:
            date_str = str(date_str)
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        except:
            return None

    def parse_business_hours(self, time_str):
        """계절별/월별 정보를 인식하여 현재 시점에 가장 적합한 운영 시간 추출"""
        if not time_str:
            return None, None
        
        import re
        from datetime import datetime
        current_month = datetime.now().month

        # <br>이나 공백 등으로 문장을 분리
        segments = re.split(r'<br>|\n|\|', time_str)
        
        season_results = []
        
        for seg in segments:
            # 1. 월 범위 추출 (예: 3월~10월, 11~2월)
            month_match = re.search(r'(\d+)\s*월?\s*[~-]\s*(\d+)\s*월?', seg)
            # 2. 시간 범위 추출 (06:00~18:00 등)
            time_match = re.search(r'(\d{1,2}(?::\d{2}|시))', seg)
            
            if time_match:
                # 해당 라인에서 시간 쌍 추출 (기존 logic 활용)
                ot, ct = self._extract_time_range(seg)
                if not ot: continue
                
                if month_match:
                    start_m, end_m = map(int, month_match.groups())
                    # 월 범위 계산 (예: 11~2월 같은 역전 범위 처리)
                    if start_m <= end_m:
                        in_season = start_m <= current_month <= end_m
                    else: # 11월 ~ 2월인 경우
                        in_season = (current_month >= start_m or current_month <= end_m)
                    
                    if in_season:
                        return ot, ct # 현재 계절에 맞으면 즉시 반환
                    
                season_results.append((ot, ct))

        # 맞는 계절을 못 찾았다면 첫 번째로 발견된 시간 반환
        if season_results:
            return season_results[0]
            
        # 마지막 보루: 전체 텍스트에서 가장 먼저 보이는 시간 쌍이라도 찾기
        return self._extract_time_range(time_str)

    def _extract_time_range(self, text):
        """문자열에서 단일 시간 쌍(HH:MM~HH:MM) 추출 Helper"""
        import re
        # 1. HH:MM 형식
        match_hm = re.search(r'(\d{1,2}:\d{2})\s*[~-]\s*(\d{1,2}:\d{2})', text)
        if match_hm:
            o, c = match_hm.groups()
            return f"{int(o.split(':')[0]):02d}:{o.split(':')[1]}", f"{int(c.split(':')[0]):02d}:{c.split(':')[1]}"
        
        # 2. HH시 형식
        match_si = re.search(r'(\d{1,2})시(?:\s*(\d{1,2})분)?\s*[~-]\s*(\d{1,2})시(?:\s*(\d{1,2})분)?', text)
        if match_si:
            oh, om, ch, cm = match_si.groups()
            return f"{int(oh):02d}:{int(om or 0):02d}", f"{int(ch):02d}:{int(cm or 0):02d}"
        
        return None, None
        
    def create_tags(self, trip, item, common_data, intro_data):
        tags_to_create = set() # 중복 방지를 위해 set 사용

        # 1. 지역/도시 태그
        if trip.region:
            tags_to_create.add(f"#{trip.region.name}")
        if trip.city:
            tags_to_create.add(f"#{trip.city.name}")

        # 2. 카테고리/분류 태그 (cat3 활용)
        cat3 = item.get('cat3', '')
        CAT3_TAGS = {
            'A05020900': ['#카페', '#디저트', '#분위기좋은'],
            'A02010800': ['#전시회', '#문화생활'],
            'A01010100': ['#자연', '#풍경명소'],
            'A02020600': ['#전통시장', '#쇼핑'],
            'A02030100': ['#사찰', '#역사'],
            'A02050100': ['#유원지', '#테마파크'],
        }
        if cat3 in CAT3_TAGS:
            for t in CAT3_TAGS[cat3]: tags_to_create.add(t)

        # 3. 제목 키워드 분석 (대폭 확장)
        title = item.get('title', '')
        keyword_map = {
            '맛집': '#맛집', '카페': '#카페', '전망대': '#야경명소', 
            '공원': '#산책로', '해수욕장': '#바다', '미술관': '#예술', 
            '박물관': '#교육', '캠핑': '#캠핑', '온천': '#힐링',
            '야경': '#야경', '일출': '#일출', '스타필드': '#복합문화공간'
        }
        for kw, tag in keyword_map.items():
            if kw in title:
                tags_to_create.add(tag)

        # 4. 개요 및 상세 정보 시설 분석 (Facility tagging)
        # overview, intro_data(parking) 등에서 키워드 추출
        full_text = f"{item.get('title', '')} {common_data.get('overview', '')} {intro_data.get('parking', '')}"
        
        facility_map = {
            '주차': '#주차가능',
            '반려동물': '#애견동반',
            '애완동물': '#애견동반',
            '유모차': '#아이와함께',
            '무선 인터넷': '#WiFi',
            '와이파이': '#WiFi',
            '포토존': '#인생샷',
            '장애인': '#배리어프리',
        }
        for kw, tag in facility_map.items():
            if kw in full_text:
                tags_to_create.add(tag)

        for tag_name in tags_to_create:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            TripTag.objects.get_or_create(trip=trip, tag=tag)

    def get_or_create_region(self, areacode):
        AREA_MAP = {
            '1': ('서울', 'seoul'), '2': ('인천', 'incheon'), '3': ('대전', 'daejeon'),
            '4': ('대구', 'daegu'), '5': ('광주', 'gwangju'), '6': ('부산', 'busan'),
            '7': ('울산', 'ulsan'), '8': ('세종', 'sejong'), '31': ('경기', 'gyeonggi'),
            '32': ('강원', 'gangwon'), '33': ('충북', 'chungbuk'), '34': ('충남', 'chungnam'),
            '35': ('경북', 'gyeongbuk'), '36': ('경남', 'gyeongnam'), '37': ('전북', 'jeonbuk'),
            '38': ('전남', 'jeonnam'), '39': ('제주', 'jeju'),
        }
        region_info = AREA_MAP.get(str(areacode), ('기타', 'etc'))
        region, _ = Region.objects.get_or_create(
            slug=region_info[1],
            defaults={'name': region_info[0], 'is_active': True}
        )
        return region

    def get_or_create_city(self, sigungucode, area_code, region):
        """시군구 실제 이름 매핑"""

        # 전국 시군구 매핑
        SIGUNGU_MAP = {
            # 서울 (1)
            '1_1': '강남구', '1_2': '강동구', '1_3': '강북구', '1_4': '강서구',
            '1_5': '관악구', '1_6': '광진구', '1_7': '구로구', '1_8': '금천구',
            '1_9': '노원구', '1_10': '도봉구', '1_11': '동대문구', '1_12': '동작구',
            '1_13': '마포구', '1_14': '서대문구', '1_15': '서초구', '1_16': '성동구',
            '1_17': '성북구', '1_18': '송파구', '1_19': '양천구', '1_20': '영등포구',
            '1_21': '용산구', '1_22': '은평구', '1_23': '종로구', '1_24': '중구',
            '1_25': '중랑구', '1_99': '서울 전체',
            
            # 인천 (2)
            '2_1': '강화군', '2_2': '계양구', '2_3': '남동구', '2_4': '동구',
            '2_5': '미추홀구', '2_6': '부평구', '2_7': '서구', '2_8': '연수구',
            '2_9': '옹진군', '2_10': '중구', '2_99': '인천 전체',
            
            # 대전 (3)
            '3_1': '대덕구', '3_2': '동구', '3_3': '서구', '3_4': '유성구', 
            '3_5': '중구', '3_99': '대전 전체',
            
            # 대구 (4)
            '4_1': '남구', '4_2': '달서구', '4_3': '달성군', '4_4': '동구',
            '4_5': '북구', '4_6': '서구', '4_7': '수성구', '4_8': '중구',
            '4_9': '군위군', '4_99': '대구 전체',
            
            # 광주 (5)
            '5_1': '광산구', '5_2': '남구', '5_3': '동구', '5_4': 
            '북구', '5_5': '서구', '5_99': '광주 전체',
            
            # 부산 (6)
            '6_1': '강서구', '6_2': '금정구', '6_3': '남구', '6_4': '동구',
            '6_5': '동래구', '6_6': '부산진구', '6_7': '북구', '6_8': '사상구',
            '6_9': '사하구', '6_10': '서구', '6_11': '수영구', '6_12': '연제구',
            '6_13': '영도구', '6_14': '중구', '6_15': '해운대구', '6_16': '기장군',
            '6_99': '부산 전체',
            
            # 울산 (7)
            '7_1': '남구', '7_2': '동구', '7_3': '북구', '7_4': '울주군', 
            '7_5': '중구', '7_99': '울산 전체',
            
            # 세종 (8)
            '8_1': '세종시', '8_99': '세종 전체', 
            
            # 경기 (31)
            '31_1': '가평군', '31_2': '고양시', '31_3': '과천시', '31_4': '광명시',
            '31_5': '광주시', '31_6': '구리시', '31_7': '군포시', '31_8': '김포시',
            '31_9': '남양주시', '31_10': '동두천시', '31_11': '부천시', '31_12': '성남시',
            '31_13': '수원시', '31_14': '시흥시', '31_15': '안산시', '31_16': '안성시',
            '31_17': '안양시', '31_18': '양주시', '31_19': '양평군', '31_20': '여주시',
            '31_21': '연천군', '31_22': '오산시', '31_23': '용인시', '31_24': '의왕시',
            '31_25': '의정부시', '31_26': '이천시', '31_27': '파주시', '31_28': '평택시',
            '31_29': '포천시', '31_30': '하남시', '31_31': '화성시', '31_99': '경기 전체',
            
            # 강원 (32)
            '32_1': '강릉시', '32_2': '고성군', '32_3': '동해시', '32_4': '삼척시',
            '32_5': '속초시', '32_6': '양구군', '32_7': '양양군', '32_8': '영월군',
            '32_9': '원주시', '32_10': '인제군', '32_11': '정선군', '32_12': '철원군',
            '32_13': '춘천시', '32_14': '태백시', '32_15': '평창군', '32_16': '홍천군',
            '32_17': '화천군', '32_18': '횡성군', '32_99': '강원 전체',
            
            # 충북 (33)
            '33_1': '괴산군', '33_2': '단양군', '33_3': '보은군', '33_4': '영동군',
            '33_5': '옥천군', '33_6': '음성군', '33_7': '제천시', '33_8': '증평군',
            '33_9': '진천군', '33_10': '청주시', '33_11': '충주시', '33_12': '증평군',
            '33_99': '충북 전체',

            # 충남 (34)
            '34_1': '계룡시', '34_2': '공주시', '34_3': '금산군', '34_4': '논산시',
            '34_5': '당진시', '34_6': '보령시', '34_7': '부여군', '34_8': '서산시',
            '34_9': '서천군', '34_10': '아산시', '34_11': '예산군', '34_12': '천안시',
            '34_13': '청양군', '34_14': '태안군', '34_15': '홍성군', '34_16': '계룡시',
            '34_99': '충남 전체',

            # 경북 (35)
            '35_1': '경산시', '35_2': '경주시', '35_3': '고령군', '35_4': '구미시',
            '35_5': '김천시', '35_6': '문경시', '35_7': '봉화군', '35_8': '상주시', 
            '35_9': '성주군', '35_10': '안동시', '35_11': '영덕군', '35_12': '영양군', 
            '35_13': '영주시', '35_14': '영천시', '35_15': '예천군', '35_16': '울릉군', 
            '35_17': '울진군', '35_18': '의성군', '35_19': '청도군', '35_20': '청송군', 
            '35_21': '칠곡군', '35_22': '포항시', '35_23':'포항시', '35_99': '경북 전체',
            
            # 경남 (36)
            '36_1': '거제시', '36_2': '거창군', '36_3': '고성군', '36_4': '김해시',
            '36_5': '남해군', '36_6': '밀양시', '36_7': '사천시', '36_8': '산청군',
            '36_9': '양산시', '36_10': '의령군', '36_11': '진주시', '36_12': '창녕군',
            '36_13': '창원시', '36_14': '통영시', '36_15': '하동군', '36_16': '함안군',
            '36_17': '함양군', '36_18': '합천군', '36_19': '함안군', '36_20': '함양군',
            '36_21': '합천군', '36_99': '경남 전체',
                    
            # 전북 (37)
            '37_1': '고창군', '37_2': '군산시', '37_3': '김제시', '37_4': '남원시',
            '37_5': '무주군', '37_6': '부안군', '37_7': '순창군', '37_8': '완주군',
            '37_9': '익산시', '37_10': '임실군', '37_11': '장수군', '37_12': '전주시',
            '37_13': '정읍시', '37_14': '진안군', '37_99': '전북 전체',
            
            # 전남 (38)
            '38_1': '강진군', '38_2': '고흥군', '38_3': '곡성군', '38_4': '광양시',
            '38_5': '구례군', '38_6': '나주시', '38_7': '담양군', '38_8': '목포시',
            '38_9': '무안군', '38_10': '보성군', '38_11': '순천시', '38_12': '신안군',
            '38_13': '여수시', '38_14': '영광군', '38_15': '영암군', '38_16': '완도군',
            '38_17': '장성군', '38_18': '장흥군', '38_19': '진도군', '38_20': '함평군',
            '38_21': '해남군', '38_22': '화순군', '38_23': '해남군', '38_24': '화순군',
            '38_99': '전남 전체',
            
            # 제주 (39)
            '39_1': '제주시', '39_2': '서귀포시', '39_3': '서귀포시', '39_4': '제주시',
            '39_99': '제주 전체',
        }
        
        map_key = f"{area_code}_{sigungucode}"
        city_name = SIGUNGU_MAP.get(map_key, f'시군구_{sigungucode}')
        
        city, _ = City.objects.get_or_create(
            external_code=map_key,
            region=region,
            defaults={'name': city_name, 'is_active': True}
        )
        return city

    def get_or_create_category(self, contenttypeid, cat3=''):
        CATEGORY_MAP = {
            '12': '관광지', '14': '문화시설', '15': '축제/공연',
            '28': '레포츠', '32': '숙박', '38': '쇼핑', '39': '음식점',
        }
        
        category_name = CATEGORY_MAP.get(str(contenttypeid), '기타')

        # 음식점(39)인 경우 cat3 코드로 세분화
        if str(contenttypeid) == '39':
            FOOD_MAP = {
                'A05020100': '한식',
                'A05020200': '일식',
                'A05020300': '양식',
                'A05020900': '카페'
            }
            if cat3 in FOOD_MAP:
                category_name = FOOD_MAP[cat3]

        category, _ = Category.objects.get_or_create(
            name=category_name, defaults={'is_active': True}
        )
        return category

    def calculate_score(self, item):
        score = 50
        if item.get('firstimage'): score += 20
        if item.get('overview'): score += 20
        if item.get('addr1'): score += 10
        return min(score, 100)

    def fetch_images(self, trip, contentid):
        if trip.thumbnail_image:
            TripImage.objects.create(
                trip=trip, image_url=trip.thumbnail_image, order=1
            )