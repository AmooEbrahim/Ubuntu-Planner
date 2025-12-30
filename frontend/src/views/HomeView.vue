<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold text-gray-800 mb-4">Ubuntu Planner</h1>
    <p class="text-lg text-gray-600 mb-8">Project planning and execution tracking service</p>

    <div v-if="loading" class="text-gray-600">Loading...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else class="bg-white rounded-lg shadow p-6">
      <h2 class="text-2xl font-semibold mb-4">API Status</h2>
      <p class="text-green-600">{{ apiStatus }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const loading = ref(true)
const error = ref(null)
const apiStatus = ref('')

onMounted(async () => {
  try {
    const response = await api.get('/health')
    apiStatus.value = `Backend is ${response.data.status}`
  } catch (e) {
    error.value = 'Failed to connect to backend API'
  } finally {
    loading.value = false
  }
})
</script>
