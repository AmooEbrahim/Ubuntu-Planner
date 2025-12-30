<script setup>
import { ref } from 'vue'
import ProjectTreeItem from './ProjectTreeItem.vue'

const props = defineProps({
  projects: Array
})

const emit = defineEmits(['edit', 'delete', 'toggle-archive', 'toggle-pin'])
</script>

<template>
  <div class="project-tree">
    <div v-if="!projects || projects.length === 0" class="text-gray-500 text-center py-8">
      No projects found. Create your first project to get started.
    </div>

    <div v-else class="space-y-2">
      <ProjectTreeItem
        v-for="project in projects"
        :key="project.id"
        :project="project"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @toggle-archive="emit('toggle-archive', $event)"
        @toggle-pin="emit('toggle-pin', $event)"
      />
    </div>
  </div>
</template>
