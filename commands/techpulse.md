# /techpulse — Newsletter Digest

## Description
Read and summarize today's AI/tech newsletters from the narradar inbox.
Pulls unread items labeled "Newsletter", extracts the key highlights,
and presents a single scannable digest.

## Instructions

You are building a tech newsletter digest for Andy Braun. Follow these
steps in order.

### Step 1: Pull Unread Newsletters

Search Gmail on **ajbraun@narradar.com** for unread newsletters:

```
query: "label:Newsletter is:unread"
page_size: 25
```

If no unread newsletters, report that and stop.

### Step 2: Fetch Content

Use `get_gmail_messages_content_batch` with format `full` to pull the
body of each unread newsletter. Batch in groups of 25 if needed.

### Step 3: Extract Highlights

For each newsletter, extract:
- **Source** — which newsletter it came from
- **Top stories** — the 2-3 most important items or announcements
- **Key takeaway** — the "so what" in one sentence

Skip boilerplate (ads, footer links, subscription prompts, course promos).
Focus on substance: product launches, model releases, funding rounds,
regulatory news, research breakthroughs, strategic moves.

### Step 4: Present the Digest

Format as a single scannable briefing:

```
TECH PULSE — [Date]
[count] newsletters processed

HIGHLIGHTS

[Source Name]
- [Headline or key point]
- [Headline or key point]
> Takeaway: [one sentence]

[Source Name]
- [Headline or key point]
- [Headline or key point]
> Takeaway: [one sentence]

...

THEMES
Top patterns across today's newsletters:
1. [Theme — e.g., "Open-weight models closing the gap on proprietary"]
2. [Theme]
3. [Theme, if applicable]

ACTION ITEMS
- [Anything worth following up on, or "None — FYI only today"]
```

### Step 5: Mark as Read

After presenting the digest, ask:
"Mark all [count] newsletters as read?"

If Andy confirms, remove the UNREAD label from all processed messages
using `batch_modify_gmail_message_labels` with
`remove_label_ids: ["UNREAD"]`.

### Guidelines

- Keep the whole digest scannable — aim for 1-2 screens max.
- Prioritize signal over completeness. Skip filler content.
- If multiple newsletters cover the same story, consolidate — note it
  once and mention which sources covered it.
- The THEMES section is the high-leverage part — name the patterns.
- For ACTION ITEMS, only flag things that connect to Andy's goals or
  require a decision. Most days this will be "None."
- If a newsletter is just a promo/upsell with no real content, skip it
  entirely and note "[Source] — skipped (promo only)".
