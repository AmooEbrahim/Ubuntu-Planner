<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="page-title text-4xl mb-4">Ubuntu Planner</h1>
    <p class="page-subtitle text-lg mb-8">Project planning and execution tracking service</p>

    <div v-if="loading" class="text-muted">Loading...</div>
    <div v-else-if="error" class="text-danger">{{ error }}</div>
    <div v-else class="glass-card p-6">
      <h2 class="section-title text-2xl mb-4">API Status</h2>
      <p class="text-success font-semibold">{{ apiStatus }}</p>
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
