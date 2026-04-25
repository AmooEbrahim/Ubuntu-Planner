<script setup>
import { computed, ref } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { Toaster } from 'vue-sonner'
import SessionBanner from '@/components/SessionBanner.vue'
import { useTheme } from '@/composables/useTheme'

const route = useRoute()
const { theme, resolvedTheme, cycleTheme } = useTheme()

const navItems = [
  { to: '/', label: 'Dashboard', icon: 'dashboard' },
  { to: '/projects', label: 'Projects', icon: 'folder' },
  { to: '/tags', label: 'Tags', icon: 'tag' },
  { to: '/planning', label: 'Planning', icon: 'calendar' },
  { to: '/sessions', label: 'Sessions', icon: 'clock' },
  { to: '/statistics', label: 'Statistics', icon: 'chart' },
  { to: '/day-memory', label: 'Day Memory', icon: 'book' },
]
const bottomNavItems = [
  { to: '/settings', label: 'Settings', icon: 'cog' },
]

const collapsed = ref(false)
function toggleCollapsed() { collapsed.value = !collapsed.value }

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path === to || route.path.startsWith(to + '/')
}

const themeLabel = computed(() =>
  theme.value === 'system' ? `Auto (${resolvedTheme.value})` : theme.value === 'dark' ? 'Dark' : 'Light'
)
</script>

<template>
  <div id="app" class="flex h-screen overflow-hidden text-fg">
    <!-- Animated background -->
    <div class="bg-blobs" aria-hidden="true">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <Toaster :position="'bottom-right'" :rich-colors="true" :close-button="true" :theme="resolvedTheme" />

    <!-- Sidebar -->
    <aside
      class="flex flex-col flex-shrink-0 m-3 mr-0 transition-[width] duration-200 ease-out glass-card overflow-hidden"
      :class="collapsed ? 'w-[72px]' : 'w-60'"
    >
      <!-- Brand -->
      <div class="flex items-center gap-3 px-4 py-5">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-accent-hover text-white shadow-lg shadow-accent/30 flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div v-if="!collapsed" class="min-w-0 flex-1">
          <div class="text-sm font-bold tracking-tight truncate">Ubuntu Planner</div>
          <div class="text-[11px] text-muted truncate">Plan · Track · Reflect</div>
        </div>
      </div>

      <div class="divider mx-3"></div>

      <!-- Primary nav -->
      <nav class="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150 relative',
            isActive(item.to)
              ? 'text-accent bg-accent/10 shadow-sm shadow-accent/10'
              : 'text-fg-muted hover:text-fg hover:bg-white/40 dark:hover:bg-white/5'
          ]"
          :title="collapsed ? item.label : null"
        >
          <span
            v-if="isActive(item.to)"
            class="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-1 rounded-r-full bg-accent"
            aria-hidden="true"
          ></span>
          <span class="flex items-center justify-center w-5 h-5 flex-shrink-0">
            <svg v-if="item.icon === 'dashboard'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <rect x="3" y="3" width="7" height="9" rx="1.5"></rect>
              <rect x="14" y="3" width="7" height="5" rx="1.5"></rect>
              <rect x="14" y="12" width="7" height="9" rx="1.5"></rect>
              <rect x="3" y="16" width="7" height="5" rx="1.5"></rect>
            </svg>
            <svg v-else-if="item.icon === 'folder'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"></path>
            </svg>
            <svg v-else-if="item.icon === 'tag'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
              <circle cx="7" cy="7" r="1.5"></circle>
            </svg>
            <svg v-else-if="item.icon === 'calendar'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <rect x="3" y="4" width="18" height="18" rx="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <svg v-else-if="item.icon === 'clock'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <svg v-else-if="item.icon === 'chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M3 3v18h18"></path>
              <path d="M7 14l4-4 4 4 5-7"></path>
            </svg>
            <svg v-else-if="item.icon === 'book'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
          </span>
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- AI Chat — special accent item -->
      <div class="px-2 pb-2">
        <RouterLink
          to="/chat"
          :class="[
            'group flex items-center gap-3 rounded-xl px-2.5 py-2 text-sm font-semibold transition-all duration-200 relative overflow-hidden',
            isActive('/chat')
              ? 'text-white'
              : 'text-fg hover:text-fg'
          ]"
          :style="isActive('/chat')
            ? 'background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);'
            : 'background: linear-gradient(135deg, rgb(168 85 247 / 0.12), rgb(var(--accent) / 0.12));'"
          :title="collapsed ? 'AI Chat' : null"
        >
          <span
            class="flex items-center justify-center w-7 h-7 rounded-lg text-white flex-shrink-0"
            style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 2px 8px rgba(168, 85, 247, 0.45);"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
              <path d="M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z"></path>
            </svg>
          </span>
          <span v-if="!collapsed" class="truncate">AI Chat</span>
          <span
            v-if="!collapsed && !isActive('/chat')"
            class="ml-auto text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-md text-white"
            style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent)));"
          >AI</span>
        </RouterLink>
      </div>

      <div class="divider mx-3"></div>

      <!-- Bottom nav + theme + collapse -->
      <div class="px-2 py-3 space-y-1">
        <RouterLink
          v-for="item in bottomNavItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150',
            isActive(item.to)
              ? 'text-accent bg-accent/10'
              : 'text-fg-muted hover:text-fg hover:bg-white/40 dark:hover:bg-white/5'
          ]"
          :title="collapsed ? item.label : null"
        >
          <span class="flex items-center justify-center w-5 h-5 flex-shrink-0">
            <svg v-if="item.icon === 'cog'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"></path>
            </svg>
          </span>
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>

        <button
          type="button"
          @click="cycleTheme"
          class="w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-fg-muted hover:text-fg hover:bg-white/40 dark:hover:bg-white/5 transition-all duration-150"
          :title="`Theme: ${themeLabel}`"
        >
          <span class="flex items-center justify-center w-5 h-5 flex-shrink-0">
            <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <circle cx="12" cy="12" r="4"></circle>
              <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path>
            </svg>
            <svg v-else-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <rect x="2" y="4" width="20" height="14" rx="2"></rect>
              <path d="M8 22h8M12 18v4"></path>
            </svg>
          </span>
          <span v-if="!collapsed" class="truncate">{{ themeLabel }}</span>
        </button>

        <button
          type="button"
          @click="toggleCollapsed"
          class="w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-fg-muted hover:text-fg hover:bg-white/40 dark:hover:bg-white/5 transition-all duration-150"
          :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        >
          <span class="flex items-center justify-center w-5 h-5 flex-shrink-0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18" :style="{ transform: collapsed ? 'rotate(180deg)' : 'none' }">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </span>
          <span v-if="!collapsed" class="truncate">Collapse</span>
        </button>
      </div>
    </aside>

    <!-- Main column -->
    <div class="flex-1 min-w-0 flex flex-col">
      <SessionBanner />
      <main class="flex-1 min-h-0 overflow-y-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>
