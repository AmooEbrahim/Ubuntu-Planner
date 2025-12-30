# Tags

Tag system supporting both global and project-specific tags with inheritance.

## Overview

Tags help categorize and filter planning and execution sessions. The tag system supports:
- **Global tags**: Usable by all projects
- **Project-specific tags**: Usable by a project and its children
- **Tag inheritance**: Children inherit parent project tags
- **Color coding**: Visual identification

## Tag Types

### Global Tags
- `project_id = NULL`
- Available to all projects
- Examples: urgent, quick-win, blocked, waiting

### Project-Specific Tags
- `project_id = <project_id>`
- Available to:
  - The project itself
  - All descendant projects (children, grandchildren, etc.)
- Examples:
  - For "Work": meeting, email, planning
  - For "Personal": exercise, reading, learning

## Tag Attributes

### Required Fields
- **Name**: Tag name (unique per project scope)
- **Color**: Hex color code for visual distinction

### Optional Fields
- **Project**: Reference to project (NULL = global)

### System Fields
- **Created At**: Auto-generated timestamp
- **Updated At**: Auto-updated timestamp

## Tag Inheritance

Tags follow project hierarchy:

```
Global Tags: urgent, blocked

Work (tags: meeting, email)
├─ Client A (tags: review, testing)
│   └─ Project X (tags: development, deployment)
└─ Client B (tags: research)
```

**Available tags per project:**
- **Work**: Global + meeting, email
- **Client A**: Global + meeting, email, review, testing
- **Project X**: Global + meeting, email, review, testing, development, deployment
- **Client B**: Global + meeting, email, research

## CRUD Operations

### Create
1. User enters tag name
2. Selects color
3. Optionally selects project (NULL = global)
4. System validates uniqueness within scope
5. Tag created

### Read/List
**All Tags View:**
- Grouped by type (global vs project-specific)
- Shows associated project for project-specific tags
- Color-coded
- Sortable by name, project, usage count

**Tag Selector (when adding to session/planning):**
- Shows available tags for current project:
  - Global tags
  - Current project tags
  - All ancestor project tags
- Grouped and labeled by source
- Color-coded for easy selection

### Update
User can change:
- Tag name (must remain unique in scope)
- Tag color
- Associated project (**with validation**)

**Changing Project Association:**

This is complex because existing sessions/planning may use the tag.

**Scenarios:**

1. **Global → Project-Specific**
   - Find all sessions/planning using this tag
   - Check if they belong to the new project or its descendants
   - If not compatible:
     - **Option A**: Remove tag from incompatible sessions
     - **Option B**: Create new project-specific tag and migrate compatible sessions

2. **Project-Specific → Global**
   - Generally safe (expands availability)
   - No data migration needed

3. **Project A → Project B**
   - Find all sessions/planning using this tag
   - Check if they belong to Project B or its descendants
   - If not compatible:
     - **Option A**: Remove tag from incompatible sessions
     - **Option B**: Keep tag on Project A, create new tag for Project B

**UI Flow for Project Change:**
```
1. User changes project association
2. System checks for affected sessions/planning
3. If conflicts found:
   - Show count of affected items
   - Present options:
     a) Cancel (keep current association)
     b) Remove tag from incompatible items
     c) Create new tag with new association and migrate compatible items
4. User chooses option
5. System executes and shows result
```

### Delete
1. Check if tag is used in any planning or sessions
2. Show count of usages
3. Confirm deletion
4. Options:
   - **Cancel**: Return without deleting
   - **Delete and remove from all**: Delete tag and remove from all planning/sessions
   - **Keep in existing items**: Delete tag but keep in existing data (orphaned references)

Recommendation: Option 2 (remove from all) is cleanest.

## Tag Usage

### In Planning
- User can add multiple tags when creating/editing planning
- Tags help categorize scheduled work
- Used for filtering and reporting

### In Sessions
- User can add multiple tags during or after session
- Tags added during review phase
- Can add new tags on-the-fly (they're created automatically)

**Auto-creating tags:**
When user types a tag name that doesn't exist:
1. Check if it matches existing tag (case-insensitive)
2. If not found, create new tag:
   - Default color (or pick from palette)
   - Associated with current project (or global if user specifies)
3. Add to session/planning

## UI Components

### Tag Management Page
**List View:**
- Table or card view of all tags
- Columns: Name, Color, Project/Global, Usage Count
- Filter by: Global/Project-specific, Project
- Sort by: Name, Usage, Created date

**Tag Form:**
- Name input (required)
- Color picker (required)
- Project selector (dropdown with "Global" option)
- Preview of tag appearance

### Tag Selector Component
Used when adding tags to sessions/planning:

**Layout:**
```
[Search/Create: ____________]

Pinned/Frequent:
[tag1] [tag2] [tag3]

Global:
[urgent] [blocked] [quick-win]

Current Project (Project X):
[development] [deployment]

Parent Projects:
From Client A: [review] [testing]
From Work: [meeting] [email]
```

**Features:**
- Type to search existing tags
- Type to create new tag (if not found)
- Click to add/remove
- Visual indicator of selected tags
- Color-coded for easy identification

### Tag Display
**In Lists:**
```
Session #123: Project X
[development] [testing] [urgent]
Duration: 90 minutes
```

**In Cards:**
Small colored badges with tag names

## Business Logic

### Uniqueness Rules
- Global tags: Name must be unique among all global tags
- Project tags: Name must be unique within project scope
- Same name can exist as both global and project-specific

Examples:
- ✅ Global "urgent" + Project A "urgent" (different scopes)
- ❌ Two global "urgent" tags
- ❌ Project A has two "urgent" tags

### Availability Rules
When selecting tags for a session on "Project X":
```python
available_tags = (
    global_tags +
    project_x_tags +
    all_ancestor_tags(project_x)
)
```

### Color Recommendations
Provide a default color palette:
- 🔴 Red: urgent, blocked, critical
- 🟢 Green: completed, approved, success
- 🔵 Blue: planning, research, documentation
- 🟡 Yellow: waiting, review, in-progress
- 🟣 Purple: personal, learning, training
- 🟠 Orange: meeting, communication

## Filtering and Search

### Filter Sessions/Planning by Tags
- **Any (OR)**: Show items with any of selected tags
- **All (AND)**: Show items with all selected tags
- **None**: Show items without specified tags

### Tag Statistics
Show insights:
- Most used tags (overall, per project)
- Tag usage trends over time
- Tag combinations (which tags often used together)

## API Endpoints

```
GET    /api/tags                  # List all tags
GET    /api/tags?project_id=X     # Tags for project X (including inherited)
GET    /api/tags/global           # Global tags only
GET    /api/tags/:id              # Get single tag
POST   /api/tags                  # Create tag
PUT    /api/tags/:id              # Update tag (with validation)
DELETE /api/tags/:id              # Delete tag
GET    /api/tags/stats            # Tag usage statistics
```

## Validation Rules

1. **Name**: Required, 1-100 characters
2. **Color**: Required, valid hex color (#RRGGBB)
3. **Project**: Must be valid project ID or NULL
4. **Uniqueness**: Name unique within scope (global or project)
5. **Project Change**: Validate compatibility with existing usage

## Migration Scenarios

### Scenario 1: Convert Global to Project-Specific
User wants to convert global "meeting" tag to "Work" project tag.

**Process:**
1. Find all sessions/planning with "meeting" tag
2. Identify which are under "Work" hierarchy
3. Compatible: 50 items, Incompatible: 5 items
4. Show user:
   ```
   This tag is used in 55 items.
   - 50 items are under "Work" hierarchy (compatible)
   - 5 items are from other projects (incompatible)

   Options:
   • Cancel
   • Remove from incompatible items (5 sessions)
   • Keep global tag, create new "Work" tag
   ```
5. Execute based on user choice

### Scenario 2: Merge Tags
User realizes they have duplicate tags: global "urgent" and Project A "urgent".

**Process:**
1. Select tags to merge
2. Choose primary tag (keep) and secondary tag (delete)
3. Migrate all uses of secondary to primary
4. Delete secondary tag

## Future Enhancements

- Tag aliases (multiple names for same tag)
- Tag hierarchies (parent-child tag relationships)
- Smart tag suggestions based on project/time/context
- Tag templates for common workflows
