<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <header class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Day Memory</h1>
        <p class="text-sm text-gray-500 mt-1">Reflect, record, and let the AI add its own observations.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          @click="shiftDate(-1)"
          aria-label="Previous day"
        >‹</button>
        <input
          type="date"
          class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :value="currentDate"
          @input="onDateInput"
        />
        <button
          type="button"
          class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          @click="shiftDate(1)"
          aria-label="Next day"
        >›</button>
        <button
          type="button"
          class="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
          @click="goToToday"
        >Today</button>
      </div>
    </header>

    <TabGroup :selected-index="selectedTab" @change="selectedTab = $event">
      <TabList class="flex gap-1 rounded-lg bg-gray-100 p-1 mb-5 max-w-md">
        <Tab v-slot="{ selected }" as="template">
          <button
            class="flex-1 rounded-md py-2 text-sm font-medium transition focus:outline-none"
            :class="selected ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
          >Your track</button>
        </Tab>
        <Tab v-slot="{ selected }" as="template">
          <button
            class="flex-1 rounded-md py-2 text-sm font-medium transition focus:outline-none"
            :class="selected ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
          >AI track</button>
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel>
          <DayMemoryDayView
            :date="currentDate"
            track="user"
            :entry="pair?.user"
            :readonly="false"
          />
        </TabPanel>
        <TabPanel>
          <DayMemoryDayView
            :date="currentDate"
            track="ai"
            :entry="pair?.ai"
            :readonly="!aiEditOverride"
            @toggle-readonly="confirmAiEdit"
          />
        </TabPanel>
      </TabPanels>
    </TabGroup>

    <div v-if="loading" class="text-sm text-gray-500 mt-4">Loading…</div>
    <div v-if="error" class="text-sm text-red-600 mt-4">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { TabGroup, TabList, Tab, TabPanels, TabPanel } from '@headlessui/vue'
import DayMemoryDayView from '@/components/day-memory/DayMemoryDayView.vue'
import { useDayMemoryStore } from '@/stores/dayMemory'

const route = useRoute()
const router = useRouter()
const store = useDayMemoryStore()

const currentDate = ref(route.params.date || dayjs().format('YYYY-MM-DD'))
const selectedTab = ref(0)
const aiEditOverride = ref(false)

const pair = computed(() => store.pairFor(currentDate.value))
const loading = computed(() => store.isLoading(currentDate.value))
const error = computed(() => store.error)

const fetchCurrent = () => store.fetchDate(currentDate.value)

const shiftDate = (delta) => {
  currentDate.value = dayjs(currentDate.value).add(delta, 'day').format('YYYY-MM-DD')
}

const goToToday = () => {
  currentDate.value = dayjs().format('YYYY-MM-DD')
}

const onDateInput = (event) => {
  if (event.target.value) currentDate.value = event.target.value
}

const confirmAiEdit = () => {
  if (window.confirm('Editing the AI track manually will overwrite the AI\'s own notes. Continue?')) {
    aiEditOverride.value = true
  }
}

watch(
  currentDate,
  (next) => {
    aiEditOverride.value = false
    if (next && next !== route.params.date) {
      router.replace({ name: 'day-memory-date', params: { date: next } }).catch(() => {})
    }
    fetchCurrent()
  },
  { immediate: true },
)
</script>
