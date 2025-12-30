<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTagStore } from '@/stores/tags'

const props = defineProps({
  projectId: Number,  // Project context for tag inheritance
  modelValue: {       // Selected tag IDs
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const tagStore = useTagStore()
const availableTags = ref([])
const searchQuery = ref('')
const loading = ref(false)

onMounted(async () => {
  await loadTags()
})

watch(() => props.projectId, async () => {
  await loadTags()
})

async function loadTags() {
  loading.value = true
  try {
    if (props.projectId) {
      availableTags.value = await tagStore.fetchTagsForProject(props.projectId)
    } else {
      await tagStore.fetchTags()
      availableTags.value = tagStore.globalTags
    }
  } finally {
    loading.value = false
  }
}

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
      placeholder="Search tags..."
      class="w-full px-3 py-2 border border-gray-300 rounded mb-3 focus:outline-none focus:ring-2 focus:ring-green-500"
    >

    <div v-if="loading" class="text-center text-gray-500 py-4">
      Loading tags...
    </div>

    <div v-else-if="filteredTags.length === 0" class="text-center text-gray-500 py-4">
      No tags found
    </div>

    <div v-else class="grid grid-cols-2 gap-2">
      <button
        v-for="tag in filteredTags"
        :key="tag.id"
        @click="toggleTag(tag.id)"
        :class="['px-3 py-2 rounded border-2 transition-all', {
          'border-opacity-100 text-white': isSelected(tag.id),
          'border-opacity-50 bg-white': !isSelected(tag.id)
        }]"
        :style="{
          backgroundColor: isSelected(tag.id) ? tag.color : 'white',
          borderColor: tag.color,
          color: isSelected(tag.id) ? 'white' : tag.color
        }"
        type="button"
      >
        {{ tag.name }}
      </button>
    </div>

    <div v-if="props.modelValue.length > 0" class="mt-3 text-sm text-gray-600">
      Selected: {{ props.modelValue.length }} tag(s)
    </div>
  </div>
</template>
