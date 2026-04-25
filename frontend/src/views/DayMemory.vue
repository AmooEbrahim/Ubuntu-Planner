<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
    <header class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="page-title">Day Memory</h1>
        <p class="page-subtitle">Reflect, record, and let the AI add its own observations.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="icon-btn"
          @click="shiftDate(-1)"
          aria-label="Previous day"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <input
          type="date"
          class="input text-sm py-1.5 w-auto"
          :value="currentDate"
          @input="onDateInput"
        />
        <button
          type="button"
          class="icon-btn"
          @click="shiftDate(1)"
          aria-label="Next day"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
        <button
          type="button"
          class="btn btn-primary btn-sm"
          @click="goToToday"
        >Today</button>
      </div>
    </header>

    <TabGroup :selected-index="selectedTab" @change="selectedTab = $event">
      <TabList class="glass-inset p-1 inline-flex gap-0.5 max-w-md w-full">
        <Tab v-slot="{ selected }" as="template">
          <button
            class="flex-1 rounded-lg py-2 text-sm font-semibold transition-all focus:outline-none"
            :class="selected ? 'bg-accent text-white shadow-sm shadow-accent/30' : 'text-fg-muted hover:text-fg'"
          >Your track</button>
        </Tab>
        <Tab v-slot="{ selected }" as="template">
          <button
            class="flex-1 rounded-lg py-2 text-sm font-semibold transition-all focus:outline-none"
            :class="selected ? 'bg-accent text-white shadow-sm shadow-accent/30' : 'text-fg-muted hover:text-fg'"
          >AI track</button>
        </Tab>
      </TabList>

      <TabPanels class="mt-5">
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

    <div v-if="loading" class="text-sm text-muted">Loading…</div>
    <div v-if="error" class="text-sm text-danger">{{ error }}</div>
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
