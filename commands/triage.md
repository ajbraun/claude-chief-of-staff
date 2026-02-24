# /triage — Inbox Triage

## Description
Scan all connected communication channels, prioritize items by urgency,
and draft responses in your voice. Clear your inbox in minutes.

## Arguments
- `quick` — Tier 1 items only, no drafts (fastest)
- `digest` — Full scan with summaries, drafts for Tier 1-2
- (no argument) — Full scan with drafts for everything actionable

## Instructions

You are running inbox triage for {{YOUR_NAME}}. The goal is to process
all incoming messages quickly and surface what needs attention.

### Step 0: Verify Time, Context, and Load Filters

Get the current time so you know what "today" and "recent" mean.
Check the calendar briefly to understand where the user is in their day.

**Before scanning anything**, read `~/.claude/triage-blacklist.yaml` and hold
it in memory. All scan steps MUST filter against this blacklist. If the file
doesn't exist, proceed without filtering.

### Step 1: Scan Channels

Scan each connected channel. Only scan channels with active MCP servers.
Report progress as you go.

**Channels to scan (in order):**

1. **Work Email — ajbraun@narradar.com** — Search for recent unread/unreplied emails
   - Query: Messages from the last 24 hours (or since last triage)
   - Filter out senders/lists in `~/.claude/triage-blacklist.yaml` (`gmail_skip`)
   - Focus on: Direct emails (not newsletters, automated, or CC-only)
   - Note: narradar.com does NOT have Gmail tab filtering (no categories)

2. **Work Email — andy@layrdata.com** — Same approach
   - Focus on: Layr-related business, prospects, internal comms

3. **Personal Email — ajbraun@gmail.com** — Same approach
   - Query: `is:inbox category:primary` (Primary tab only)
   - Focus on: Anything from key contacts or family

3. **Slack** — Check DMs and mentions
   - Query: Recent DMs and @mentions
   - Skip: Channel chatter unless directly relevant

4. **WhatsApp** — If connected, check recent messages
   - Focus on: Direct messages requiring response

5. **iMessage** (via `imsg` CLI, macOS only)
   - Run `imsg chats --limit 20 --json` to get recent active chats
   - Filter out blacklisted chats (see `~/.claude/triage-blacklist.yaml`)
   - Also skip short-code / automated SMS (identifiers with 5-6 digits)
   - For each remaining chat with recent activity, run:
     `imsg history --chat-id {ID} --limit 5 --json`
   - Focus on: Messages where `is_from_me: false` with no subsequent
     `is_from_me: true` reply (i.e., unreplied messages from contacts)
   - Cross-reference phone numbers against `~/.claude/contacts/` for names

### Step 2: Classify Each Item

For each item found, assign a triage tier:

| Tier | Criteria | Action |
|------|----------|--------|
| **Tier 1** | From key contacts, time-sensitive, blocking someone, or explicit urgency | Respond NOW |
| **Tier 2** | Important but not urgent, requires thoughtful response, due today | Handle today |
| **Tier 3** | FYI, newsletters, automated notifications, low-stakes | Archive or brief ack |

**Tier assignment factors:**
- Who sent it? (Key contacts and leadership = higher tier)
- Is someone blocked waiting for a response?
- Is there a deadline mentioned?
- Has it been waiting a long time? (Older = higher urgency)
- Does it align with active goals?

### Step 3: Verify Not Already Handled (ALL Channels)

**This is a mandatory gate.** No item moves to drafting without passing BOTH checks.

**Check A — Same-channel reply:**
- Check sent mail for responses to the same thread
- Check if the contact file shows a more recent interaction
- If already replied in the same thread, skip it entirely

**Check B — Cross-channel verification:**
- Run `/channelcheck` against ALL Tier 1 and Tier 2 items that passed Check A
- This checks iMessage, Slack, and other connected channels for evidence the
  item was already addressed on a different channel
- If channelcheck finds recent activity with the sender, mark as "likely handled"
  and skip — do NOT draft a response

**An item is only actionable if it passes both checks.** Communication is
multi-channel. An email with no email reply may have been handled via text,
iMessage, Slack, or in person.

### Step 4: Draft Responses

For each actionable item (Tier 1 and Tier 2), draft a response that:
- Matches the user's writing style (reference CLAUDE.md Part 4)
- Is send-ready (not a starting point for editing)
- Is appropriately concise for the context
- Includes specific scheduling proposals if timing is involved (verify calendar first)

For `quick` mode: Skip drafts, just list Tier 1 items.
For `digest` mode: Include drafts for Tier 1, summaries for Tier 2.

### Step 5: Present Results

Format output as:

```
Scanned: [channels] ([counts])

TIER 1 — Respond Now
1. [Sender] — [Subject/summary] ([channel], [wait time])
   Draft: "[proposed response]"

2. ...

TIER 2 — Handle Today
3. [Sender] — [Subject/summary] ([channel])
   Draft: "[proposed response]"

4. ...

TIER 3 — FYI
5-N. [Brief list, auto-archived if possible]

SUMMARY: [X] items need action, [Y] drafts ready to send.
```

### Step 6: Save the Triage Log

After presenting results, write the full triage output to:
`~/SideProjects/claude-chief-of-staff/Notes/Dailies/{YYYY-MM-DD}-triage.md`

Include the date/time as an H1 header. Append if a file for today already exists
(you may have run triage multiple times). This creates a searchable daily log.

### Step 7: Await Approval

**NEVER send any message without explicit approval.**

After presenting drafts, wait for the user to:
- Say "Send" or "Y" to approve a specific draft
- Say "Send all" to approve all drafts
- Edit a draft and then approve
- Skip items

### Guidelines

- Speed matters. A triage should take 2-3 minutes, not 10.
- Don't over-explain. The user knows their contacts — just surface what's important.
- If a channel's MCP server or CLI tool isn't available, skip it silently.
- For iMessage, always check `~/.claude/triage-blacklist.yaml` before scanning chats.
- Track what was surfaced to avoid re-surfacing in the next triage run.
- If you find nothing urgent, say so clearly: "Inbox clear. No items need immediate attention."
- For long email threads, summarize the thread — don't just quote the last message.
