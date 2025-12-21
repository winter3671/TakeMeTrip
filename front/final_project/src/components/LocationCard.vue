<template>
  <div class="course-card">
    <div class="card-thumb">
      <img :src="trip.thumbnail_image" :alt="trip.title" />
    </div>

    <div class="card-info">
      <div class="info-header">
        <h3 class="title">{{ trip.title }}</h3>
        </div>
      
      <p class="address">{{ trip.region_name }} {{ trip.city_name }}</p>
      
    </div>

  </div>
</template>

<script setup>
defineProps({
  trip: {
    type: Object,
    required: true
  }
});
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
}

.address {
  font-size: 13px;
  color: #888;
  margin-bottom: 8px;
}
</style>