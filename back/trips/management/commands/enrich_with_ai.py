import time
import json
from google import genai
from django.core.management.base import BaseCommand
from django.db import models
from trips.models import Trip
from decouple import config

class Command(BaseCommand):
    help = 'Enrich trip data with Gemini AI (Extracting precise business hours & Holidays)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of items to process',
        )

    def format_time(self, t_str):
        """24:00 등의 잘못된 시간 형식을 23:59로 보정"""
        if not t_str: return "00:00"
        if t_str.startswith("24:"): return "23:59"
        return t_str

    def handle(self, *args, **options):
        # 1. Gemini 설정
        api_key = config('GEMINI_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('GEMINI_API_KEY NOT FOUND in .env'))
            return

        client = genai.Client(api_key=api_key)
        
        # [진단] 사용 가능한 모델 목록 출력
        self.stdout.write("--- 사용 가능한 모델 목록 ---")
        try:
            for m in client.models.list():
                self.stdout.write(f" - {m.name}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"모델 목록을 가져오는 데 실패했습니다: {e}"))

        # 목록에 명백히 존재하는 가장 안정적인 모델 명칭 사용
        model_name = "gemini-flash-latest" 

        # 2. 가공 대상 선정 (영업시간이 없거나, 휴무일 정보가 아직 분석되지 않은 데이터)
        # 모든 휴무일 필드가 False인 것을 '아직 분석 안 됨'의 기준으로 삼습니다.
        target_trips = Trip.objects.filter(
            use_time__isnull=False
        ).filter(
            models.Q(open_time__isnull=True) | 
            models.Q(is_closed_mon=False, is_closed_tue=False, is_closed_wed=False, 
                     is_closed_thu=False, is_closed_fri=False, is_closed_sat=False, is_closed_sun=False)
        ).exclude(use_time='')[:options['limit']]

        if not target_trips.exists():
            self.stdout.write(self.style.SUCCESS('가공할 데이터가 없습니다.'))
            return

        self.stdout.write(self.style.WARNING(f'🚀 {target_trips.count()}개의 데이터를 AI로 가공하기 시작합니다...'))

        for trip in target_trips:
            self.stdout.write(f'--- [{trip.title}] 분석 중 ---')
            
            prompt = f"""
            너는 여행지 운영 정보 분석 전문가야. 
            아래 [이용시간]과 [휴무일] 정보를 분석해서 가장 정확한 운영 정보를 추출해줘.
            
            [이용시간]: {trip.use_time}
            [휴무일]: {trip.rest_date}
            
            [규칙]:
            1. 반드시 JSON 형식으로만 응답해.
            2. "open": 시작시간(HH:MM), "close": 종료시간(HH:MM).
            3. "closed_days": 휴무 요일을 리스트 형태로 포함해. (Mon, Tue, Wed, Thu, Fri, Sat, Sun) 
               예: ["Mon"] 또는 ["Sat", "Sun"]
            4. '연중무휴'나 '상시개방'이면 "closed_days": [] 로 해줘.
            5. 오직 JSON만 출력해.
            """

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                
                # JSON 문자열 추출 (new SDK에서는 response.text 사용)
                json_str = response.text.strip().replace('```json', '').replace('```', '')
                data = json.loads(json_str)

                # 데이터 업데이트
                trip.open_time = self.format_time(data.get('open'))
                trip.close_time = self.format_time(data.get('close'))
                
                # 휴무일 필드 초기화 후 업데이트
                closed_days = data.get('closed_days', [])
                trip.is_closed_mon = "Mon" in closed_days
                trip.is_closed_tue = "Tue" in closed_days
                trip.is_closed_wed = "Wed" in closed_days
                trip.is_closed_thu = "Thu" in closed_days
                trip.is_closed_fri = "Fri" in closed_days
                trip.is_closed_sat = "Sat" in closed_days
                trip.is_closed_sun = "Sun" in closed_days
                
                trip.save()

                self.stdout.write(self.style.SUCCESS(f"  ✅ 업데이트 완료: {data.get('open')}~{data.get('close')} / 휴무: {closed_days}"))
                
                # 무료 티어 한도(분당 5회)를 지키기 위해 15초 대기
                time.sleep(15)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ 에러 발생 ({trip.title}): {str(e)}"))

        self.stdout.write(self.style.SUCCESS('\n✨ 모든 AI 가공 작업이 완료되었습니다!'))
