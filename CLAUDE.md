# KI-Konkret Hackathon Project Guide

## Commands
- Run app: `python cvApp.py`
- Create conda env: `conda env create -f environment.yml`
- Activate env: `conda activate ki-konkret-hackathon`
- Install additional packages: `conda install -c conda-forge package_name`
- Format code: `black cvApp.py`
- Lint code: `flake8 cvApp.py --max-line-length=100`
- Check types: `mypy cvApp.py`

## Code Style Guidelines
- **Imports**: Standard library → third-party → local imports with blank line between groups
- **Error Handling**: Use specific exceptions with proper logging and user feedback
- **Logging**: Use logger with appropriate levels (INFO for normal flow, ERROR for issues)
- **Naming**: snake_case for functions/variables, PascalCase for classes, ALL_CAPS for constants
- **Documentation**: Docstrings with description, parameters, and return values
- **Formatting**: 4-space indentation, max 100 chars per line
- **Gradio UI**: Group related components in blocks/columns for organization
- **Config**: Store settings in YAML, never hardcode API keys
- **Types**: Use type hints for function parameters and return values

## Project Structure
- Single-file Gradio app (cvApp.py) for CV generation and PDF export
- Configuration via settings.yml for API keys and model selection
- Dependencies managed through environment.yml