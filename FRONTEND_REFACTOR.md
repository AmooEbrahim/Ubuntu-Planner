# Frontend Refactor — Glassmorphism + Dark Mode

This is the **single source of truth** for the frontend visual refactor. Every phase and every subagent MUST follow it.

The goal is a modern, cohesive UI built around **Glassmorphism** (frosted-glass surfaces over a soft animated gradient background) with full **dark mode** support. Restraint over flash: subtle gradients, limited accent palette, no 3D objects, no rainbow colors.

---

## 1. Hard rules (read before touching anything)

1. **Do not change behavior.** Markup may be reorganized for layout, but every `v-if`, `v-for`, `@click`, `:value`, store call, prop, and emitted event must keep working. If you want to drop a `v-if`, ask first by leaving it in.
2. **Do not change routes, store APIs, or `services/api.js`.** Pure visual / presentational refactor.
3. **Do not add new dependencies** unless explicitly listed in section 8. The user agreed to library installs in principle but we want zero new deps if possible. If you think you truly need one, stop and surface it.
4. **Tailwind first.** Replace `<style scoped>` blocks with Tailwind utility classes wherever practical. Keep `<style scoped>` only for things Tailwind can't express (complex `@keyframes`, scoped pseudo-element tweaks). When you do keep scoped CSS, rewrite it to consume the design tokens (CSS variables) — never hardcode hex colors that already exist as a token.
5. **Dark mode is class-based** (`darkMode: 'class'` in tailwind.config.js). Always supply `dark:` variants for color, background, border, ring, and shadow. If you add a new token, add both `--xxx` (light) and `.dark --xxx` (dark) values in `main.css`.
6. **Accessibility:** every interactive element has visible `:focus-visible` ring (`focus-visible:ring-2 focus-visible:ring-accent/60`). Keep semantic elements (`<button>`, `<label>`, `<nav>`).
7. **No emojis** unless the original file already had them in user-visible copy (e.g. Dashboard greeting "👋"). Don't add new ones.
8. **Icons:** keep using inline SVGs already present in files. Do not introduce an icon library.
9. **i18n:** if a string is already in `src/lang/en.json`, keep using it. Don't move existing literal strings into i18n as part of this refactor — out of scope.
10. **Test before claiming done:** at minimum run `npm run build` from `frontend/` and confirm zero errors. If you broke a template, fix it.

---

## 2. Design tokens

All colors are CSS variables defined once in `src/assets/main.css` and consumed via Tailwind's arbitrary-value syntax (`bg-[hsl(var(--surface))]`) **or** via the named Tailwind colors we extend in `tailwind.config.js`. Prefer the named version (e.g. `bg-surface`, `text-fg`, `border-border`).

### 2.1 Palette (semantic)

| Token            | Light                          | Dark                              | Use                                           |
| ---------------- | ------------------------------ | --------------------------------- | --------------------------------------------- |
| `--bg`           | `#f4f6fb`                      | `#0b0d12`                         | Page body background base                     |
| `--bg-grad-1`    | `#dbeafe` (sky-200, alpha 0.7) | `#1e1b4b` (indigo-950, alpha 0.6) | Background blob 1                             |
| `--bg-grad-2`    | `#fae8ff` (fuchsia-100, 0.6)   | `#3b0764` (purple-950, 0.5)       | Background blob 2                             |
| `--bg-grad-3`    | `#cffafe` (cyan-100, 0.6)      | `#082f49` (sky-950, 0.55)         | Background blob 3                             |
| `--surface`      | `255 255 255 / 0.55`           | `20 22 30 / 0.55`                 | Glass card fill (rgba)                        |
| `--surface-2`    | `255 255 255 / 0.75`           | `28 30 40 / 0.7`                  | Modal / drawer fill (more opaque)             |
| `--surface-3`    | `255 255 255 / 0.35`           | `30 32 42 / 0.4`                  | Subtle inset / row hover                      |
| `--border`       | `255 255 255 / 0.6`            | `255 255 255 / 0.08`              | Glass border (top highlight)                  |
| `--border-soft`  | `15 23 42 / 0.08`              | `255 255 255 / 0.06`              | Divider lines inside cards                    |
| `--fg`           | `#0f172a` (slate-900)          | `#e6e8ee`                         | Primary text                                  |
| `--fg-muted`     | `#475569` (slate-600)          | `#9aa3b2`                         | Secondary text                                |
| `--fg-subtle`    | `#94a3b8` (slate-400)          | `#646b7a`                         | Tertiary / placeholder                        |
| `--accent`       | `#6366f1` (indigo-500)         | `#818cf8` (indigo-400)            | Primary action, links, active nav             |
| `--accent-hover` | `#4f46e5`                      | `#a5b4fc`                         | Hover                                         |
| `--success`      | `#10b981`                      | `#34d399`                         | Positive (running session, satisfaction high) |
| `--warning`      | `#f59e0b`                      | `#fbbf24`                         | Warnings, overtime                            |
| `--danger`       | `#ef4444`                      | `#f87171`                         | Destructive, errors                           |
| `--info`         | `#0ea5e9`                      | `#38bdf8`                         | Info badges                                   |

### 2.2 Radii / spacing / shadow

- Border radius: cards `rounded-2xl` (1rem), modals `rounded-3xl` (1.5rem), buttons `rounded-xl`, inputs `rounded-xl`, pills `rounded-full`.
- Glass shadow (light): `shadow-[0_8px_32px_rgba(15,23,42,0.08)]`. Dark: `dark:shadow-[0_8px_32px_rgba(0,0,0,0.45)]`.
- Standard transition: `transition-all duration-200 ease-out`.

### 2.3 Typography

- Font: **Inter** (loaded via Google Fonts in `index.html`), with system fallback. Already declared in `body { font-family }`.
- Page title: `text-2xl font-bold tracking-tight text-fg`.
- Section title: `text-base font-semibold text-fg`.
- Body: `text-sm text-fg`.
- Muted: `text-sm text-fg-muted`.

---

## 3. Reusable utility classes (defined in `main.css` `@layer components`)

These exist so subagents can write `class="glass-card"` instead of repeating 10 utilities. **Use them. Don't re-invent.**

| Class           | What it is                                                                                    |
| --------------- | --------------------------------------------------------------------------------------------- |
| `.glass-card`   | The frosted card. `bg-surface` + `backdrop-blur-xl` + border + shadow + rounded-2xl.          |
| `.glass-panel`  | More opaque variant for modals / drawers. Uses `--surface-2`.                                 |
| `.glass-inset`  | Subtle inset row (list items, hover row). Uses `--surface-3`.                                 |
| `.btn`          | Base button: padding, rounded-xl, font-medium, transition, focus ring.                        |
| `.btn-primary`  | Indigo gradient, white text, soft glow shadow.                                                |
| `.btn-secondary`| Glass border + transparent fill, fg text.                                                     |
| `.btn-ghost`    | No border, transparent, hover glass-inset.                                                    |
| `.btn-danger`   | Red gradient.                                                                                 |
| `.btn-success`  | Green gradient (used by "Start Session").                                                     |
| `.input`        | Glass input: `bg-surface-3 backdrop-blur` + border + focus ring + rounded-xl.                 |
| `.label`        | `text-xs font-medium text-fg-muted uppercase tracking-wide`.                                  |
| `.badge`        | `inline-flex px-2 py-0.5 rounded-full text-xs font-medium`. Combine with color modifiers.     |
| `.divider`      | `h-px bg-border-soft`.                                                                        |
| `.icon-btn`     | Square 36px button, rounded-xl, glass hover.                                                  |
| `.section-title`| `text-base font-semibold text-fg`.                                                            |
| `.page-title`   | `text-2xl font-bold tracking-tight text-fg`.                                                  |
| `.page-subtitle`| `text-sm text-fg-muted`.                                                                      |

---

## 4. Layout shell

`App.vue` uses a **left sidebar** layout instead of the current top nav, because there are 10 routes and a top bar runs out of room.

```
┌──────────────────────────────────────────────────────┐
│ [animated gradient blobs background]                 │
│  ┌────────────┐  ┌─────────────────────────────────┐ │
│  │  Sidebar   │  │  SessionBanner (when active)    │ │
│  │  (glass)   │  ├─────────────────────────────────┤ │
│  │            │  │                                 │ │
│  │  Logo      │  │  <RouterView/>                  │ │
│  │  Dashboard │  │  (page content)                 │ │
│  │  Projects  │  │                                 │ │
│  │  ...       │  │                                 │ │
│  │            │  │                                 │ │
│  │  ─────     │  │                                 │ │
│  │  Settings  │  │                                 │ │
│  │  Theme ☀️  │  │                                 │ │
│  └────────────┘  └─────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

- Sidebar width: `w-64` expanded, `w-16` collapsed (`@media (max-width: 1024px)` collapses to icons only).
- Active nav item: `bg-accent/10 text-accent border-l-2 border-accent` (or for icon-only mode, the whole pill is `bg-accent/15`).
- Theme toggle is a small icon button at the bottom of the sidebar above the AI/Settings group.
- SessionBanner remains pinned at top of the main column when an active session exists (don't move it into the sidebar).

---

## 5. Background

A single fixed-position gradient layer in `App.vue`:

```html
<div class="bg-blobs" aria-hidden="true">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>
</div>
```

Defined once in `main.css` — three soft blurred radial blobs at `position: fixed; inset: 0; z-index: -1; overflow: hidden`. Slow `transform` animation (60–80s) to feel alive. **No bouncy, no fast.** No 3D objects.

---

## 6. Dark mode

- Strategy: `darkMode: 'class'`. The `<html>` element gets `class="dark"` via the `useTheme` composable.
- Composable: `frontend/src/composables/useTheme.js` exposes `theme` (`'light' | 'dark' | 'system'`), `resolvedTheme`, `setTheme(t)`, `toggleTheme()`. Persists to `localStorage` under key `ub-theme`. Listens to `prefers-color-scheme` when `system`.
- Bootstrap: `index.html` includes a tiny inline script that sets `documentElement.classList` **before** Vue mounts, to avoid a flash. (Standard FOUC-free pattern.)
- Default for new users: `system`.
- The toggle in the sidebar cycles `light → dark → system → light`.

---

## 7. Component contracts (what each phase must preserve)

When a subagent edits a component, these external behaviors **must not change**:

- `App.vue`: same routes, same `RouterView`, same `Toaster`. New shell layout is fine. SessionBanner still rendered.
- `SessionBanner.vue`: keeps `useSessionStore`, all timers, `showReview`, `showNoteDialog`, all action handlers (`handleAddTime`, etc.). Just restyle.
- All forms (`PlanningForm`, `ProjectForm`, `TagForm`, `EditSessionDialog`, etc.): keep `defineEmits` signatures, validation logic, store calls.
- Modals: keep `Transition name="modal"` outer markup if removed elsewhere — check before deleting.
- `TagMultiSelect`, `TagSelector`, `ProjectTreeItem`: keep prop and emit contracts unchanged.
- `Chat.vue` and `chat/*`: streaming, tool-approval, and permissions logic must be untouched.

---

## 8. Allowed new dependencies

**Default: none.** If you really need one, the only pre-approved options are:

- `@tailwindcss/forms` (devDep) — only if necessary to normalize form-control styles. Confirm it's needed before installing.

Anything else — stop and ask.

---

## 9. Phase order (DO NOT parallelize)

Each phase is a separate subagent invocation in this order. The user explicitly asked for sequential, not parallel, because earlier phases set the design tokens and shared classes that later phases consume.

| # | Phase                  | Files                                                                                                                             |
| - | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Foundation             | `tailwind.config.js`, `src/assets/main.css`, `index.html`, new `src/composables/useTheme.js`, `App.vue`, `components/SessionBanner.vue` |
| 2 | Dashboard              | `views/Dashboard.vue`, `components/StartSessionDialog.vue`                                                                        |
| 3 | Projects               | `views/Projects.vue`, `components/ProjectForm.vue`, `ProjectTree.vue`, `ProjectTreeItem.vue`                                      |
| 4 | Tags                   | `views/Tags.vue`, `components/TagForm.vue`, `TagSelector.vue`, `TagMultiSelect.vue`                                               |
| 5 | Planning               | `views/Planning.vue`, `components/PlanningForm.vue`, `CalendarDay.vue`                                                            |
| 6 | Sessions               | `views/SessionsDaily.vue`, `Sessions.vue`, `SessionReview.vue`, `components/SessionCalendarDay.vue`, `SessionDetailsModal.vue`, `EditSessionDialog.vue`, `SessionReviewDialog.vue` |
| 7 | Statistics             | `views/Statistics.vue`                                                                                                            |
| 8 | Day Memory             | `views/DayMemory.vue`, `components/day-memory/*.vue`                                                                              |
| 9 | Chat                   | `views/Chat.vue`, `components/chat/*.vue`                                                                                         |
| 10| Settings + AI Settings | `views/Settings.vue`, `views/AISettings.vue`, `views/HomeView.vue`                                                                |
| 11| Build verify           | `npm run build`, fix any errors                                                                                                   |

---

## 10. Subagent briefing template

When dispatching a phase, the prompt MUST include:

1. Full path to this `FRONTEND_REFACTOR.md` (the agent must read it).
2. Exact list of files for the phase.
3. The hard rules from section 1 repeated.
4. Reminder: do not modify backend, stores, services, router, or any file outside the phase list.
5. Reminder: the foundation classes (`.glass-card`, `.btn-primary`, etc.) and Tailwind tokens (`bg-surface`, `text-fg`, `text-accent`, `border-border-soft`, `dark:` variants) already exist — use them, don't re-define.
6. Verify with `cd frontend && npm run build` at the end.

---

## 11. Acceptance for each phase

Before marking a phase complete:

- [ ] Every interactive control still calls the same store/method.
- [ ] Light + dark both render — verify by reading the JSX/template and confirming `dark:` variants exist for color-bearing classes.
- [ ] No raw hex colors in templates that already have a token (e.g. `#0f172a` → `text-fg`, `#6366f1` → `text-accent`). Hex values are still OK for *data* coloring (project color, tag color picked by the user).
- [ ] No `<style scoped>` block contains a duplicate of something already in the design tokens.
- [ ] `npm run build` succeeds.
