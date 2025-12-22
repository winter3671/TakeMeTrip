<template>
  <div>
    <button @click="logout">Logout</button>
  </div>
</template>

<script setup>
import { useAccountStore } from '@/stores/accounts';

const store = useAccountStore()

const logout = () => {
  store.logOut()
}
</script>

<style scoped>

</style>