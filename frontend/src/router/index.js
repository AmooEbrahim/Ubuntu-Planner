import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Projects from '../views/Projects.vue'
import Tags from '../views/Tags.vue'

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
    }
  ]
})

export default router
