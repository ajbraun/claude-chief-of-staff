# /channelcheck — Cross-Channel Verification

## Description
Second-pass filter for triage results. Checks whether flagged items have
already been handled on a different channel (iMessage, Slack, in-person
inference). Downgrades items that show cross-channel activity.

## When to Use
Called automatically by `/triage` after initial classification, or manually
when reviewing whether something has already been addressed.

## Arguments
- (none) — Runs against the current triage results in context

## Instructions

You are running cross-channel verification. Triage has already identified
items that appear to need a response. Your job is to check whether those
items were actually handled on a different channel.

### Step 1: Build the Check List

From triage output, collect every Tier 1 and Tier 2 item where the user
has NOT replied on the same channel (e.g., email flagged with no sent reply).

For each item, note:
- **Sender name and identifiers** (email, phone number if known)
- **Timestamp** of the inbound message
- **Channel** it arrived on

### Step 2: Query Connected Channels

For each flagged item, check for **any interaction with that sender** on
**any other connected channel** after the inbound message timestamp.

#### iMessage (via imsg CLI)
Use the `imsg` CLI tool (`brew install steipete/tap/imsg`) to check message history.

**Lookup priority (fastest to slowest):**

1. **Chat ID from contact file (preferred):** Check `~/.claude/contacts/{name}.md`
   for an `iMessage Chat ID` field. If present, use it directly — no searching needed:
   ```bash
   imsg history --chat-id {CHAT_ID} --after "{INBOUND_TIMESTAMP}" --limit 10 --json
   ```

2. **Phone number from contact file:** If no Chat ID but phone is known:
   ```bash
   imsg history --participant "{PHONE}" --after "{INBOUND_TIMESTAMP}" --limit 10 --json
   ```

3. **Search by name (last resort):** Only if neither Chat ID nor phone is available:
   ```bash
   imsg chats --limit 50 --json | grep -i "{SENDER_NAME}"
   ```
   Then use the found chat ID for history lookup.

**Always use Chat ID when available.** It's a direct lookup with zero ambiguity.
Name-based searching is unreliable — many chats display as phone numbers only.

**What counts as "handled":**
- Any message with `is_from_me: true` after the email arrived
- Any message with `is_from_me: false` that references the same topic —
  suggests an active conversation moved channels

#### Slack (if MCP connected)
- Check DMs with the same person after the inbound timestamp
- Check for @mentions or thread replies involving them

#### WhatsApp (if MCP connected)
- Same approach as iMessage — check for recent messages with that contact

### Step 3: Classify Cross-Channel Status

For each checked item, assign one of:

| Status | Meaning | Triage Effect |
|--------|---------|---------------|
| **Handled** | You sent a message on another channel after the email | Downgrade to Tier 3, mark "handled via [channel]" |
| **Likely handled** | Active conversation on another channel around same time, but can't confirm topic match | Keep tier but add note: "likely handled via [channel]" |
| **Not handled** | No cross-channel activity found | Keep original tier, no change |

### Step 4: Return Updated Triage

Output the revised triage list with cross-channel annotations:

```
CHANNELCHECK RESULTS:

1. [Sender] — [Subject] — HANDLED via iMessage (you texted at 2:15 PM)
2. [Sender] — [Subject] — LIKELY HANDLED (iMessage activity 30min after email)
3. [Sender] — [Subject] — NOT HANDLED (no cross-channel activity)

Revised action items: [X] (down from [Y])
```

### Step 5: Contact File Updates

If you discover a contact's phone number or iMessage handle during lookup,
offer to save it to their contact file in `~/.claude/contacts/` for future
triage runs. This makes subsequent channelchecks faster and more accurate.

If a contact has a phone number but no `iMessage Chat ID`, and you successfully
find their chat during this run, add the Chat ID to their contact file
immediately — don't wait to be asked. This is a one-time cost that speeds up
every future triage.

### Guidelines

- Speed matters. This should add seconds, not minutes.
- When in doubt, mark "likely handled" — don't suppress items you're unsure about.
- If no connected channels have data for a sender, skip silently — don't flag it as a gap.
- Phone number matching is fuzzy — strip formatting, match last 10 digits.
- If `imsg` is not installed or errors, note it once and skip iMessage checks.
