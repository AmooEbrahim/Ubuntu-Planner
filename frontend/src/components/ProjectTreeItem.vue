<script setup>
import { ref } from 'vue'

const props = defineProps({
  project: Object,
  depth: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['edit', 'delete', 'toggle-archive', 'toggle-pin', 'add-child', 'start-session'])

const expanded = ref(false)
const showMenu = ref(false)

function toggleExpand() {
  expanded.value = !expanded.value
}

function toggleMenu() {
  showMenu.value = !showMenu.value
}

function closeMenu() {
  showMenu.value = false
}
</script>

<template>
  <div :style="{ paddingLeft: `${depth * 1.5}rem` }">
    <div
      class="glass-card flex items-center justify-between gap-3 px-4 py-3 transition-all duration-200"
      :class="{ 'opacity-60': project.is_archived }"
    >
      <div class="flex items-center gap-3 flex-1 min-w-0">
        <button
          v-if="project.children && project.children.length > 0"
          @click="toggleExpand"
          class="flex items-center justify-center w-6 h-6 rounded-md text-fg-muted hover:bg-fg-subtle/15 transition-colors flex-shrink-0"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            width="16"
            height="16"
            class="transition-transform duration-200"
            :class="{ 'rotate-180': expanded }"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <span v-else class="w-6 h-6 flex-shrink-0"></span>

        <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: project.color }"></div>

        <div class="min-w-0 flex-1">
          <span class="text-sm font-medium text-fg">{{ project.name }}</span>
          <div class="flex gap-1.5 mt-1 flex-wrap">
            <span v-if="project.is_pinned" class="badge badge-warning" title="Pinned">
              <svg viewBox="0 0 24 24" fill="currentColor" width="10" height="10">
                <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
              </svg>
            </span>
            <span v-if="project.is_archived" class="badge badge-neutral">Archived</span>
            <span
              v-if="project.description"
              class="badge badge-neutral max-w-[200px] truncate"
              :title="project.description"
            >{{ project.description }}</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-shrink-0">
        <span class="badge badge-neutral">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          {{ project.default_duration }}m
        </span>

        <div class="flex items-center gap-0.5">
          <button
            @click="emit('start-session', project)"
            class="icon-btn !text-success hover:!bg-success/15"
            title="Start session"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
          </button>
          <button
            @click="emit('add-child', project)"
            class="icon-btn !text-info hover:!bg-info/15"
            title="Add sub-project"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>

          <div class="relative" v-click-outside="closeMenu">
            <button
              @click="toggleMenu"
              class="icon-btn"
              title="More actions"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                <circle cx="12" cy="5" r="2"></circle>
                <circle cx="12" cy="12" r="2"></circle>
                <circle cx="12" cy="19" r="2"></circle>
              </svg>
            </button>
            <Transition name="dropdown">
              <div
                v-if="showMenu"
                class="glass-card absolute top-[calc(100%+4px)] right-0 z-50 p-1.5 min-w-[160px]"
              >
                <button
                  @click="emit('edit', project); closeMenu()"
                  class="glass-row w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left text-fg"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                  Edit
                </button>
                <button
                  @click="emit('toggle-pin', project); closeMenu()"
                  class="glass-row w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left text-fg"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                  </svg>
                  {{ project.is_pinned ? 'Unpin' : 'Pin' }}
                </button>
                <button
                  @click="emit('toggle-archive', project); closeMenu()"
                  class="glass-row w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left text-fg"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <polyline points="21 8 21 21 3 21 3 8"></polyline>
                    <rect x="1" y="3" width="22" height="5"></rect>
                    <line x1="10" y1="12" x2="14" y2="12"></line>
                  </svg>
                  {{ project.is_archived ? 'Unarchive' : 'Archive' }}
                </button>
                <button
                  @click="emit('delete', project); closeMenu()"
                  class="glass-row w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left text-danger hover:!bg-danger/10"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                  Delete
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>

    <Transition name="children">
      <div
        v-if="expanded && project.children && project.children.length > 0"
        class="mt-2 ml-4 pl-3 border-l-2 border-fg-subtle/20 flex flex-col gap-2"
      >
        <ProjectTreeItem
          v-for="child in project.children"
          :key="child.id"
          :project="child"
          :depth="0"
          @edit="emit('edit', $event)"
          @delete="emit('delete', $event)"
          @toggle-archive="emit('toggle-archive', $event)"
          @toggle-pin="emit('toggle-pin', $event)"
          @add-child="emit('add-child', $event)"
          @start-session="emit('start-session', $event)"
        />
      </div>
    </Transition>
  </div>
</template>

<script>
export default {
  directives: {
    clickOutside: {
      mounted(el, binding) {
        el.clickOutsideEvent = (event) => {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value()
          }
        }
        document.addEventListener('click', el.clickOutsideEvent)
      },
      unmounted(el) {
        document.removeEventListener('click', el.clickOutsideEvent)
      }
    }
  }
}
</script>

<style scoped>
.children-enter-active,
.children-leave-active {
  transition: all 0.2s ease;
}
.children-enter-from,
.children-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
