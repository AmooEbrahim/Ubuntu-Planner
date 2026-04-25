<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
const rootRef = ref(null)

onMounted(async () => {
  if (tagStore.tags.length === 0) {
    await tagStore.fetchTags()
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
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
  if (index > -1) current.splice(index, 1)
  else current.push(tagId)
  emit('update:modelValue', current)
  searchQuery.value = ''
}

function removeTag(tagId) {
  const current = props.modelValue.filter(id => id !== tagId)
  emit('update:modelValue', current)
}

function handleClickOutside(event) {
  if (rootRef.value && !rootRef.value.contains(event.target)) {
    isOpen.value = false
  }
}
</script>

<template>
  <div ref="rootRef" class="relative w-full">
    <!-- Trigger / selected tags -->
    <div
      class="input min-h-[42px] flex items-center justify-between gap-2 cursor-pointer py-1.5"
      @click="isOpen = !isOpen"
    >
      <div v-if="selectedTags.length === 0" class="text-subtle text-sm">
        Select tags...
      </div>
      <div v-else class="flex flex-wrap gap-1.5 flex-1">
        <span
          v-for="tag in selectedTags"
          :key="tag.id"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold border"
          :style="{
            backgroundColor: tag.color + '20',
            borderColor: tag.color + '60',
            color: tag.color
          }"
        >
          {{ tag.name }}
          <button
            type="button"
            @click.stop="removeTag(tag.id)"
            class="opacity-70 hover:opacity-100 ml-0.5 leading-none text-base"
            aria-label="Remove tag"
          >×</button>
        </span>
      </div>
      <svg
        class="flex-shrink-0 text-fg-subtle transition-transform duration-200"
        :class="{ 'rotate-180': isOpen }"
        viewBox="0 0 20 20"
        fill="currentColor"
        width="16"
        height="16"
      >
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </div>

    <!-- Dropdown -->
    <div
      v-if="isOpen"
      class="glass-panel absolute top-full left-0 right-0 mt-1 z-50 max-h-64 flex flex-col overflow-hidden"
    >
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search tags..."
        class="w-full px-3 py-2 bg-transparent border-b border-fg-subtle/15 text-sm text-fg placeholder:text-fg-subtle focus:outline-none"
        @click.stop
      />

      <div v-if="availableTags.length === 0" class="p-4 text-center text-sm text-muted">
        No tags found
      </div>

      <div v-else class="overflow-y-auto max-h-52">
        <button
          v-for="tag in availableTags"
          :key="tag.id"
          type="button"
          @click.stop="toggleTag(tag.id)"
          class="w-full px-3 py-2 flex items-center gap-2 text-sm text-fg text-left hover:bg-fg-subtle/10 transition-colors"
        >
          <span
            class="inline-block w-3.5 h-3.5 rounded flex-shrink-0"
            :style="{ backgroundColor: tag.color }"
          ></span>
          <span class="truncate">{{ tag.name }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
