import requests
import time
from urllib.parse import unquote
from django.core.management.base import BaseCommand
from trips.models import Trip, TripImage, Region, City, Category
from decouple import config

class Command(BaseCommand):
    help = 'Import data from TourAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-code',
            type=str,
            nargs='?', 
            help='Area code (If empty, imports ALL regions)',
        )

    def handle(self, *args, **options):
        raw_key = config('TOUR_API_KEY')
        API_KEY = unquote(raw_key)
        BASE_URL = 'https://apis.data.go.kr/B551011/KorService2'
        endpoint = '/areaBasedList2'

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
            '12': '관광지', '14': '문화시설', '15': '축제/공연', '25': '여행코스',
            '28': '레포츠', '32': '숙박', '38': '쇼핑', '39': '음식점'
        }

        self.stdout.write(self.style.SUCCESS(f'Target Regions: {list(target_regions.values())}'))


        for area_code, area_name in target_regions.items():
            self.stdout.write(self.style.WARNING(f'\n\n🚀 Starting Region: {area_name} (Code: {area_code})'))
            
            for c_id, c_name in content_types.items():
                self.stdout.write(f'\n  Category: {c_name} (Code: {c_id})')
                
                page = 1
                total_imported_in_category = 0

                while True:
                    params = {
                        'serviceKey': API_KEY,
                        'numOfRows': 100,
                        'pageNo': page,
                        'MobileOS': 'ETC',
                        'MobileApp': 'TripPlanner',
                        'areaCode': area_code,
                        'arrange': 'A',
                        '_type': 'json',
                        'contentTypeId': c_id
                    }
                    
                    try:
                        response = requests.get(f'{BASE_URL}{endpoint}', params=params, timeout=30)
                        
                        if response.status_code != 200:
                            self.stdout.write(self.style.ERROR(f'API Error: {response.status_code}'))
                            break

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
                            if self.process_item(item):
                                count += 1
                                total_imported_in_category += 1
                        
                        self.stdout.write(f'    - {area_name} | {c_name} | p.{page}: Saved {count} items')
                        
                        if len(items) < 100:
                            break
                        
                        page += 1
                        
                        time.sleep(0.2) 

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                        break
                

                self.stdout.write(self.style.SUCCESS(f'  -> Finished {c_name} in {area_name}: {total_imported_in_category} items'))

    
    def process_item(self, item):
        try:
            if not item.get('contentid') or not item.get('title'):
                return False
            
            region = self.get_or_create_region(item.get('areacode', '1'))
            city = None
            if item.get('sigungucode'):
                city = self.get_or_create_city(item.get('sigungucode'), region)
            
            category = self.get_or_create_category(item.get('contenttypeid', '12'))
            
            trip, created = Trip.objects.update_or_create(
                external_id=item['contentid'],
                defaults={
                    'title': item.get('title', '')[:200],
                    'description': item.get('overview', '')[:1000],
                    'destination': item.get('addr1', '')[:100],
                    'region': region,
                    'city': city,
                    'category': category,
                    'thumbnail_image': item.get('firstimage', ''),
                    'price': 0,
                    'duration': 1,
                    'status': 'active',
                    'recommendation_score': self.calculate_score(item),
                }
            )
            
            if created or not trip.images.exists():
                self.fetch_images(trip, item['contentid'])
            return True
            
        except Exception as e:
            return False

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

    def get_or_create_city(self, sigungucode, region):
        city, _ = City.objects.get_or_create(
            external_code=str(sigungucode),
            region=region,
            defaults={'name': f'시군구_{sigungucode}', 'is_active': True}
        )
        return city

    def get_or_create_category(self, contenttypeid):
        CATEGORY_MAP = {
            '12': '관광지', '14': '문화시설', '15': '축제/공연', '25': '여행코스',
            '28': '레포츠', '32': '숙박', '38': '쇼핑', '39': '음식점',
        }
        category_name = CATEGORY_MAP.get(str(contenttypeid), '기타')
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