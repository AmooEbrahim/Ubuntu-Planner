# Tags Frontend Implementation

Vue 3 frontend for tag management.

## Store

Create `frontend/src/stores/tags.js`:

```javascript
import { defineStore } from 'pinia'
import api from '@/services/api'

export const useTagStore = defineStore('tags', {
  state: () => ({
    tags: [],
    loading: false,
    error: null
  }),

  getters: {
    globalTags: (state) => state.tags.filter(t => t.project_id === null),
    projectTags: (state) => state.tags.filter(t => t.project_id !== null),

    tagsByProject: (state) => (projectId) => {
      return state.tags.filter(t => t.project_id === projectId)
    }
  },

  actions: {
    async fetchTags() {
      this.loading = true
      try {
        const response = await api.get('/api/tags/')
        this.tags = response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTagsForProject(projectId) {
      const response = await api.get(`/api/tags/project/${projectId}`)
      return response.data
    },

    async createTag(tagData) {
      const response = await api.post('/api/tags/', tagData)
      this.tags.push(response.data)
      return response.data
    },

    async updateTag(tagId, tagData) {
      const response = await api.put(`/api/tags/${tagId}`, tagData)
      const index = this.tags.findIndex(t => t.id === tagId)
      if (index !== -1) {
        this.tags[index] = response.data
      }
      return response.data
    },

    async deleteTag(tagId) {
      await api.delete(`/api/tags/${tagId}`)
      this.tags = this.tags.filter(t => t.id !== tagId)
    }
  }
})
```

## Tags Page

Create `frontend/src/views/Tags.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTagStore } from '@/stores/tags'
import { useProjectStore } from '@/stores/projects'
import TagForm from '@/components/TagForm.vue'

const tagStore = useTagStore()
const projectStore = useProjectStore()
const showForm = ref(false)
const editingTag = ref(null)
const filterProject = ref(null)

const filteredTags = computed(() => {
  if (!filterProject.value) return tagStore.tags

  if (filterProject.value === 'global') {
    return tagStore.globalTags
  }

  return tagStore.tagsByProject(filterProject.value)
})

onMounted(async () => {
  await tagStore.fetchTags()
  await projectStore.fetchProjects()
})

function openCreateForm() {
  editingTag.value = null
  showForm.value = true
}

function openEditForm(tag) {
  editingTag.value = tag
  showForm.value = true
}

async function handleDelete(tag) {
  if (confirm(`Delete tag "${tag.name}"?`)) {
    await tagStore.deleteTag(tag.id)
  }
}
</script>

<template>
  <div class="tags-page">
    <div class="header">
      <h1>Tags</h1>
      <div class="actions">
        <select v-model="filterProject">
          <option :value="null">All Tags</option>
          <option value="global">Global Tags Only</option>
          <option v-for="p in projectStore.activeProjects" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
        <button @click="openCreateForm" class="btn-primary">
          + New Tag
        </button>
      </div>
    </div>

    <div class="tags-list">
      <div v-for="tag in filteredTags" :key="tag.id" class="tag-card">
        <span class="tag-preview" :style="{ backgroundColor: tag.color }">
          {{ tag.name }}
        </span>
        <span class="tag-scope">
          {{ tag.project_id ? 'Project' : 'Global' }}
        </span>
        <div class="tag-actions">
          <button @click="openEditForm(tag)">Edit</button>
          <button @click="handleDelete(tag)">Delete</button>
        </div>
      </div>
    </div>

    <TagForm
      v-if="showForm"
      :tag="editingTag"
      @close="showForm = false"
      @saved="showForm = false"
    />
  </div>
</template>
```

## Tag Selector Component (Reusable)

Create `frontend/src/components/TagSelector.vue`:

```vue
<script setup>
import { ref, computed, watch } from 'vue'
import { useTagStore } from '@/stores/tags'

const props = defineProps({
  projectId: Number,  // Project context
  modelValue: Array   // Selected tag IDs
})

const emit = defineEmits(['update:modelValue'])

const tagStore = useTagStore()
const availableTags = ref([])
const searchQuery = ref('')

watch(() => props.projectId, async (newProjectId) => {
  if (newProjectId) {
    availableTags.value = await tagStore.fetchTagsForProject(newProjectId)
  } else {
    availableTags.value = tagStore.globalTags
  }
}, { immediate: true })

const filteredTags = computed(() => {
  if (!searchQuery.value) return availableTags.value

  const query = searchQuery.value.toLowerCase()
  return availableTags.value.filter(t =>
    t.name.toLowerCase().includes(query)
  )
})

function toggleTag(tagId) {
  const selected = [...props.modelValue]
  const index = selected.indexOf(tagId)

  if (index > -1) {
    selected.splice(index, 1)
  } else {
    selected.push(tagId)
  }

  emit('update:modelValue', selected)
}

function isSelected(tagId) {
  return props.modelValue.includes(tagId)
}
</script>

<template>
  <div class="tag-selector">
    <input
      v-model="searchQuery"
      placeholder="Search or create tag..."
      class="search-input"
    >

    <div class="tags-grid">
      <button
        v-for="tag in filteredTags"
        :key="tag.id"
        @click="toggleTag(tag.id)"
        :class="['tag-btn', { selected: isSelected(tag.id) }]"
        :style="{
          backgroundColor: isSelected(tag.id) ? tag.color : 'transparent',
          borderColor: tag.color,
          color: isSelected(tag.id) ? 'white' : tag.color
        }"
      >
        {{ tag.name }}
      </button>
    </div>

    <div v-if="props.modelValue.length" class="selected-tags">
      Selected: {{ props.modelValue.length }} tag(s)
    </div>
  </div>
</template>
```

## Checklist

- [ ] Tag store created
- [ ] Tags page created
- [ ] Tag form component created
- [ ] Tag selector component created (reusable)
- [ ] Global vs project-specific filtering works
- [ ] Create/edit/delete works
- [ ] Tag inheritance displayed correctly
