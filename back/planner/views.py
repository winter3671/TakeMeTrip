# back/planner/views.py
import math
import random 
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from trips.models import Trip, Wishlist, Region
from trips.serializers import TripListSerializer
from .serializers import PlannerInputSerializer, RegionSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# --- Helper Functions (Static) ---

def calculate_distance(p1, p2):
    if not (p1.mapx and p1.mapy and p2.mapx and p2.mapy):
        return 99999
    return math.sqrt(
        (float(p1.mapx) - float(p2.mapx))**2 + 
        (float(p1.mapy) - float(p2.mapy))**2
    )

def get_mapx(trip):
    try:
        return float(trip.mapx) if trip.mapx else 999.0
    except (ValueError, TypeError):
        return 999.0

def calculate_move_time_minutes(dist_coord):
    km = dist_coord * 111
    hours = km / 40 
    return int(hours * 60) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_region_list(request):
    regions = Region.objects.prefetch_related('cities').all()
    serializer = RegionSerializer(regions, many=True)
    return Response(serializer.data)

class AIPlannerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PlannerInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.validated_data
        user = request.user
        
        start_date = data['start_date']
        duration = (data['end_date'] - start_date).days + 1
        user_loc = type('UserLoc', (), {'mapx': data['current_mapx'], 'mapy': data['current_mapy']})()

        all_places = Trip.objects.filter(
            region_id=data['region_id'], 
            city_id=data['city_id'],
            status='active'
        )
        if not all_places.exists():
            return Response({"message": "해당 지역에 데이터가 없습니다."}, status=404)

        my_wish_ids = set(Wishlist.objects.filter(user=user).values_list('trip_id', flat=True))

        pools = self._classify_and_score_places(all_places, my_wish_ids)
        
        if not pools['attractions']:
             return Response({"message": "관광지 데이터가 부족합니다."}, status=400)

        anchors = self._select_anchors(pools['attractions'], duration)
        best_accommodation = self._select_best_accommodation(anchors, pools['accommodations'], my_wish_ids)

        travel_time_minutes = self._calc_initial_travel_time(user_loc, anchors[0])

        plan = self._generate_schedule(
            request, anchors, best_accommodation, pools, 
            start_date, duration, travel_time_minutes, 
            used_ids=set(a.id for a in anchors), 
            wish_ids=my_wish_ids
        )

        return Response({
            "duration": duration,
            "travel_time_to_dest": travel_time_minutes,
            "region_id": data['region_id'],
            "recommended_accommodation": TripListSerializer(best_accommodation, context={'request': request}).data if best_accommodation else None,
            "plan": plan
        })

    # --- Internal Logic Methods ---

    def _classify_and_score_places(self, places, wish_ids):
        """초기 분류 및 점수 계산 (좋아요 반영 O, 조회수 X)"""
        pools = {'attractions': [], 'restaurants': [], 'accommodations': []}

        for trip in places:
            base_score = trip.recommendation_score if trip.recommendation_score else 50
            wish_bonus = 150 if trip.id in wish_ids else 0
            
            # 대중성 점수 (좋아요만 반영)
            raw_popularity = trip.like_count * 2
            popularity_bonus = min(raw_popularity, 60)
            
            noise = random.uniform(-5, 5)
            final_score = base_score + wish_bonus + popularity_bonus + noise
            
            item = {'trip': trip, 'score': final_score}
            
            if trip.category_id == 8: 
                pools['restaurants'].append(item)
            elif trip.category_id == 6: 
                pools['accommodations'].append(item)
            else: 
                pools['attractions'].append(item)

        for key in pools:
            pools[key].sort(key=lambda x: x['score'], reverse=True)
            pools[key] = [x['trip'] for x in pools[key]]
        
        return pools

    def _select_anchors(self, attractions, duration):
        candidates = attractions[:duration * 15]
        anchors = []
        used_ids = set()

        start_node = min(candidates, key=get_mapx)
        anchors.append(start_node)
        used_ids.add(start_node.id)

        while len(anchors) < duration:
            last_anchor = anchors[-1]
            remaining = [t for t in candidates if t.id not in used_ids]
            if not remaining: break
            
            remaining.sort(key=lambda x: calculate_distance(last_anchor, x))
            
            top_k = remaining[:3]
            next_anchor = random.choice(top_k)
            
            anchors.append(next_anchor)
            used_ids.add(next_anchor.id)
            
        return anchors

    def _select_best_accommodation(self, anchors, accommodations, wish_ids):
        if not accommodations or not anchors: return None

        valid_anchors = [a for a in anchors if a.mapx and a.mapy]
        if not valid_anchors: return accommodations[0]

        avg_x = sum(float(a.mapx) for a in valid_anchors) / len(valid_anchors)
        avg_y = sum(float(a.mapy) for a in valid_anchors) / len(valid_anchors)
        centroid = type('Centroid', (), {'mapx': avg_x, 'mapy': avg_y})()

        candidates_with_score = []
        for acc in accommodations:
            p_base = acc.recommendation_score if acc.recommendation_score else 50
            p_wish = 150 if acc.id in wish_ids else 0
            
            raw_popularity = acc.like_count * 2
            popularity_bonus = min(raw_popularity, 60)
            
            dist = calculate_distance(centroid, acc)
            distance_penalty = dist * 2500 
            
            final = (p_base + p_wish + popularity_bonus) - distance_penalty
            candidates_with_score.append((acc, final))
        
        candidates_with_score.sort(key=lambda x: x[1], reverse=True)
        
        top_k_accs = [item[0] for item in candidates_with_score[:3]]
        return random.choice(top_k_accs) if top_k_accs else None

    def _calc_initial_travel_time(self, user_loc, dest):
        dist = calculate_distance(user_loc, dest)
        km = dist * 111
        speed = 70 if km > 10 else 40
        return int((km / speed) * 60)

    def _generate_schedule(self, request, anchors, accommodation, pools, start_date, duration, travel_time, used_ids, wish_ids):
        plan = []
        
        for day_idx, anchor in enumerate(anchors):
            day_items = []
            current_date_obj = start_date + timedelta(days=day_idx)
            is_first_day = (day_idx == 0)
            is_last_day = (day_idx == duration - 1)

            if is_first_day:
                current_place = anchor 
                current_time = datetime.combine(current_date_obj, datetime.min.time()).replace(hour=9, minute=0) + timedelta(minutes=travel_time)
            else:
                current_place = accommodation if accommodation else anchor
                current_time = datetime.combine(current_date_obj, datetime.min.time()).replace(hour=9, minute=0)

                if accommodation:
                    day_items.append(self._make_item("accommodation", "start", current_time, accommodation, request))
                    move_min = calculate_move_time_minutes(calculate_distance(accommodation, anchor))
                    current_time += timedelta(minutes=move_min)

            # 오전 일정
            lunch_threshold = current_time.replace(hour=11, minute=30)
            if current_time < lunch_threshold:
                day_items.append(self._make_item("spot", current_time, current_time, anchor, request))
                current_time += timedelta(minutes=90)
                last_visited = anchor 
                current_place = anchor

                if current_time < lunch_threshold:
                    am_spot = self._find_best_nearby(
                        current_place, pools['attractions'], used_ids, wish_ids, 
                        current_date_obj, last_place=last_visited
                    )
                    if am_spot:
                        move_min = calculate_move_time_minutes(calculate_distance(current_place, am_spot))
                        expected_end = current_time + timedelta(minutes=move_min + 60)
                        
                        if expected_end <= current_time.replace(hour=13, minute=0):
                            current_time += timedelta(minutes=move_min)
                            day_items.append(self._make_item("spot", current_time, current_time, am_spot, request))
                            used_ids.add(am_spot.id)
                            current_place = am_spot
                            last_visited = am_spot
                            current_time += timedelta(minutes=60)

            # 점심
            lunch_limit = current_time.replace(hour=14, minute=0)
            if current_time < lunch_limit:
                lunch_spot = self._find_best_nearby(
                    current_place, pools['restaurants'], used_ids, wish_ids, 
                    current_date_obj, is_restaurant=True
                )
                if lunch_spot:
                    move_min = calculate_move_time_minutes(calculate_distance(current_place, lunch_spot))
                    arrival_at_lunch = current_time + timedelta(minutes=move_min)
                    real_lunch_time = max(arrival_at_lunch, current_time.replace(hour=12, minute=0))
                    
                    day_items.append(self._make_item("meal", real_lunch_time, real_lunch_time, lunch_spot, request))
                    current_place = lunch_spot
                    last_visited = lunch_spot
                    current_time = real_lunch_time + timedelta(minutes=60)

            # 오후
            if is_last_day and duration > 1:
                pass 
            else:
                for _ in range(2):
                    if current_time.hour >= 18: break
                    pm_spot = self._find_best_nearby(
                        current_place, pools['attractions'], used_ids, wish_ids, 
                        current_date_obj, last_place=last_visited
                    )
                    if pm_spot:
                        move_min = calculate_move_time_minutes(calculate_distance(current_place, pm_spot))
                        current_time += timedelta(minutes=move_min)
                        day_items.append(self._make_item("spot", current_time, current_time, pm_spot, request))
                        used_ids.add(pm_spot.id)
                        current_place = pm_spot
                        last_visited = pm_spot
                        current_time += timedelta(minutes=90)

                # 저녁
                dinner_spot = self._find_best_nearby(
                    current_place, pools['restaurants'], used_ids, wish_ids, 
                    current_date_obj, is_restaurant=True
                )
                if dinner_spot:
                    move_min = calculate_move_time_minutes(calculate_distance(current_place, dinner_spot))
                    arrival_at_dinner = current_time + timedelta(minutes=move_min)
                    real_dinner_time = max(arrival_at_dinner, current_time.replace(hour=18, minute=0))
                    
                    day_items.append(self._make_item("meal", real_dinner_time, real_dinner_time, dinner_spot, request))
                    current_place = dinner_spot
                    current_time = real_dinner_time + timedelta(minutes=60)

                if accommodation:
                    move_to_acc = calculate_move_time_minutes(calculate_distance(current_place, accommodation))
                    arrival_acc = current_time + timedelta(minutes=move_to_acc)
                    status = "check-in" if is_first_day else "return"
                    day_items.append(self._make_item("accommodation", status, arrival_acc, accommodation, request))

            plan.append({
                "day": day_idx + 1,
                "date": current_date_obj.strftime("%Y-%m-%d"),
                "schedule": day_items
            })
            
        return plan

    def _find_best_nearby(self, current_place, pool, used_ids, wish_ids, date, is_restaurant=False, last_place=None):
        candidates_with_score = []

        for potential in pool:
            if potential.id in used_ids: continue
            if is_restaurant and potential.id == current_place.id: continue

            if not self._is_open(potential, date):
                continue 

            p_base = potential.recommendation_score if potential.recommendation_score else 50
            p_wish = 150 if potential.id in wish_ids else 0
            
            raw_popularity = potential.like_count * 2
            popularity_bonus = min(raw_popularity, 60)

            dist = calculate_distance(current_place, potential)
            penalty_weight = 3000 if is_restaurant else 2000
            distance_penalty = dist * penalty_weight
            
            variety_penalty = 0
            if last_place and not is_restaurant: 
                last_cat = getattr(last_place, 'category_id', None)
                curr_cat = getattr(potential, 'category_id', None)
                if last_cat and curr_cat and last_cat == curr_cat:
                    variety_penalty = 80 
            
            final_score = (p_base + p_wish + popularity_bonus) - distance_penalty - variety_penalty
            
            candidates_with_score.append((potential, final_score))
        
        candidates_with_score.sort(key=lambda x: x[1], reverse=True)
        
        if not candidates_with_score:
            return None
        
        top_k = candidates_with_score[:5]
        
        weights = []
        for i in range(len(top_k)):
            if i < 3: 
                weights.append(10)
            else:     
                weights.append(2)
        
        selected_tuple = random.choices(top_k, weights=weights, k=1)[0]
        
        return selected_tuple[0]

    def _is_open(self, trip, date):
        if not getattr(trip, 'rest_date', None): 
            return True 
        
        weekday = date.weekday()
        korean_days = ["월", "화", "수", "목", "금", "토", "일"]
        current_day_char = korean_days[weekday] 

        if current_day_char in trip.rest_date:
            return False 
        
        return True 

    def _make_item(self, type_name, status_or_time, time_obj, trip, request):
        time_str = time_obj.strftime("%H:%M") if hasattr(time_obj, 'strftime') else status_or_time
        
        item = {
            "type": type_name,
            "time": time_str,
            "data": TripListSerializer(trip, context={'request': request}).data
        }
        if type_name == "accommodation":
            item["status"] = status_or_time 
            item["time"] = time_obj.strftime("%H:%M")
        return item
    
