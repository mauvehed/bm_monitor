# Release Process

This document outlines the process for creating releases of the BM Monitor project.

## Release Steps

### 1. Prepare Release Changes

Create a new branch for the version bump:
```bash
git checkout -b chore/version-X.Y.Z
```

### 2. Update Version Information

**Update version in code:**
- Edit `bm_monitor.py` line 8: Change `# Current Version: X.Y.Z` to the new version

**Update changelog:**
- Edit `README.md` in the "Change Log" section
- Add new entry at the top following this format:
  ```
  - MM/DD/YYYY - Point Release X.Y.Z - Brief description of changes
  ```

### 3. Create Version Bump PR

```bash
git add bm_monitor.py README.md
git commit -m "chore: bump version to X.Y.Z and update changelog

- Version X.Y.Z: Brief description of changes"
git push -u origin chore/version-X.Y.Z
```

Create PR:
```bash
gh pr create --title "Bump version to X.Y.Z" --body "## Summary
- Update version number in bm_monitor.py to X.Y.Z
- Add changelog entry for [brief description]

Prepares for vX.Y.Z release with [description of changes]."
```

### 4. Merge and Pull

1. Merge the version bump PR
2. Switch back to main and pull:
   ```bash
   git checkout main
   git pull origin main
   ```

### 5. Create GitHub Release

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes "## What's Changed
[Description of the main changes in this release]

[Technical details if needed]

* [PR title] by @username in https://github.com/mauvehed/bm_monitor/pull/##
* [Version bump PR] by @username in https://github.com/mauvehed/bm_monitor/pull/##

**Full Changelog**: https://github.com/mauvehed/bm_monitor/compare/vPREVIOUS...vX.Y.Z"
```

## Release Notes Format

Follow this template for release notes:

```markdown
## What's Changed
Brief summary of the main feature/fix in this release.

[Optional technical details paragraph]

* [Main feature/fix PR title] by @username in https://github.com/mauvehed/bm_monitor/pull/##
* Bump version to X.Y.Z by @username in https://github.com/mauvehed/bm_monitor/pull/##

**Full Changelog**: https://github.com/mauvehed/bm_monitor/compare/vPREVIOUS...vX.Y.Z
```

## Version Numbering

This project uses semantic versioning:
- **Major** (X): Breaking changes
- **Minor** (Y): New features, significant updates
- **Patch** (Z): Bug fixes, small improvements

Recent pattern shows point releases for fixes and minor features:
- v1.3.4 - Fix Discord message line breaks
- v1.3.3 - Add debug logging
- v1.3.2 - Improve logging
- v1.3.1 - TalkerAlias compatibility

## Notes

- All version changes require a PR (no direct commits to main)
- Changelog entries should be concise but descriptive
- Release notes should include both user-facing description and technical details
- Always include links to relevant PRs in release notes