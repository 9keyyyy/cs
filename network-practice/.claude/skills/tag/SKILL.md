---
name: tag
description: Semver tag bump and CHANGELOG update. Use when the user asks to tag, release, or bump version (e.g. "태그해줘", "버전 올려줘", "tag해줘").
argument-hint: "[major|minor|patch]"
---

# Tag - Semver Tag & Changelog

Analyzes commits since the last semver tag, determines the version bump, creates the tag, and updates CHANGELOG.md.

## Input
$ARGUMENTS

Format: `[major|minor|patch]` (optional override)
- `/tag` → auto-detect bump type from commits
- `/tag patch` → force patch bump
- `/tag minor` → force minor bump

---

## Semver Bump Rules (auto-detect)

Analyze commit messages since the last semver tag (`vX.Y.Z`):

| Commit type | Bump |
|-------------|------|
| `feat:` | **minor** (0.X.0) |
| `fix:` | **patch** (0.0.X) |
| `refactor:` | **patch** |
| `chore:` | **patch** |
| `docs:` | **patch** |
| `style:` | **patch** |
| `test:` | **patch** |
| Commit message contains `BREAKING CHANGE` or type has `!` suffix (e.g. `feat!:`) | **major** (X.0.0) |

The highest bump level wins. If the user provides an explicit level, use that instead.

If no semver tag exists yet, start from `v1.0.0` (since `v1` floating tag already exists for GitHub Actions).

---

## Procedure

### Step 1: Find the latest semver tag
1. Run `git tag -l 'v[0-9]*.[0-9]*.[0-9]*' --sort=-v:refname | head -1`
2. If no tag found, set base version as `v0.0.0`

### Step 2: Analyze commits
1. Run `git log {last_tag}..HEAD --oneline` (or `git log --oneline` if no previous tag)
2. Categorize each commit by its type prefix
3. Determine the bump level (or use the user-provided override)
4. Calculate the new version

### Step 3: Update CHANGELOG.md
1. If CHANGELOG.md does not exist, create it
2. Prepend a new section at the top (below the `# Changelog` header):

```markdown
## [vX.Y.Z] - YYYY-MM-DD

### Added
- {feat commits}

### Fixed
- {fix commits}

### Changed
- {refactor, chore, style, docs, test commits}
```

- Only include sections that have entries (e.g., skip `### Added` if no feat commits)
- Each entry: commit summary in Korean (strip the type prefix)
- Group by section, not by commit order

### Step 4: Commit, tag, and push
1. Stage and commit CHANGELOG.md:
   ```
   chore: v{X.Y.Z} 릴리스 노트 추가
   ```
2. Create annotated tag:
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   ```
3. Update major version tag (`v1`) to point to the same commit (GitHub Actions `@v1` convention):
   ```bash
   git tag -f v1
   ```
4. Push commit and tags:
   ```bash
   git push origin main
   git push origin vX.Y.Z
   git push origin -f v1
   ```

### Step 5: Report
- New version tag
- Bump type (major/minor/patch)
- Number of commits included
- CHANGELOG.md preview (the new section only)
