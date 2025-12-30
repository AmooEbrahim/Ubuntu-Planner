# Projects

Project management system with hierarchical structure, archiving, and pinning.

## Overview

Projects are the core organizational unit. Users can:
- Create nested project hierarchies (unlimited depth)
- Archive projects instead of deleting them
- Pin favorite projects for quick access
- Set default session duration per project
- Customize notification intervals per project

## Project Attributes

### Required Fields
- **Name**: Project name (display)
- **Color**: Hex color code for visual identification

### Optional Fields
- **Parent**: Reference to parent project (allows nesting)
- **Description**: Detailed project description
- **Default Duration**: Default session length in minutes (default: 60)
- **Notification Interval**: How often to repeat notifications in minutes (NULL = use global default)

### System Fields
- **Archived**: Boolean flag (default: false)
- **Pinned**: Boolean flag (default: false)
- **Created At**: Auto-generated timestamp
- **Updated At**: Auto-updated timestamp

## Hierarchical Structure

### Nesting Rules
- Projects can have unlimited nesting depth
- Parent-child relationship via `parent_id`
- Circular references prevented by application logic
- Deleting parent: children's `parent_id` set to NULL

### Display Format
When showing a project in selection lists:
```
Root > Parent > Child
```

If only one parent: `Parent > Child`
If no parent: `Child`

## Project States

### Active
- Default state
- Shows in all selection lists
- Can be used for planning and execution

### Pinned
- Special highlight in UI
- Shows in quick-start menu
- Limited to 3-5 pinned projects in quick menu
- Can be both pinned and archived (though not recommended)

### Archived
- Hidden from selection lists by default
- Not deleted (data preserved)
- Can be un-archived anytime
- Planning and sessions remain intact
- Show in special "archived projects" view

## CRUD Operations

### Create
1. User fills form (name, color required)
2. Optionally selects parent project
3. Sets default duration
4. System validates and saves

### Read/List
**All Projects View:**
- Shows active projects by default
- Option to toggle archived projects
- Tree view showing hierarchy
- Color-coded for easy identification

**Quick Select (for starting sessions):**
- 3 pinned projects
- 2 recently used projects
- Search/browse all active projects

### Update
- All fields editable
- Changing parent: validate no circular reference
- Archive toggle: confirm if has active sessions
- Unpin automatically if archiving

### Delete
**Recommended: Archive instead of delete**

If user insists on deletion:
1. Check for existing planning and sessions
2. Show warning with counts
3. Options:
   - **Cancel**: Return without deleting
   - **Archive instead**: Recommended action
   - **Delete planning only**: Keep sessions, delete planning
   - **Delete all data**: Remove project, planning, and sessions

## Tag Inheritance

Projects inherit tags from parents:
- Project-specific tags usable by project and all children
- Global tags usable by all projects
- When selecting tags for a session:
  - Show global tags
  - Show project-specific tags
  - Show all parent project tags

Example:
```
Work (has tags: meeting, email)
  └─ Client A (has tags: review)
      └─ Project X (has tags: development)
```

When working on "Project X", available tags:
- Global tags
- development (own)
- review (parent: Client A)
- meeting, email (grandparent: Work)

## UI Components

### Project List View
- Tree structure with expand/collapse
- Color indicator per project
- Icons: 📌 (pinned), 📦 (archived)
- Quick actions: Edit, Archive/Unarchive, Delete

### Project Form
- Name input (required)
- Color picker (required)
- Parent selector (dropdown with tree view)
- Description textarea
- Default duration (number input, minutes)
- Notification interval (number input, minutes, or "use default")
- Checkboxes: Pin, Archive

### Quick Select Menu
**Pinned Projects** (max 5):
- Large, colorful buttons
- One-click to start session

**Recent Projects** (2-3):
- Smaller buttons below pinned
- Based on recent session history

**Search/Browse**:
- Search input
- Filtered list of active projects
- Tree view for browsing

## Business Logic

### Default Duration
- Used when starting a session without planning
- Can be overridden when starting session
- Typical values: 30, 60, 90, 120 minutes

### Notification Interval
- How often to repeat notifications after time expires
- Project-specific overrides global default (10 minutes)
- Use cases:
  - Quick tasks: 2-5 minutes
  - Focus work: 10-15 minutes
  - Long sessions: 20-30 minutes

### Pinning Strategy
- Limit to 3-5 pinned projects for UI clarity
- If pinning 6th project, show warning
- Suggest unpinning least-used pinned project

### Archiving Strategy
- Preferred over deletion
- Preserves historical data
- Can be filtered out of views
- Easy to unarchive if needed

## API Endpoints

```
GET    /api/projects              # List all projects
GET    /api/projects?archived=true  # Include archived
GET    /api/projects/pinned       # Get pinned projects
GET    /api/projects/recent       # Get recently used projects
GET    /api/projects/:id          # Get single project
POST   /api/projects              # Create project
PUT    /api/projects/:id          # Update project
DELETE /api/projects/:id          # Delete project
PATCH  /api/projects/:id/archive  # Toggle archive status
PATCH  /api/projects/:id/pin      # Toggle pin status
```

## Validation Rules

1. **Name**: Required, 1-255 characters
2. **Color**: Required, valid hex color (#RRGGBB)
3. **Parent**: Must be valid project ID or NULL
4. **Circular Reference**: Parent cannot be self or descendant
5. **Default Duration**: Positive integer (suggested: 5-480 minutes)
6. **Notification Interval**: Positive integer or NULL (suggested: 1-60 minutes)
