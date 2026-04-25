<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTagStore } from '@/stores/tags'

const props = defineProps({
  projectId: Number,
  modelValue: {
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
  if (index > -1) selected.splice(index, 1)
  else selected.push(tagId)
  emit('update:modelValue', selected)
}

function isSelected(tagId) {
  return props.modelValue.includes(tagId)
}
</script>

<template>
  <div>
    <input
      v-model="searchQuery"
      placeholder="Search tags..."
      class="input mb-3"
    >

    <div v-if="loading" class="text-center text-muted py-4 text-sm">
      Loading tags...
    </div>

    <div v-else-if="filteredTags.length === 0" class="text-center text-muted py-4 text-sm">
      No tags found
    </div>

    <div v-else class="grid grid-cols-2 gap-2">
      <button
        v-for="tag in filteredTags"
        :key="tag.id"
        @click="toggleTag(tag.id)"
        type="button"
        class="px-3 py-2 rounded-xl border-2 transition-all duration-150 text-sm font-medium text-left truncate"
        :style="{
          backgroundColor: isSelected(tag.id) ? tag.color : 'transparent',
          borderColor: tag.color + (isSelected(tag.id) ? '' : '80'),
          color: isSelected(tag.id) ? 'white' : tag.color
        }"
      >
        {{ tag.name }}
      </button>
    </div>

    <div v-if="props.modelValue.length > 0" class="mt-3 text-xs text-muted">
      Selected: {{ props.modelValue.length }} tag(s)
    </div>
  </div>
</template>
