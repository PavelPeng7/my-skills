---
name: card-note
description: Turn raw ideas, highlights, reading excerpts, fleeting notes, and Obsidian/Zettelkasten note requests into atomic card notes that are written in the user's own words, connected to nearby notes, and saved in a reusable Markdown structure. Use this whenever the user asks to make a permanent note, evergreen note, literature note, slip-box note, card note, atomic note, or wants to turn scattered note material into one clear Obsidian note.
---

# Card Note

Use this skill to convert rough note input into a durable card note instead of a pasted archive.

The goal is not to "store more text." The goal is to help the user produce one clear idea per note, expressed in their own words, with meaningful links to related notes.

## When to use

Use this skill when the user:

- wants a card note, permanent note, evergreen note, or Zettelkasten note
- shares a highlight, excerpt, reading note, or copied passage and wants it turned into a note
- asks to organize a fleeting idea into a note worth keeping
- wants help connecting a new note to an existing Obsidian vault
- asks for a note template that supports atomic thinking and bidirectional links

## Core rules

1. Write one core idea per note.
2. Prefer paraphrase over copy-paste.
3. Use complete sentences for the main claim.
4. Add links only when the relationship is meaningful.
5. Keep the note useful on its own, even when opened months later.

## Workflow

### 1. Classify the input

Decide which case applies:

- `raw excerpt`: copied paragraph, quote, web snippet, book highlight
- `fleeting thought`: short idea, question, intuition, observation
- `half-formed note`: rough bullets that already point to one idea
- `existing card rewrite`: user wants to polish or split a note

### 2. Refuse passive storage

If the input is mostly copied text, do not directly turn the pasted text into the final note body.

First extract or ask for:

- the user's own paraphrase of the core point
- the source
- why this idea matters

If the user already gave enough explanation in their own words, proceed without asking.

### 3. Enforce atomicity

Check whether the content contains one idea or several.

Signals that the note should be split:

- it makes multiple unrelated claims
- it mixes summary, critique, and action plan without a single center
- the title would need "and" to stay accurate

If splitting is needed, produce:

- `primary card`: the strongest single idea
- `split candidates`: 1-3 follow-up card titles

### 4. Search for nearby notes before writing

When working inside a vault or note workspace, look for related notes before finalizing the new one.

Practical search method:

- extract 2-5 keywords from the new idea
- use local filename/content search to find overlapping concepts
- keep only notes with a clear relationship: support, contrast, example, extension, prerequisite

Do not add links just because the same word appears.

### 5. Write the card

Use the template below unless the user already has a stricter house style.

## Default card-note template

````markdown
# <Card Title>

## Core Idea
<One clear claim in the user's own words. 2-4 sentences.>

## Why It Matters
<Why this idea changes understanding, decision-making, or behavior. 1-3 sentences.>

## Evidence or Source
- Source: <book / article / video / conversation / personal observation>
- Context: <where this idea came from>
- Optional quote: > <short quote only if it adds precision>

## Related Notes
- [[Related Note A]] - <support / contrast / extension / example>
- [[Related Note B]] - <support / contrast / extension / example>

## Open Questions
- <question worth exploring next>
````

## Output rules

- Prefer concrete titles over vague titles.
- Titles should name the idea, not the capture event.
- Keep `Core Idea` self-contained and readable without the source.
- Keep quotes short and secondary.
- Add `Related Notes` only when you can state the reason for the link.
- If no real link exists yet, write `- None yet.` instead of inventing one.

## Title heuristics

Good titles usually:

- make a claim
- name a tension or distinction
- stay short enough to scan in a graph or sidebar

Prefer:

- `Feedback loses value when it arrives after the decision point`
- `A checklist reduces recall load but not judgment load`

Avoid:

- `Random Thought`
- `Notes from Article`
- `About productivity and systems`

## Literature-note handling

If the user starts from reading material, produce two layers when useful:

1. `literature note`: brief source-grounded summary in the user's words
2. `card note`: one atomic idea worth keeping independently

Do not collapse an entire chapter into one permanent note unless the user explicitly wants a broad summary.

## Linking heuristics

When suggesting or writing links, label the relationship in plain language:

- `support`
- `contrast`
- `extends`
- `example`
- `prerequisite`

If multiple candidate links exist, prefer depth over breadth. Two good links are better than eight weak ones.

## MOC awareness

If the note clearly belongs to an emerging cluster, suggest one MOC entry line after the note:

```markdown
Possible MOC placement: [[MOC-Topic Name]] - <why this card belongs there>
```

Only do this when the cluster is real. Do not create fake structure too early.

## Response patterns

### If the input is strong and atomic

Return the finished card note directly.

### If the input is copied and under-explained

Ask for a short paraphrase first, such as:

`Summarize the core point in your own words in up to 3 sentences, and I’ll turn it into a durable card note.`

### If the input contains too many ideas

Say which idea should become the main card, then propose split titles.

## Example

**Input**

`I highlighted a passage saying people confuse collecting information with learning, and I want a permanent note from it.`

**Output**

````markdown
# Collecting information can feel like learning without improving recall

## Core Idea
Copying, highlighting, and saving material can create the feeling of progress without proving that understanding has improved. Real learning usually requires retrieval, reformulation, or application, not just exposure.

## Why It Matters
This changes how I judge note-taking quality. A note is valuable when it helps me think again later, not when it merely preserves the source.

## Evidence or Source
- Source: reading highlight
- Context: reflection on passive note collection

## Related Notes
- [[Retrieval practice reveals whether knowledge is usable]] - support

## Open Questions
- What note formats force me to restate an idea instead of merely storing it?
````

## Final check before saving

Before you finish, verify:

- the note contains one main idea
- the main idea is in the user's own words
- the source is preserved without taking over the note
- every related link has a reason
- the title still makes sense when seen alone
