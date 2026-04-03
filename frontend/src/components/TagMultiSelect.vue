<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTagStore } from '@/stores/tags'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const tagStore = useTagStore()
const searchQuery = ref('')
const isOpen = ref(false)

onMounted(async () => {
  if (tagStore.tags.length === 0) {
    await tagStore.fetchTags()
  }
})

const availableTags = computed(() => {
  const selected = new Set(props.modelValue)
  return tagStore.tags.filter(tag =>
    !selected.has(tag.id) &&
    tag.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectedTags = computed(() => {
  return tagStore.tags.filter(tag => props.modelValue.includes(tag.id))
})

function toggleTag(tagId) {
  const current = [...props.modelValue]
  const index = current.indexOf(tagId)

  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(tagId)
  }

  emit('update:modelValue', current)
  searchQuery.value = ''
}

function removeTag(tagId) {
  const current = props.modelValue.filter(id => id !== tagId)
  emit('update:modelValue', current)
}

function handleClickOutside(event) {
  if (!event.target.closest('.tag-multiselect')) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="tag-multiselect">
    <!-- Selected Tags Display -->
    <div class="selected-tags" @click="isOpen = !isOpen">
      <div v-if="selectedTags.length === 0" class="placeholder">
        Select tags...
      </div>
      <div v-else class="tags-list">
        <span
          v-for="tag in selectedTags"
          :key="tag.id"
          class="tag-chip"
          :style="{ backgroundColor: tag.color + '20', borderColor: tag.color, color: tag.color }"
        >
          {{ tag.name }}
          <button
            type="button"
            @click.stop="removeTag(tag.id)"
            class="remove-btn"
          >
            ×
          </button>
        </span>
      </div>
      <svg class="dropdown-icon" :class="{ open: isOpen }" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </div>

    <!-- Dropdown -->
    <div v-if="isOpen" class="dropdown">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search tags..."
        class="search-input"
        @click.stop
      />

      <div v-if="availableTags.length === 0" class="no-results">
        No tags found
      </div>

      <div v-else class="tags-dropdown-list">
        <button
          v-for="tag in availableTags"
          :key="tag.id"
          type="button"
          @click.stop="toggleTag(tag.id)"
          class="tag-option"
        >
          <span
            class="tag-color"
            :style="{ backgroundColor: tag.color }"
          ></span>
          <span>{{ tag.name }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tag-multiselect {
  position: relative;
  width: 100%;
}

.selected-tags {
  min-height: 42px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  transition: border-color 0.2s;
}

.selected-tags:hover {
  border-color: #10b981;
}

.placeholder {
  color: #9ca3af;
  font-size: 0.9rem;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  flex: 1;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  padding: 0;
  margin-left: 0.125rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.remove-btn:hover {
  opacity: 1;
}

.dropdown-icon {
  flex-shrink: 0;
  color: #6b7280;
  transition: transform 0.2s;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 250px;
  display: flex;
  flex-direction: column;
}

.search-input {
  padding: 0.5rem;
  border: none;
  border-bottom: 1px solid #e5e7eb;
  outline: none;
  font-size: 0.9rem;
}

.search-input:focus {
  border-bottom-color: #10b981;
}

.tags-dropdown-list {
  overflow-y: auto;
  max-height: 200px;
}

.tag-option {
  width: 100%;
  padding: 0.5rem;
  border: none;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-align: left;
  transition: background-color 0.2s;
}

.tag-option:hover {
  background-color: #f3f4f6;
}

.tag-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
}

.no-results {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.9rem;
}
</style>
