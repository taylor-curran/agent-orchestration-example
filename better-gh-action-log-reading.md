# GitHub Actions: Quick Triage Guide (with generic placeholders)

Use these commands to investigate a failing job without relying on the web UI. Replace placeholders like `<repo>`, `<job-id>`, and `<run-id>`.

---

## 1) Identify step outcomes for a job

See exactly which step failed.

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id> \
  --jq '.steps[] | [.number, .name, .status, .conclusion] | @tsv'
```

-   Look for the step with `conclusion` = `failure` (e.g., the **Build** step).
    

> FYI: Lines labeled `UNKNOWN STEP` in raw logs usually come from reusable workflows or internal scripts printing their own groups; they’re not GitHub “steps.” Trust the list above for real step boundaries.

---

## 2) Get the job’s raw logs

Dump the entire job log to a local file and search it.

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id>/logs > job.log
```

Common grep filters that quickly surface root causes:

```bash
grep -nE 'FAILURE: Build failed|> Task .* FAILED|BUILD FAILED|Could not resolve|Could not find|Execution failed|Compilation failed|error:|Exit code|returned non-zero' job.log | sed -n '1,200p'
```

---

## 3) View logs in the terminal (unpaginated)

Handy when you want to stay in the CLI.

```bash
GH_PAGER=cat gh run view --job <job-id> --repo <org>/<repo> --log
```

Optionally jump to a likely step area (e.g., “Build”) and show the next ~400 lines:

```bash
GH_PAGER=cat gh run view --job <job-id> --repo <org>/<repo> --log | \
  sed -n '/Build/,$p' | head -n 400
```

---

## 4) Download step-by-step files

Great for pinpointing a single failing step file.

```bash
gh run download --job <job-id> --repo <org>/<repo> -D logs

# list step text files
find logs -type f -name '*.txt' | sort | nl

# open likely “Build” step files (try both forms)
sed -n '1,200p' logs/*/*'49_Build'*.txt     # if step numbers are in filenames
sed -n '1,200p' logs/*/*'Build.txt'         # if names only
```

---

## 5) Get the run id from a job, then enumerate jobs in the run

Sometimes multiple jobs exist; this helps you compare.

```bash
# Get the run id containing this job
gh api repos/<org>/<repo>/actions/jobs/<job-id> --jq .run_id
```

```bash
# List jobs and their step names for the run
RUN_ID=<run-id>
gh api repos/<org>/<repo>/actions/runs/$RUN_ID/jobs?per_page=100 \
  --jq '.jobs[] | {id, name, steps: [.steps[]?.name]}'
```

---

## 6) Inspect a single step’s metadata (timings & status)

Helpful to time-box where to look in the log.

```bash
gh api repos/<org>/<repo>/actions/jobs/<job-id> \
  --jq '.steps[] | select(.number==<step-number>)'
```

---

## 7) Quick patterns for Java/Node builds (optional)

Use these on `job.log` or a specific step file:

```bash
# Dependency resolution / repo access
grep -nE 'Could not resolve|Could not find|401 Unauthorized|403 Forbidden|ENOTFOUND|ECONNREFUSED' job.log

# Java compilation
grep -nE ':compile.*FAILED|error: cannot find symbol|package .* does not exist|symbol: *class|method .* not found' job.log

# Node builds
grep -nE 'ERR!|ELIFECYCLE|npm ERR! code|yarn run v|Command failed with exit code' job.log
```

---

## Notes & Tips

-   **UNKNOWN STEP** labels in `gh run view` usually reflect grouped output produced *inside* a step (reusable workflows, composite actions, or custom tooling). They’re not failures by themselves.
    
-   Always start with the **step summary** (Section 1) to find the single failing step, then drill into logs (Sections 2–4).
    
-   When sharing snippets, include ~100 lines around the first “Could not … / FAILED” line for fastest triage.
