# 🧩 GitHub Actions: Quick Triage Guide

Use these commands to investigate a failing GitHub Actions job directly from the CLI — no web UI needed.  
Replace placeholders like `<org>`, `<repo>`, `<job-id>`, and `<run-id>`.

---

## 1️⃣ Identify step outcomes for a job

See exactly which step failed:

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id> \
  --jq '.steps[] | [.number, .name, .status, .conclusion] | @tsv'
```

-   Look for the step where `conclusion` = `failure` (e.g., **Build**).
    
-   Lines labeled **UNKNOWN STEP** in logs usually come from *reusable workflows* or *custom tooling* that emit grouped logs. They’re not actual steps — rely on this list for the real step breakdown.
    

---

## 2️⃣ Get the job’s raw logs

Dump the full job log to a local file for easy searching:

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id>/logs > job.log
```

Common filters to find the failure quickly:

```bash
grep -nE 'FAILURE: Build failed|> Task .* FAILED|BUILD FAILED|Could not resolve|Could not find|Execution failed|Compilation failed|error:|Exit code|returned non-zero' job.log | sed -n '1,200p'
```

---

## 3️⃣ View logs in the terminal (unpaginated)

Quickly inspect logs inline:

```bash
GH_PAGER=cat gh run view --job <job-id> --repo <org>/<repo> --log
```

Jump straight to a likely area (like “Build”) and show the next ~400 lines:

```bash
GH_PAGER=cat gh run view --job <job-id> --repo <org>/<repo> --log | \
  sed -n '/Build/,$p' | head -n 400
```

---

## 4️⃣ Download full logs and artifacts for the workflow run

`gh run download` works at the **run level**, not the job level.  
First, get the **run ID** associated with your job:

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id> --jq .run_id
```

Then download all artifacts and logs for that run:

```bash
gh run download <run-id> --repo <org>/<repo> -D logs
```

List and explore downloaded log files:

```bash
find logs -type f -name '*.txt' | sort | nl
```

Open the likely “Build” step log (try both patterns):

```bash
sed -n '1,200p' logs/*/*'49_Build'*.txt
sed -n '1,200p' logs/*/*'Build.txt'
```

Search for failures:

```bash
grep -nE 'FAIL|error:|Could not' logs/*/*'Build'*.txt | head -n 50
```

---

## 5️⃣ List all jobs and steps in the same run

If your workflow has multiple jobs, compare their outcomes:

```bash
RUN_ID=<run-id>
gh api repos/<org>/<repo>/actions/runs/$RUN_ID/jobs?per_page=100 \
  --jq '.jobs[] | {id, name, steps: [.steps[]?.name]}'
```

---

## 6️⃣ Inspect metadata for a single step

To see timing, status, and environment info for a specific step:

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id> \
  --jq '.steps[] | select(.number==<step-number>)'
```

---

## 7️⃣ Common search patterns for Java / Node builds

Use these on `job.log` or a specific step log:

```bash
# Dependency resolution / repo access issues
grep -nE 'Could not resolve|Could not find|401 Unauthorized|403 Forbidden|ENOTFOUND|ECONNREFUSED' job.log

# Java compilation problems
grep -nE ':compile.*FAILED|error: cannot find symbol|package .* does not exist|symbol: *class|method .* not found' job.log

# Node / NPM / Yarn issues
grep -nE 'ERR!|ELIFECYCLE|npm ERR! code|yarn run v|Command failed with exit code' job.log
```

---

## 🧠 Notes & Tips

-   **UNKNOWN STEP** → comes from grouped output within composite or reusable workflows. It’s just a log grouping, not a real step failure.
    
-   Start every investigation by checking the **step summary** (Section 1). That tells you which step actually failed before diving into logs.
    
-   For collaboration, share ~100 lines around the first “Could not …” or “FAILED” match — that’s typically where the root cause appears.
    

---
