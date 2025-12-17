import requests
import time
from urllib.parse import unquote # 키 안전장치
from django.core.management.base import BaseCommand
from trips.models import Trip, TripImage, Region, City, Category
from decouple import config

class Command(BaseCommand):
    help = 'Import data from TourAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--area-code',
            type=str,
            help='Area code (1=서울, 6=부산, 39=제주 등)',
        )

    def handle(self, *args, **options):
        raw_key = config('TOUR_API_KEY')
        API_KEY = unquote(raw_key)
        BASE_URL = 'https://apis.data.go.kr/B551011/KorService2'
        endpoint = '/areaBasedList2'
        
        area_code = options.get('area_code', '1')
        self.stdout.write(f'Importing ALL data for area code: {area_code}')

        page = 1 
        total_imported = 0

        while True:
            self.stdout.write(f'Fetching page {page}...')

            params = {
                'serviceKey': API_KEY,
                'numOfRows': 100,     
                'pageNo': page,    
                'MobileOS': 'ETC',
                'MobileApp': 'TripPlanner',
                'areaCode': area_code,
                'arrange': 'A',
                '_type': 'json',
                'contentTypeId': '12'
            }
            
            try:
                response = requests.get(
                    f'{BASE_URL}{endpoint}',
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f'API Error on page {page}: {response.status_code}'))
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
                        self.stdout.write(self.style.SUCCESS('No more items. Finished!'))
                        break
                else:
                    self.stdout.write(self.style.ERROR('Invalid response structure'))
                    break

                count = 0
                for item in items:
                    if self.process_item(item):
                        count += 1
                        total_imported += 1
                
                self.stdout.write(f'  - Saved {count} items on page {page}')
                
                if len(items) < 100:
                    self.stdout.write(self.style.SUCCESS(f'Reached the last page. Total imported: {total_imported}'))
                    break
                
                page += 1
                time.sleep(0.1)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error on page {page}: {str(e)}'))
                break

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
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action}: {trip.title}')
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing item: {str(e)}'))
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