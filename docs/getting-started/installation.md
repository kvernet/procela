# Installation

This guide covers various ways to install Procela for different use cases.

## Prerequisites

Procela requires **Python 3.10 or higher**. Check your Python version:

```bash
python --version
# or
python3 --version
```

!!! tip "Python Version Management"
    If you need to manage multiple Python versions, consider using:
    - [pyenv](https://github.com/pyenv/pyenv) (Linux/macOS)
    - [pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows)
    - [conda](https://conda.io/) (cross-platform)

## Installation Methods

### Method 1: From PyPI (Stable Release)

The simplest way to install Procela for most users:

```bash
pip install procela
```

To install a specific version:

```bash
pip install procela==1.0.0
```

### Method 2: From GitHub (Development Version)

Install the latest development version directly from the source repository:

```bash
pip install git+https://github.com/kvernet/procela.git
```

To install a specific branch:

```bash
pip install git+https://github.com/kvernet/procela.git@develop
```

### Method 3: Development Installation (Editable Mode)

Recommended if you plan to modify Procela or contribute to its development:

```bash
# Clone the repository
git clone https://github.com/kvernet/procela.git
cd procela

# Create a virtual environment (recommended)
python -m venv .venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

This installs Procela in "editable" mode, meaning changes to the source code are immediately reflected without reinstallation.

### Method 4: Using Conda/Mamba

While Procela isn't on conda-forge yet, you can install it via pip within a conda environment:

```bash
# Create a conda environment with Python 3.10+
conda create -n procela python=3.10
conda activate procela

# Install via pip
pip install procela
```

## Verifying Installation

After installation, verify that Procela is correctly installed:

```python
import procela
print(procela.__version__)
```

If this runs without errors, you're ready to go!

## Development Dependencies

If you're setting up a development environment, you'll need additional packages. Install them with:

```bash
pip install -e ".[dev]"
```

The development dependencies include:
- **Testing**: `pytest`, `pytest-cov`
- **Linting**: `ruff`, `black`
- **Type checking**: `mypy`
- **Documentation**: `mkdocs`, `mkdocs-material`, `mkdocstrings`
- **Pre-commit hooks**: `pre-commit`

## Setting Up Pre-commit Hooks (For Contributors)

If you're contributing to Procela, set up pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

This will automatically run linters and formatters before each commit.

## Makefile Commands (Development)

Procela includes a Makefile with useful commands for development:

```bash
make install          # Install package and dependencies
make dev-install      # Install with development dependencies
make lint            # Run linters (ruff, black)
make type-check      # Run mypy type checking
make test            # Run pytest with coverage
make pre-commit      # Run all checks before committing
make docs            # Build documentation
make clean           # Clean build artifacts
```

## Platform-Specific Notes

### Windows

If you encounter issues with `make` on Windows, you can:
1. Install [Make for Windows](http://gnuwin32.sourceforge.net/packages/make.htm)
2. Use WSL (Windows Subsystem for Linux)
3. Manually run the commands from `Makefile`

### Linux/macOS

Most Linux distributions and macOS have `make` pre-installed. If not:

```bash
# Ubuntu/Debian
sudo apt-get install make

# macOS
xcode-select --install  # Installs command line tools including make

# Fedora
sudo dnf install make
```

## Common Installation Issues

### Issue: "Python 3.10 or higher required"

**Solution**: Install Python 3.10+ from [python.org](https://python.org) or use pyenv:

```bash
# Using pyenv
pyenv install 3.10.0
pyenv local 3.10.0
```

### Issue: "pip not found"

**Solution**: Install pip or use python -m pip:

```bash
# Install pip
python -m ensurepip --upgrade

# Or use python -m pip directly
python -m pip install procela
```

### Issue: Permission denied on Linux/macOS

**Solution**: Install for your user only (no sudo needed):

```bash
pip install --user procela
```

Or use a virtual environment to avoid permission issues.

### Issue: "No module named 'procela'" after installation

**Solution**: Verify your Python environment:
- Check that you're using the correct Python interpreter (activate the virtual environment)
- Ensure the installation succeeded without errors
- Try installing in a fresh virtual environment

## Docker Installation (Optional)

For containerized development or deployment:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install procela

COPY . .

CMD ["python", "your_script.py"]
```

Build and run:

```bash
docker build -t procela-app .
docker run procela-app
```

## Next Steps

After successful installation:
- Follow the [Quick Start Guide](quickstart.md) to create your first simulation
- Explore the [Core Concepts](../core-concepts/variables.md) to understand Procela's architecture
- Check out the [AMR Case Study](../examples/amr-case-study.md) for a real-world example

## Getting Help

If you encounter installation issues not covered here:

- Open an issue on [GitHub](https://github.com/kvernet/procela/issues)
- Email: <a href="mailto:research@procela.org">research@procela.org</a>
