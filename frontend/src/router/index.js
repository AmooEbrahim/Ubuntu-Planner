import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Projects from '../views/Projects.vue'
import Tags from '../views/Tags.vue'
import Planning from '../views/Planning.vue'
import Sessions from '../views/Sessions.vue'
import SessionsDaily from '../views/SessionsDaily.vue'
import Statistics from '../views/Statistics.vue'
import SessionReview from '../views/SessionReview.vue'
import Settings from '../views/Settings.vue'
import DayMemory from '../views/DayMemory.vue'
import Chat from '../views/Chat.vue'
import AISettings from '../views/AISettings.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Dashboard
    },
    {
      path: '/projects',
      name: 'projects',
      component: Projects
    },
    {
      path: '/tags',
      name: 'tags',
      component: Tags
    },
    {
      path: '/planning',
      name: 'planning',
      component: Planning
    },
    {
      path: '/sessions',
      name: 'sessions',
      component: SessionsDaily
    },
    {
      path: '/sessions/list',
      name: 'sessions-list',
      component: Sessions
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: Statistics
    },
    {
      path: '/session-review/:id',
      name: 'session-review',
      component: SessionReview
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    },
    {
      path: '/day-memory',
      name: 'day-memory',
      component: DayMemory
    },
    {
      path: '/day-memory/:date',
      name: 'day-memory-date',
      component: DayMemory
    },
    {
      path: '/chat',
      name: 'chat',
      component: Chat
    },
    {
      path: '/chat/:id',
      name: 'chat-detail',
      component: Chat
    },
    {
      path: '/settings/ai',
      name: 'ai-settings',
      component: AISettings
    }
  ]
})

export default router
