---
name: commit
description: Convention-based commits. Use when the user asks to commit (e.g. "커밋해줘", "commit해줘", "변경사항 저장해줘").
argument-hint: "[jira-key]"
---

# Commit - Convention-based Commits

Analyzes changes and creates commits following the project convention.

## Input
$ARGUMENTS

Format: `<jira-key>` (optional)
Example: `/commit KMEDAI-121`

---

## Commit Message Convention

### Format

```
type: summary of changes (max 50 chars)

- detail 1
- detail 2
```

First line is a concise summary; after a blank line, list details with bullets (`-`).
If a Jira key is provided, append it as `({jira-key})` at the end of the first line.

### Type Rules
| Type | When to use |
|------|------------|
| `feat` | New feature or screen |
| `fix` | Bug fix |
| `refactor` | Code restructure without behavior change |
| `style` | UI/CSS only changes |
| `chore` | Config, deps, tooling, generated files |
| `test` | Test files only |
| `docs` | Documentation only |

### Seven Rules
1. Separate subject from body with a **blank line**
2. Limit subject line to **50 characters**
3. Type prefix in **lowercase**; description starts after `type: `
4. **No period** at end of subject line
5. Write subject in **imperative mood** (e.g. "추가", "수정", "제거" — not "추가했음", "수정하는 중")
6. Wrap body at **72 characters**
7. Body explains **what** and **why**, not *how*
8. **All commit messages must be written in Korean** (type prefix remains English)

### Commit Grouping Strategy

**Group by feature unit**, not by code layer (implementation vs test).

- **One commit = one complete feature unit** — implementation code + its tests together
- If the same type repeats 3+ times in a row, the grouping is wrong (e.g. `test:` x3)
- Use `test:` type **only** when adding tests to existing code or changing test infrastructure

**Grouping example:**
```
# Good — 기능 단위로 분리, 구현 + 테스트 포함
feat: 관리자 활성 상태 변경 구현 (KMEDAI-312)
feat: 관리자 일괄 수정 API 구현 (KMEDAI-312)
feat: 관리자 일괄 삭제 API 구현 (KMEDAI-312)

# Bad — 코드 레이어로 분리, 구현/테스트 따로
feat: 어드민 수정 API 확장 및 일괄 수정/삭제 구현 (KMEDAI-312)
test: 활성 상태 변경 테스트 (KMEDAI-312)
test: 일괄 수정 테스트 (KMEDAI-312)
test: 일괄 삭제 테스트 (KMEDAI-312)
```

### Examples
```
feat: 관리자 계정 생성 구현 (KMEDAI-120)

- AdminService.create_admin() 메서드 구현
- CreateAdminRequest/Response DTO 추가
- POST /api/v1/admins 엔드포인트 등록
- 생성 성공/실패 테스트 추가
```

```
fix: reissue 시 Admin 상태 검증 (KMEDAI-119)

- INACTIVE 상태 관리자 토큰 재발급 차단
- AuthService.reissue()에 상태 검증 로직 추가
```

---

## Procedure

### Step 0: Branch check
1. Check if the current branch is the base branch (`main`)
2. If on `main`:
   - Suggest a branch name to the user based on the changes (or use `{type}/{jira-key}` if a Jira key is provided)
   - Create the new branch and check out to it before committing
3. If not on `main`, continue to Step 1

### Step 1: Sync with remote
1. `git stash` to save current changes (only if there are changes)
2. `git pull --ff-only` to fast-forward to the latest remote commits
3. `git stash pop` to re-apply changes

### Step 2~8: Execute commits
1. `git status` to list changed files
2. `git diff` to analyze changes
3. Determine the appropriate type for each change
4. Stage logically related files together
5. Create commit
6. If changes span multiple concerns, split into 2~4 commits
7. Report results (commit hash, message, branch name)
