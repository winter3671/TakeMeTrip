<template>
  <div class="course-card">
    <div class="card-thumb">
      <img :src="trip.thumbnail_image || '/src/assets/no-image.png'" :alt="trip.title" />
    </div>

    <div class="card-info">
      <div class="info-header">
        <h3 class="title">{{ trip.title }}</h3>
        
      </div>
      
      <p class="address">
        {{ trip.region_name }} {{ trip.city_name }}
      <span class="distance-badge" v-if="userLocation && trip.mapy && trip.mapx">
        내 위치로부터 {{ getDistanceFromLatLon(userLocation.lat, userLocation.lon, trip.mapy, trip.mapx) }}
      </span>
      </p>
    </div>

  </div>
</template>

<script setup>
const props = defineProps({
  trip: {
    type: Object,
    required: true
  },
  userLocation: {
    type: Object,
    default: null
  }
});

const deg2rad = (deg) => {
  return deg * (Math.PI / 180);
}

const getDistanceFromLatLon = (lat1, lon1, lat2, lon2) => {
  if (!lat1 || !lon1 || !lat2 || !lon2) return "";
  
  const R = 6371;
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
            
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const d = R * c; 
  
  if (d < 1) return (d * 1000).toFixed(0) + "m";
  return d.toFixed(1) + "km";
}
</script>

<style scoped>
.course-card {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.course-card:hover {
  background-color: #fafafa;
}

.card-thumb {
  width: 160px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #f0f0f0;
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.address {
  display: flex; 
  justify-content: space-between;
  align-items: center;
  
  font-size: 13px;
  color: #888;
  margin-bottom: 4px;
}

.distance-badge {
  font-size: 13px;
  font-weight: 700;
  background-color: #fff0f0;
  padding: 2px 8px;
  border-radius: 12px;
  white-space: nowrap;
}

</style>