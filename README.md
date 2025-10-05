# Agent Orchestration Example - Java Dependency Analysis

> 🤖 Automated Java dependency analysis using Devin API to identify dependencies that need migration to SaaS repositories

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Devin API key (set as `DEVIN_API_KEY` environment variable)
- `uv` package manager (optional but recommended)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd agent-orchestration-example

# Install dependencies
pip install -r api_example_scripts/requirements.txt

# Or using uv (faster)
uv pip install -r api_example_scripts/requirements.txt
```

### Set up your environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API key
# Get your API key from: https://app.devin.ai/settings/api-keys
vim .env
```

The `.env` file should contain:
```bash
DEVIN_API_KEY=your-actual-api-key-here
```

See `.env.example` for all available configuration options.

---

## 📋 Main Scripts

### 1. `list_dependencies_simple.py` - Run Dependency Analysis

**Purpose**: Creates a Devin session to analyze Java repositories and identify dependencies that need migration from on-premises to SaaS repositories.

#### Basic Usage
```python
# In the script, modify these values:
REPO = "your-org/your-java-repo"
TARGET = "3.17"  # Or None for current version only

# Run the script
python api_example_scripts/list_dependencies_simple.py
```

#### What it does:
1. **Creates a Devin session** with your repository
2. **Analyzes dependencies** for current version and optionally a target version
3. **Waits for completion** (polls every 10 seconds, max 30 minutes)
4. **Saves results** to timestamped JSON file (e.g., `dependencies_20251005_124044.json`)
5. **Prints summary** of dependencies found

#### Output Structure:
```json
{
  "current_version": "3.13.0",
  "target_version": "3.17",
  "dual_mode": true,
  "results": {
    "current": {
      "upload_candidates": [...],  // Dependencies needing upload
      "summary": {...}
    },
    "target": {
      "upload_candidates": [...],
      "summary": {...}
    }
  },
  "stats": {
    "total_dependencies": 34,
    "internal_dependencies": 34,
    "oss_dependencies": 0
  }
}
```

#### Advanced Usage - As a Module:
```python
from api_example_scripts.list_dependencies_simple import get_java_dependencies

# Analyze current version only
results = get_java_dependencies(
    repo_name="my-org/my-repo",
    target_version=None  # Current version only
)

# Analyze both current and target version
results = get_java_dependencies(
    repo_name="my-org/my-repo",
    target_version="3.17"
)
```

---

### 2. `display_dependencies.py` - View and Export Results

**Purpose**: Display dependency analysis results in a readable format and export to CSV.

#### View JSON Results
```bash
# Display from saved JSON file
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json

# Display only current version
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json --version current

# Display only target version
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json --version target
```

#### View from Session ID/URL
```bash
# Using session ID
python api_example_scripts/display_dependencies.py devin-092bcaf1c5544fa59f99ec0095eac782

# Using session URL
python api_example_scripts/display_dependencies.py https://app.devin.ai/sessions/092bcaf1c5544fa59f99ec0095eac782
```

#### Export to CSV
```bash
# Export to CSV (creates output_current.csv and output_target.csv)
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json --csv output

# Export only current version to CSV
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json --version current --csv current_deps
```

#### List Available Files
```bash
# See all dependency JSON files
python api_example_scripts/display_dependencies.py --list
```

---

### 3. `update_playbook.py` - Update Devin Playbooks

**Purpose**: Update or create Devin playbooks that define reusable prompts for dependency analysis.

#### Basic Usage
```python
# Run the script (edit values inside the script)
python api_example_scripts/update_playbook.py
```

#### What it does:
1. **Reads markdown file** (`find-java-deps-playbook.md`)
2. **Creates/updates playbook** in Devin with name `get_java_deps`
3. **Makes it available** as `!get_java_deps` macro in prompts

#### Why use playbooks?
- **Consistency**: Same analysis logic across all sessions
- **Reusability**: Use `!get_java_deps` instead of typing full instructions
- **Version control**: Keep playbook content in Git
- **Updates**: Easily update logic for all future sessions

---

### 4. `create_knowledge_from_markdown.py` - Create Knowledge Base

**Purpose**: Convert markdown documentation into Devin's knowledge base for better context understanding.

#### Basic Usage
```bash
# Create knowledge from README
python api_example_scripts/create_knowledge_from_markdown.py README_DEPENDENCY_RETRIEVAL.md "Dependency Retrieval Guide"

# Create from any markdown file
python api_example_scripts/create_knowledge_from_markdown.py docs/guide.md "My Guide"
```

#### What it does:
1. **Parses markdown** into sections and code blocks
2. **Creates knowledge entries** in Devin's system
3. **Makes context available** for all future sessions
4. **Improves accuracy** of Devin's responses

#### Best practices:
- Keep markdown files focused on single topics
- Include code examples and clear instructions
- Update knowledge when processes change
- Use descriptive titles for easy reference

---

## 🔄 Typical Workflow

### Step 1: Set Up Playbook (One-time setup)
```bash
# Update the playbook with your analysis logic
python api_example_scripts/update_playbook.py
```

### Step 2: Run Analysis
```bash
# Edit the script with your repository
vim api_example_scripts/list_dependencies_simple.py

# Run the analysis
python api_example_scripts/list_dependencies_simple.py
```
**Output**: `dependencies_20251005_124044.json`

### Step 3: View Results
```bash
# Display in terminal
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json

# Export to CSV for sharing
python api_example_scripts/display_dependencies.py dependencies_20251005_124044.json --csv results
```
**Output**: `results_current.csv`, `results_target.csv`

### Step 4: Share Results
- JSON files for technical teams
- CSV files for management/tracking
- Use DataFrame display for quick analysis

---

## 📊 Understanding the Results

### Dependency Classification
- **Internal Dependencies**: Packages from `com.wellsfargo.*`
- **OSS Dependencies**: Open source packages (filtered out by default)
- **Upload Candidates**: Internal dependencies not in SaaS repositories

### Key Fields
- `group`: Maven group ID (e.g., `com.wellsfargo.orchestra`)
- `artifact`: Package name
- `version`: Current version number
- `repository_hint`: Where it's currently hosted
- `needs_upload`: Whether it needs migration to SaaS
- `is_transitive`: Direct (false) or transitive (true) dependency

---

## 🛠️ Additional Scripts

### Session Management
- `list_sessions.py` - List all your Devin sessions
- `inspect_session.py` - Get detailed info about a specific session

### Examples
- `read_session_example.py` - Example usage patterns

---

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEVIN_API_KEY` | Your Devin API key | Yes |
| `JAVA_DEVIN_API_KEY` | Alternative API key name | No |

---

## 🐛 Troubleshooting

### Session gets blocked
This is normal - "blocked" means the task is complete and waiting for input.

### No results in structured_output
Check attachments - results might be in a JSON file attachment instead.

### Timeout errors
Increase `max_wait_minutes` in the script (default is 30).

### Missing dependencies in results
Check the errors section in the JSON output for Gradle resolution issues.

---

## 📚 Resources

- [Devin API Documentation](https://docs.devin.ai)
- [Internal Playbook](api_example_scripts/find-java-deps-playbook.md)
- [Dependency Retrieval Guide](README_DEPENDENCY_RETRIEVAL.md)

---

## 📄 License

[Your License Here]