<template>
  <navbar v-if="!route.meta.hideNavbar"/>
  <div>
    
  </div>
  <RouterView />
</template>

<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import navbar from '@/components/navbar.vue'

const route = useRoute()
</script>

<style scoped>

</style>