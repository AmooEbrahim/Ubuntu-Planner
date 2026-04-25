<template>
  <div id="app" class="flex flex-col h-screen bg-gray-50 overflow-hidden">
    <Toaster :position="'bottom-right'" :rich-colors="true" :close-button="true" />
    <SessionBanner />
    <nav class="flex-shrink-0 bg-white shadow-sm border-b border-gray-200">
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
            <RouterLink to="/day-memory" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Day Memory
            </RouterLink>
            <RouterLink to="/chat" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Chat
            </RouterLink>
            <RouterLink to="/settings" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              Settings
            </RouterLink>
            <RouterLink to="/settings/ai" class="inline-flex items-center px-1 pt-1 text-gray-700 hover:text-blue-600">
              AI
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>
    <main class="flex-1 min-h-0 overflow-y-auto">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView, RouterLink } from 'vue-router'
import { Toaster } from 'vue-sonner'
import SessionBanner from '@/components/SessionBanner.vue'
</script>

<style scoped>
.router-link-active {
  border-bottom: 2px solid #3B82F6;
  color: #3B82F6;
}
</style>
