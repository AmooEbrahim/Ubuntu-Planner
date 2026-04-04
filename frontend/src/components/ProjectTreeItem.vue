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
  <div class="tree-item" :style="{ paddingLeft: `${depth * 1.5}rem` }">
    <div
      class="tree-row"
      :class="{ 'is-archived': project.is_archived, 'has-children': project.children && project.children.length > 0 }"
    >
      <div class="row-left">
        <button
          v-if="project.children && project.children.length > 0"
          @click="toggleExpand"
          class="expand-btn"
          :class="{ 'is-expanded': expanded }"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <span v-else class="expand-placeholder"></span>

        <div class="color-indicator" :style="{ backgroundColor: project.color }"></div>

        <div class="project-info">
          <span class="project-name">{{ project.name }}</span>
          <div class="project-badges">
            <span v-if="project.is_pinned" class="badge pinned" title="Pinned">
              <svg viewBox="0 0 24 24" fill="currentColor" width="10" height="10">
                <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
              </svg>
            </span>
            <span v-if="project.is_archived" class="badge archived">Archived</span>
            <span v-if="project.description" class="badge desc">{{ project.description }}</span>
          </div>
        </div>
      </div>

      <div class="row-right">
        <span class="duration-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          {{ project.default_duration }}m
        </span>

        <div class="row-actions">
          <button @click="emit('start-session', project)" class="icon-btn play" title="Start session">
            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
          </button>
          <button @click="emit('add-child', project)" class="icon-btn add" title="Add sub-project">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>

          <div class="dropdown" v-click-outside="closeMenu">
            <button @click="toggleMenu" class="icon-btn more" title="More actions">
              <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                <circle cx="12" cy="5" r="2"></circle>
                <circle cx="12" cy="12" r="2"></circle>
                <circle cx="12" cy="19" r="2"></circle>
              </svg>
            </button>
            <Transition name="dropdown">
              <div v-if="showMenu" class="dropdown-menu">
                <button @click="emit('edit', project); closeMenu()" class="dropdown-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                  Edit
                </button>
                <button @click="emit('toggle-pin', project); closeMenu()" class="dropdown-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                  </svg>
                  {{ project.is_pinned ? 'Unpin' : 'Pin' }}
                </button>
                <button @click="emit('toggle-archive', project); closeMenu()" class="dropdown-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <polyline points="21 8 21 21 3 21 3 8"></polyline>
                    <rect x="1" y="3" width="22" height="5"></rect>
                    <line x1="10" y1="12" x2="14" y2="12"></line>
                  </svg>
                  {{ project.is_archived ? 'Unarchive' : 'Archive' }}
                </button>
                <button @click="emit('delete', project); closeMenu()" class="dropdown-item danger">
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
      <div v-if="expanded && project.children && project.children.length > 0" class="children-container">
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
.tree-item {
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tree-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all var(--transition);
}

.tree-row:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.tree-row.is-archived {
  opacity: 0.6;
}

.row-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  transition: all var(--transition);
}

.expand-btn:hover {
  background: #f1f5f9;
}

.expand-btn.is-expanded svg {
  transform: rotate(180deg);
}

.expand-btn svg {
  transition: transform var(--transition);
}

.expand-placeholder {
  width: 24px;
  height: 24px;
}

.color-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-info {
  min-width: 0;
  flex: 1;
}

.project-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: #0f172a;
}

.project-badges {
  display: flex;
  gap: 0.375rem;
  margin-top: 0.25rem;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.7rem;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.badge.pinned {
  background: #fef3c7;
  color: #d97706;
}

.badge.archived {
  background: #f1f5f9;
  color: #64748b;
}

.badge.desc {
  background: #f1f5f9;
  color: #64748b;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.duration-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #64748b;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition);
}

.icon-btn.play {
  color: #059669;
}

.icon-btn.play:hover {
  background: #ecfdf5;
}

.icon-btn.add {
  color: #0ea5e9;
}

.icon-btn.add:hover {
  background: #f0f9ff;
}

.icon-btn.more {
  color: #94a3b8;
}

.icon-btn.more:hover {
  background: #f1f5f9;
  color: #64748b;
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.375rem;
  min-width: 160px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 50;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #334155;
  cursor: pointer;
  transition: all var(--transition);
  text-align: left;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.danger {
  color: #ef4444;
}

.dropdown-item.danger:hover {
  background: #fef2f2;
}

.children-container {
  margin-top: 0.5rem;
  margin-left: 1rem;
  padding-left: 0.75rem;
  border-left: 2px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

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
