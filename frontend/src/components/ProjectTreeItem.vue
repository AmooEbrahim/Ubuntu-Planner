<script setup>
import { ref } from 'vue'

const props = defineProps({
  project: Object
})

const emit = defineEmits(['edit', 'delete', 'toggle-archive', 'toggle-pin'])

const expanded = ref(false)

function toggleExpand() {
  expanded.value = !expanded.value
}
</script>

<template>
  <div class="project-tree-item">
    <div class="project-row border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3 flex-1">
          <button
            v-if="project.children && project.children.length > 0"
            @click="toggleExpand"
            class="text-gray-500 hover:text-gray-700 w-6 text-left"
          >
            <span v-if="expanded">▼</span>
            <span v-else>▶</span>
          </button>
          <span v-else class="w-6"></span>

          <div
            class="w-4 h-4 rounded"
            :style="{ backgroundColor: project.color }"
          ></div>

          <span class="font-medium text-gray-800">{{ project.name }}</span>

          <span
            v-if="project.is_pinned"
            class="text-yellow-500"
            title="Pinned"
          >📌</span>

          <span
            v-if="project.is_archived"
            class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded"
          >Archived</span>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="emit('toggle-pin', project)"
            class="text-sm px-3 py-1 text-gray-600 hover:text-yellow-600"
            :title="project.is_pinned ? 'Unpin' : 'Pin'"
          >
            {{ project.is_pinned ? 'Unpin' : 'Pin' }}
          </button>
          <button
            @click="emit('edit', project)"
            class="text-sm px-3 py-1 text-blue-600 hover:text-blue-800"
          >
            Edit
          </button>
          <button
            @click="emit('toggle-archive', project)"
            class="text-sm px-3 py-1 text-gray-600 hover:text-gray-800"
          >
            {{ project.is_archived ? 'Unarchive' : 'Archive' }}
          </button>
          <button
            @click="emit('delete', project)"
            class="text-sm px-3 py-1 text-red-600 hover:text-red-800"
          >
            Delete
          </button>
        </div>
      </div>

      <div v-if="project.description" class="mt-2 text-sm text-gray-600 ml-9">
        {{ project.description }}
      </div>
    </div>

    <!-- Render children recursively -->
    <div
      v-if="expanded && project.children && project.children.length > 0"
      class="ml-8 mt-2 space-y-2"
    >
      <ProjectTreeItem
        v-for="child in project.children"
        :key="child.id"
        :project="child"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @toggle-archive="emit('toggle-archive', $event)"
        @toggle-pin="emit('toggle-pin', $event)"
      />
    </div>
  </div>
</template>
