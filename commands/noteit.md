# /noteit — Save a Note from Recent Work

## Description
Captures research, analysis, or output from the current session into a
structured note file in `Notes/active/`. Move to `Notes/complete/` when done.

## Arguments
- `{topic}` — The subject of the note (e.g., "sce pike call prep", "narradar tax deadlines")

## Instructions

### Step 1: Clarify if needed

If `{topic}` is ambiguous or could match multiple things discussed in the session,
ask ONE clarifying question before proceeding. Examples:
- "Do you mean the LinkedIn mutual connections research or the full call prep?"
- "Is this about the NDA status or the investor message?"

If the topic is clear, skip this step.

### Step 2: Determine filename

Convert `{topic}` to a slug:
- Lowercase
- Replace spaces with hyphens
- Strip special characters
- Example: "Sce Pike call prep" → `sce-pike-call-prep.md`

### Step 3: Compile the note

Pull together all relevant content from the current session on `{topic}`:
- Research findings
- Key facts, names, dates, links
- Recommendations or next steps
- Any context needed to make the note useful standalone

Structure the note clearly with headers. Include a date at the top.

### Step 4: Write the file

Save to: `./Notes/active/{slug}.md`

If a file with that name already exists, surface the conflict:
"A note named `{slug}.md` already exists. Overwrite, append, or use a new name?"

### Step 5: Confirm

Report: "Saved to Notes/active/{filename}.md"
