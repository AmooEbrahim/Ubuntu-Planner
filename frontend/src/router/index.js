import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Projects from '../views/Projects.vue'
import Tags from '../views/Tags.vue'
import Planning from '../views/Planning.vue'
import Sessions from '../views/Sessions.vue'
import Statistics from '../views/Statistics.vue'

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
      component: Sessions
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: Statistics
    }
  ]
})

export default router
