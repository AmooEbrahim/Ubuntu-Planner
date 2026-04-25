<script setup>
import ProjectTreeItem from './ProjectTreeItem.vue'

const props = defineProps({
  projects: Array
})

const emit = defineEmits(['edit', 'delete', 'toggle-archive', 'toggle-pin', 'add-child', 'start-session'])
</script>

<template>
  <div>
    <div
      v-if="!projects || projects.length === 0"
      class="glass-card flex flex-col items-center justify-center py-16 px-8 text-center text-muted"
    >
      <div class="flex items-center justify-center w-14 h-14 rounded-full bg-fg-subtle/15 text-fg-subtle mb-4">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <p class="text-sm">No projects found. Create your first project to get started.</p>
    </div>

    <div v-else class="flex flex-col gap-2">
      <ProjectTreeItem
        v-for="project in projects"
        :key="project.id"
        :project="project"
        :depth="0"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @toggle-archive="emit('toggle-archive', $event)"
        @toggle-pin="emit('toggle-pin', $event)"
        @add-child="emit('add-child', $event)"
        @start-session="emit('start-session', $event)"
      />
    </div>
  </div>
</template>
