---
name: obsidian-task-management-editor
description: Create, edit, schedule, complete, and review project tasks in the PavelObsidianNotes Obsidian vault. Use this skill whenever the user asks to add a task, update a task's status/priority/date/project, plan today's work, create a project or daily progress record, break work into actionable tasks, or maintain the task-management workspace in this vault—even when they only describe the work naturally in Chinese.
---

# Obsidian Task Management Editor

Maintain the task system in `B:\GitHub\Obsadian\PavelObsidianNotes` as local Markdown files. The system is intentionally simple: a project owns tasks, and daily-progress notes record what happened. Preserve this structure so Obsidian Bases, Dataview, and the custom task workspace continue to work.

## Read the vault conventions first

Before making changes, read these files in this order:

1. `知识库配置.md` — source of truth for folder locations.
2. `目标与任务/项目任务字段规范.md` — allowed task states, priorities, and periods.
3. The relevant template in `模板/`.
4. The target record(s), if they already exist.

Do not hard-code a folder when `知识库配置.md` defines it. Its defaults are:

| Record | Config key | Default folder |
| --- | --- | --- |
| Project | `project_folder` | `目标与任务/任务管理/项目` |
| Task | `task_folder` | `目标与任务/任务管理/任务` |
| Daily progress | `daily_progress_folder` | `目标与任务/任务管理/每日进展` |

Use the vault root as the working directory. Read and write Markdown as UTF-8.

## Core model and valid values

- A **project** is a durable outcome or initiative. It has `type: 项目`.
- A **task** is a concrete, independently completable action. It has `type: 任务` and optionally links to its project through `所属项目: "[[项目名称]]"`.
- A **daily progress** record logs the work done on a specific date. It has `type: 每日进展` and links using `关联任务` and `所属项目`.

Keep these values exact unless the user explicitly asks to extend the schema:

- `任务状态`: `待做`, `进行中`, `完成`, `暂停`
- `任务优先级`: `P0`, `P1`, `P2`
- `周期`: `每日`, `每周`, `每月`, `每季度`
- `完成`: boolean `true` or `false`

Use ISO dates: `YYYY-MM-DD`. Infer the current quarter as `YYYY Q1` through `YYYY Q4` from the current date if it is not specified.

## Create records

Start from the corresponding template in `模板/`, retaining the frontmatter keys and body headings. Replace the placeholder title and fill only the fields that are known or safely inferable.

### Create a task

Create one Markdown file in the configured task folder. The file name and first heading should be the task title.

Minimum useful frontmatter:

```yaml
type: 任务
所属项目: "[[项目名称]]" # leave blank only when genuinely unassigned
周期: 每日
所属季度: 2026 Q3
是否今日重点: false
任务状态: 待做
任务优先级: P2
创建日期: 2026-07-19
计划日期:
预计完成时间:
预计耗时分钟:
计时状态: 未开始
计时开始时间:
累计耗时秒: 0
完成: false
完成日期:
任务负责人:
任务描述:
父记录:
关联笔记: []
tags:
  - task
```

Give the body a concrete, checkable `完成标准` and a single immediately actionable `下一步行动`. Do not turn a vague project into dozens of tasks. Propose a short task breakdown first when the number or scope is unclear.

### Create a project

Create a file in the configured project folder using `模板/项目模板.md`. Set `type: 项目`, the correct `所属季度`, and link `年度目标` only when known. Keep the project's task query block from the template so related tasks remain discoverable.

### Create a daily progress record

Create it in the configured daily-progress folder using `模板/每日进展模板.md`. Set `进展日期` and link the task/project with wikilinks. Use the record to capture completed work, current work, blockers, and a realistic next-day plan; do not change task status merely because a progress note is created.

## Edit existing tasks safely

1. Locate the record by exact file name first. If that is ambiguous, search task titles and frontmatter and report the candidates before writing.
2. Preserve unknown frontmatter, links, tags, body text, and manually written checklists.
3. Update only the fields needed for the requested change.
4. Keep state fields consistent:
   - Marking a task complete sets `任务状态: 完成`, `完成: true`, and `完成日期` to the completion date. If it was timing, set `计时状态: 完成` and clear `计时开始时间`.
   - Reopening a completed task sets `任务状态: 待做` (or `进行中` if requested), `完成: false`, and clears `完成日期`. Do not erase accumulated time.
   - Pausing sets `任务状态: 暂停`; resuming sets it to `进行中`.
   - Scheduling a task for today sets `计划日期` to today and `是否今日重点: true`. Moving it to another date sets `是否今日重点: false`, unless the user explicitly wants it highlighted.
   - Removing a schedule clears `计划日期` and sets `是否今日重点: false`.
5. Do not rename or delete records unless the user explicitly requests it. Before deleting, identify the exact file and warn that linked Base/Dataview views will no longer show it.

## Planning and review requests

For requests such as “plan today”, “整理任务”, or “what should I do next”:

1. Inspect active tasks in the configured task folder.
2. Prioritize `P0`, then `P1`, then `P2`; within a priority, prefer already scheduled, overdue, or nearest-deadline tasks.
3. Treat `完成: true` or `任务状态: 完成` as completed; flag mismatches instead of silently guessing.
4. Suggest a small, feasible plan. Only write schedule or priority changes when the user asks to apply the plan.

For a review, report concise counts of active/completed tasks, overdue work, unscheduled work, and any inconsistent records. Use the relevant quarterly `.base` file only as a view definition; task Markdown frontmatter is the editable source data.

## Quality checks before handoff

After every change, verify:

- The target file is in the configured folder and has the expected `type`.
- Wikilinks point to an existing project/task when a link was supplied.
- Dates use `YYYY-MM-DD` and the quarter matches the intended period.
- `任务状态`, `完成`, `完成日期`, and timer fields remain consistent.
- New tasks contain a non-empty completion criterion and next action.

Then state exactly which files were created or changed and summarize the field-level updates. If the request was ambiguous, state the assumption made; do not fabricate dates, project associations, owners, estimates, or completion evidence.
