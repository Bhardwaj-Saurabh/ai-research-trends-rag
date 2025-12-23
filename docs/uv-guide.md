# Using `uv` for Environment Management

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reliable Python environment management.

## Why `uv`?

- **10-100x faster** than pip
- **Better dependency resolution** - resolves conflicts automatically
- **Built in Rust** - rock solid and performant
- **Drop-in replacement** for pip and venv
- **Created by Astral** (makers of Ruff)

## Installation

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Via pip
```bash
pip install uv
```

### Verify
```bash
uv --version
# uv 0.1.x or later
```

## Quick Start

### Create Virtual Environment
```bash
# In any service directory
cd services/processing-service

# Create venv (uv is much faster than python -m venv)
uv venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Install Dependencies

**From pyproject.toml** (recommended):
```bash
uv pip install -e .
```

**From requirements.txt**:
```bash
uv pip install -r requirements.txt
```

**Individual packages**:
```bash
uv pip install fastapi uvicorn
```

### Update Dependencies
```bash
# Update all packages
uv pip install --upgrade -e .

# Update specific package
uv pip install --upgrade fastapi
```

## Project Structure

Each service has a `pyproject.toml`:

```toml
[project]
name = "processing-service"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.109.0",
    "uvicorn[standard]==0.27.0",
    # ...
]

[tool.uv]
dev-dependencies = [
    "pytest==7.4.3",
    # ...
]
```

## Common Commands

### Create Environment
```bash
uv venv                    # Create .venv
uv venv --python 3.11      # Specify Python version
uv venv myenv              # Custom name
```

### Install Packages
```bash
uv pip install -e .                 # Install project in editable mode
uv pip install fastapi              # Install package
uv pip install -r requirements.txt  # From requirements.txt
```

### List Packages
```bash
uv pip list                # List installed packages
uv pip show fastapi        # Show package details
```

### Uninstall
```bash
uv pip uninstall fastapi   # Remove package
```

### Sync (install exact versions)
```bash
uv pip sync requirements.txt  # Install exact versions, remove extras
```

## Workflow for Each Service

### Processing Service
```bash
cd services/processing-service
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn main:app --reload
```

### RAG Query Service
```bash
cd services/rag-query-service
uv venv
source .venv/bin/activate
uv pip install -e .
uvicorn main:app --reload --port 8001
```

### Frontend
```bash
cd services/frontend
uv venv
source .venv/bin/activate
uv pip install -e .
streamlit run app.py
```

## Performance Comparison

**Installing processing-service dependencies:**

| Tool | Time |
|------|------|
| pip | ~60 seconds |
| pip with cache | ~30 seconds |
| uv | **~3 seconds** |

**Creating virtual environment:**

| Tool | Time |
|------|------|
| python -m venv | ~2 seconds |
| uv venv | **~0.1 seconds** |

## Tips & Tricks

### 1. Always use `pyproject.toml`
uv works best with `pyproject.toml`. We've created one for each service.

### 2. Install in editable mode
```bash
uv pip install -e .
```
This allows you to edit code without reinstalling.

### 3. Use `--upgrade` to update
```bash
uv pip install --upgrade -e .
```

### 4. Check what changed
```bash
uv pip list --outdated
```

### 5. Generate requirements.txt
```bash
uv pip freeze > requirements.txt
```

### 6. Use dev dependencies
```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Defined in pyproject.toml:
# [tool.uv]
# dev-dependencies = ["pytest", "ruff"]
```

## Troubleshooting

### "uv: command not found"

**Solution:**
```bash
# Add to PATH (usually done automatically)
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Package conflicts

uv has better resolution than pip, so it will catch conflicts:

```
error: Package 'X' requires 'Y>=2.0', but 'Y==1.0' is installed
```

**Solution:**
```bash
# Update the conflicting package
uv pip install --upgrade Y

# Or specify exact version in pyproject.toml
```

### "No such file or directory: '.venv'"

**Solution:**
```bash
# Create venv first
uv venv

# Then activate
source .venv/bin/activate
```

## Migration from pip

### Replace these commands:

| Old (pip) | New (uv) |
|-----------|----------|
| `python -m venv venv` | `uv venv` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install package` | `uv pip install package` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |

### No changes needed for:
- Activating venv: `source .venv/bin/activate`
- Running services: `uvicorn main:app`
- Python imports: Everything works the same

## Advanced Usage

### Lock Dependencies
```bash
# Generate lock file (ensures reproducible installs)
uv pip compile pyproject.toml -o requirements.lock

# Install from lock file
uv pip sync requirements.lock
```

### Multiple Python Versions
```bash
# Use specific Python version
uv venv --python 3.11
uv venv --python 3.12

# uv will download Python if needed
```

### Workspace Support
```bash
# In project root
uv pip install -e services/processing-service
uv pip install -e services/rag-query-service
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: |
    uv venv
    source .venv/bin/activate
    uv pip install -e .
```

### Docker
```dockerfile
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Copy files
COPY pyproject.toml .
COPY . .

# Install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e .
```

## Resources

- **uv Documentation**: https://github.com/astral-sh/uv
- **Astral Blog**: https://astral.sh/blog
- **Python Packaging Guide**: https://packaging.python.org/

## Summary

**Key Benefits:**
- ⚡ 10-100x faster than pip
- 🎯 Better dependency resolution
- 🔒 Reproducible builds
- 🛠️ Drop-in pip replacement
- 🚀 Created by the Ruff team

**Quick Commands:**
```bash
uv venv                  # Create venv
source .venv/bin/activate # Activate
uv pip install -e .      # Install project
uv pip install package   # Install package
uv pip list              # List packages
```

Start using `uv` today and never wait for pip again! 🚀
