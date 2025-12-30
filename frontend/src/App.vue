<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <SessionBanner />
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex space-x-8">
            <RouterLink to="/" class="inline-flex items-center px-1 pt-1 text-gray-900 font-medium hover:text-blue-600">
              Dashboard
            </RouterLink>
            <RouterLink to="/projects" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Projects
            </RouterLink>
            <RouterLink to="/tags" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Tags
            </RouterLink>
            <RouterLink to="/planning" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Planning
            </RouterLink>
            <RouterLink to="/sessions" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Sessions
            </RouterLink>
            <RouterLink to="/statistics" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Statistics
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView, RouterLink } from 'vue-router'
import SessionBanner from '@/components/SessionBanner.vue'
</script>

<style scoped>
.router-link-active {
  border-bottom: 2px solid #3B82F6;
  color: #3B82F6;
}
</style>
