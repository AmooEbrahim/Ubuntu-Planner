<script setup>
import ProjectTreeItem from './ProjectTreeItem.vue'

const props = defineProps({
  projects: Array
})

const emit = defineEmits(['edit', 'delete', 'toggle-archive', 'toggle-pin', 'add-child', 'start-session'])
</script>

<template>
  <div class="project-tree">
    <div v-if="!projects || projects.length === 0" class="empty-tree">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
      </svg>
      <p>No projects found. Create your first project to get started.</p>
    </div>

    <div v-else class="tree-list">
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

<style scoped>
.project-tree {
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.empty-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #94a3b8;
}

.empty-tree svg {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
}

.empty-tree p {
  font-size: 0.95rem;
}

.tree-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
