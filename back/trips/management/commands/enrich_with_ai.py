import time
import json
from google import genai
from django.core.management.base import BaseCommand
from trips.models import Trip
from decouple import config

class Command(BaseCommand):
    help = 'Enrich trip data with Gemini AI (Extracting precise business hours)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of items to process',
        )

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

        # 2. 가공 대상 선정 (open_time이 비어있고, use_time 원본이 있는 데이터)
        target_trips = Trip.objects.filter(
            open_time__isnull=True,
            use_time__isnull=False
        ).exclude(use_time='')[:options['limit']]

        if not target_trips.exists():
            self.stdout.write(self.style.SUCCESS('가공할 데이터가 없습니다.'))
            return

        self.stdout.write(self.style.WARNING(f'🚀 {target_trips.count()}개의 데이터를 AI로 가공하기 시작합니다...'))

        for trip in target_trips:
            self.stdout.write(f'--- [{trip.title}] 분석 중 ---')
            
            prompt = f"""
            너는 여행지 운영시간 분석 전문가야. 
            아래 제공되는 [이용시간] 텍스트를 분석해서, 현재 시즌(1월)에 가장 적합한 시작시간과 종료시간을 HH:MM 형식으로 추출해줘.
            
            [이용시간]: {trip.use_time}
            
            [규칙]:
            1. 반드시 JSON 형식으로만 응답해: {{"open": "HH:MM", "close": "HH:MM"}}
            2. '상시개방'이거나 시간이 명확하지 않으면 "00:00", "23:59"로 답해줘.
            3. 월별/계절별로 다르면 현재 1월에 해당하는 시간을 선택해.
            4. 오직 JSON만 출력하고 다른 설명은 하지마.
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
                trip.open_time = data.get('open')
                trip.close_time = data.get('close')
                trip.save()

                self.stdout.write(self.style.SUCCESS(f"  ✅ 업데이트 완료: {data.get('open')} ~ {data.get('close')}"))
                
                # 무료 티어 한도(분당 5회)를 지키기 위해 15초 대기
                time.sleep(15)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ 에러 발생 ({trip.title}): {str(e)}"))

        self.stdout.write(self.style.SUCCESS('\n✨ 모든 AI 가공 작업이 완료되었습니다!'))
