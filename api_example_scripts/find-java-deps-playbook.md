# 🎯 Devin Session Prompt — Upload Candidates (Internal deps only, JSON output)

**Provide your results as JSON using one of these methods:**
1. **Preferred**: Update the `structured_output` API field 
2. **Alternative**: Create a JSON file attachment (e.g., `output.json`)

**Do not modify the repo. Do not commit.**

## Parameters

```
CURRENT_VERSION = "current"  # The baseline Orchestra version (as declared in existing build)
TARGET_VERSION = "3.17"      # Target Orchestra version to analyze
DUAL_MODE = True             # Analyze both current and TARGET_VERSION
INCLUDE_FULL_GRAPH = False   # Keep false to avoid noise (only upload candidates)

ALLOWED_SAAS_REPOS = [
  "mavenCentral", 
  "central-proxy", 
  "gradle-plugin-portal", 
  "gradle-plugin-portal-proxy",
  "confluent-proxy", 
  "apache-snapshots-proxy",
  "jfrog-saas-proxy", 
  "wf-saas-internal"
]
# Adjust based on actual repo names from Gradle logs
```

## Output Format

**Provide your analysis results using the JSON schema below.**

**Output Options:**
- **Option 1 (Preferred)**: Update the `structured_output` API field with your results
- **Option 2**: Create a JSON file attachment (e.g., `output.json`) with the results

**Progressive Updates (if using structured_output):** Update after EACH milestone:
1. After detecting current BOM/Orchestra version → Set `progress.version_detected = true`
2. After resolving current version dependencies → Set `progress.current_resolved = true`
3. After building current upload candidates → Set `progress.candidates_built = true`
4. If DUAL_MODE, after resolving target version → Set `progress.target_resolved = true`
5. If DUAL_MODE, after creating diff → Set `progress.diff_created = true`
6. When complete → Set `status = "complete"` (status should ideally be "finished")

Use this exact JSON schema:

```json
{
  "status": "complete",
  "dual_mode": true,
  "current_version": "X.Y.Z",
  "target_version": "3.17",
  "progress": {
    "version_detected": true,
    "current_resolved": true,
    "target_resolved": true,
    "candidates_built": true,
    "diff_created": true
  },
  "results": {
    "current": {
      "summary": {
        "total_dependencies": 0,
        "internal_dependencies": 0,
        "oss_dependencies": 0,
        "unresolved_count": 0
      },
      "upload_candidates": [
        {
          "group": "com.wellsfargo",
          "artifact": "orchestra-framework",
          "version": "3.10",
          "type": "lib",
          "repository_hint": "prod-dev-java",
          "reason": "internal artifact resolved from on-prem repo not in ALLOWED_SAAS_REPOS",
          "is_transitive": false,
          "parents": []
        }
      ],
      "unresolved": [
        {
          "coordinate": "com.wellsfargo:variable-tokenizer:3.10",
          "via": "runtimeClasspath",
          "reason": "404 Not Found",
          "repository_hint": "prod-dev-java"
        }
      ]
    },
    "target": {
      "summary": {
        "total_dependencies": 0,
        "internal_dependencies": 0,
        "oss_dependencies": 0,
        "unresolved_count": 0
      },
      "upload_candidates": [],
      "unresolved": []
    },
    "diff": {
      "added_candidates": [
        { "group": "com.wellsfargo", "artifact": "orchestra-openapi", "old": null, "new": "3.17" }
      ],
      "removed_candidates": [
        { "group": "com.wellsfargo", "artifact": "orchestra-legacy", "old": "3.10", "new": null }
      ],
      "version_changed_candidates": [
        { "group": "com.wellsfargo", "artifact": "orchestra-framework", "old": "3.10", "new": "3.17" }
      ]
    }
  },
  "stats": {
    "current": {
      "candidates_count": 0,
      "oss_ignored_count": 0
    },
    "target": {
      "candidates_count": 0,
      "oss_ignored_count": 0
    }
  },
  "notes": [
    "Classified needs_upload by (internal && repo not in ALLOWED_SAAS_REPOS) OR unresolved.",
    "Repository hints inferred from Gradle resolution output.",
    "Parents truncated to 3 hops to keep JSON readable."
  ],
  "errors": []
}
```

**Field Specifications:**
- `type`: `lib` | `plugin` | `bom`
- `repository_hint`: Target repository name from Gradle resolution logs (e.g., `prod-dev-java`, `jfrog-proxy`)
- `reason`: Explanation for why this artifact needs upload (e.g., "resolved from on-prem prod-dev-java", "unresolved 404", "auth 401")
- `parents`: List of parent dependencies (empty for direct deps, truncate to 3 hops max)
- `is_transitive`: `true` if brought in transitively, `false` if direct dependency

---

## Task

Discover **only the dependencies that must be uploaded** to non-prod JFrog SaaS in order to build this repo. Do this for:

1. The repo's current Orchestra/BOM version
2. `TARGET_VERSION = "3.17"` (via an ephemeral Gradle init script outside the repo to pin the BOM—no edits to repo files)

## Classification & "Needs Upload" Logic

**Internal** if:
- `group` starts with `com.wellsfargo`, OR
- `artifact` id starts with `orchestra-`, OR
- Known WF Gradle plugin ids

**needs_upload = true** if:
- (Internal) AND (`repository_hint` not in `ALLOWED_SAAS_REPOS` OR unresolved due to 401/403/404/Not Found)

**Keep OSS out of the main list** — only summarize counts in `stats.oss_ignored_count`.

For each candidate, include **why** (e.g., "resolved from on-prem prod-dev-java", "unresolved 404", "auth 401").

## Objectives

1. **Detect BOM and plugin versions** declared in the build configuration.

2. **Resolve dependencies** by running safe introspection commands:
   ```bash
   ./gradlew buildEnvironment
   ./gradlew dependencies --configuration runtimeClasspath --refresh-dependencies
   ```

3. **Parse Gradle resolution logs** to determine:
   - Which repository each artifact resolved from
   - Classify artifacts as internal vs OSS
   - Identify which internal artifacts resolved from repos NOT in `ALLOWED_SAAS_REPOS`

4. **Populate `upload_candidates` array** with ONLY internal artifacts that need upload:
   - Include: `group`, `artifact`, `version`, `type`, `repository_hint`, `reason`, `is_transitive`, `parents`
   - Populate `parents` array for transitive dependencies (truncate to 3 hops max)

5. **Track unresolved dependencies** with full context (coordinate, via configuration, reason, repository_hint).

6. **If `DUAL_MODE = True`**: 
   - Use a Gradle init script in a temporary location (outside the repo) to force `TARGET_VERSION` for the BOM
   - Extract target version upload candidates using the same process
   - Generate a `diff` object with `added_candidates`, `removed_candidates`, and `version_changed_candidates` arrays

7. **Update structured output progressively** as each phase completes.

## Constraints

- **Output results as JSON** (via structured_output or file attachment)
- No code or config edits. Only read and parse existing build metadata.
- No artifact uploads, publishing, or CI/CD activity.
- Use existing `~/.gradle/gradle.properties` for authentication.
- Focus only on dependency metadata (no binary downloads).
- For `TARGET_VERSION` resolution, use a Gradle init script in a temporary location (outside the repo) to avoid modifying project files.

## Output Deliverable

**JSON format** — The complete upload candidate analysis via structured_output OR as a file attachment.

This includes:
- **`upload_candidates`** array: ONLY internal artifacts that need upload (with reason, repository_hint, parent tracking)
- **`unresolved`** array: Dependencies that failed to resolve (with failure reasons)
- **Summary statistics**: Total deps, internal vs OSS counts, candidates count
- **Diff analysis**: `added_candidates`, `removed_candidates`, `version_changed_candidates` (if `DUAL_MODE = True`)
- **Progress indicators** and contextual notes

## Operational Guidance

- If a repo name in logs is ambiguous, include the full resolving URL snippet as `repository_hint`.
- If `ALLOWED_SAAS_REPOS` appears different on this machine (naming), infer and include them in `notes`.
- **`INCLUDE_FULL_GRAPH = False`**: Do NOT include the full dependency list (only upload candidates).
- If you need to show the full graph, add a `full_graph` section only when explicitly requested.

---

## FINAL REMINDER

**Provide your results as JSON using either:**
1. The `structured_output` API field (preferred)
2. A JSON file attachment (alternative)

Both methods work - use whichever is more convenient for the task.

---

