import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Projects from '../views/Projects.vue'
import Tags from '../views/Tags.vue'
import Planning from '../views/Planning.vue'
import Sessions from '../views/Sessions.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
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
    }
  ]
})

export default router
