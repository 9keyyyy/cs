---
name: pr
description: Convention-based PR creation. Use when the user asks to create a PR (e.g. "PR 만들어줘", "PR 생성해줘", "풀리퀘 올려줘").
argument-hint: "[github_issue_number] [jira-key] [--auto]"
---

# PR Creation Skill

Analyzes changes on the current branch and creates a PR following the project convention.

## Input
$ARGUMENTS

Format: `<github_issue_numbers> [jira-key] [--auto]`
- Multiple issue numbers can be separated by spaces or commas
Examples:
- `/pr 42 KMEDAI-121` → Create PR after user confirmation, closes #42
- `/pr 42 43 KMEDAI-121 --auto` → Create PR without confirmation, closes #42 and #43
- `/pr 42,43` → Closes #42 and #43, no Jira key
- `/pr 42` → Link GitHub Issue #42, no Jira key
- `/pr` → No arguments, write PR based on commit content

---

## Pre-checks

1. Verify the current branch is NOT the base branch (`main`)
   - If on base branch, warn and abort
2. Check for uncommitted changes (`git status`)
   - `--auto` mode: ignore unstaged changes and proceed
   - Default mode: if unstaged changes exist, ask the user whether to run `/commit` first

---

## Procedure

### Step 1: Analyze changes
1. Run `git log --oneline main..HEAD` to review commit history
2. Run `git diff main...HEAD` to understand the full diff
3. **Read changed files directly for full context** (diff alone is insufficient)
   - New files: read entire content to understand purpose and structure
   - Modified files: read surrounding context of changes
4. Identify and summarize:
   - Newly introduced patterns, architecture decisions, conventions
   - New files/directory structures
   - **For test code**: fixture structure, helper functions, purpose of each test case
5. Determine Jira key (priority order):
   - Jira key passed as argument
   - Extract from branch name (e.g. `feat/KMEDAI-121` → `KMEDAI-121`)
   - If none, proceed without Jira key
6. If `.claude/plans/{jira-key}.md` exists, reference the plan content

### Step 2: Write PR content
If `.github/PULL_REQUEST_TEMPLATE.md` exists, follow that format. Otherwise, use the default template below.

**PR Title**: `[{JIRA-KEY}] {Korean summary} (#{github_issue_numbers})`
- Multiple issues: `[{JIRA-KEY}] {Korean summary} (#42, #43)`
- No Jira key provided: `[KMEDAI-X] {Korean summary} (#{github_issue_numbers})`
- No GitHub issue number either: `[KMEDAI-X] {Korean summary}`

**PR Body**:
````markdown
## ✨ 작업 배경

{One-line summary of what and why.}
{If needed, list key decisions/constraints as bullet points.}
{Reference .claude/plans/ content if available.}

Closes #{github_issue_number}
{If multiple issues: list each on its own line, e.g. "Closes #42", "Closes #43"}

## 💻 작업 내용

### 🔑 Key changes
{Number major changes (1. 2. 3.) and use sub-bullets (-) for details.}

{Add section below only if new patterns/conventions are introduced}
### 📖 사용 가이드
{Explain usage of new patterns with code examples.}

{Add section below only if new files/directories are added}
### 📁 변경 파일 구조
{Show new/changed file structure in tree format.}

## 🏃 기능 동작 시연

{Describe scenarios if applicable, otherwise "N/A"}

## 💬 코멘트

- Jira: [{jira-key}](https://jira.navercorp.com/browse/{jira-key})
````

> **Writing principle**: Do not list diffs. Describe *what*, *why*, and *how* changes were made so reviewers can understand without reading the code.

### Step 3: User confirmation

> If `--auto` option is set, skip this step and go directly to Step 4.

Show the following to the user and wait for approval:
- PR title
- PR body preview
- Base branch → Head branch
- Number of changed files, lines added/deleted

Based on user response:
- **Approve** → Proceed to Step 4
- **Request changes** → Modify title/body and re-confirm
- **Abort** → Do not create PR

### Step 4: Push and create PR
1. Push the branch to remote:
   ```bash
   git push -u origin {current_branch}
   ```
2. Create PR using `gh` CLI:
   ```bash
   gh pr create --base main --head {current_branch} \
     --title "{pr_title}" \
     --body "{pr_body}"
   ```
3. Assign self to the PR after creation:
   ```bash
   gh pr edit {pr_number} --add-assignee @me
   ```

> On failure: show the error message to the user and clarify whether push or PR creation failed.

---

## Final report
- PR URL
- Title
- Number of changed files
