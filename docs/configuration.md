# Configuration Guide for Table-Deep-Research Agents

## Overview

The Table-Deep-Research (TDR) agents use a two-tier configuration system:
1. **Environment variables** (from `.env` file or system environment)
2. **YAML configuration files** (in `conf.d/` directory)

## Environment Variables (.env)

Create a `.env` file in the project root to set environment-specific variables:

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
vi .env
```

### Supported Variables

- `USE_GLEAN_STUB` (default: `true`) - Use stub mode for Glean API instead of real API
- `LLM_PAR` (default: `4`) - Maximum parallel LLM API calls
- `OPENAI_API_KEY` - Your OpenAI API key (required for LLM calls)

## YAML Configuration (conf.d/)

The `conf.d/table_research.yaml` file contains application settings:

```yaml
table_research:
  llm:
    model: gpt-4o-mini
    temperature: 0.1
  glean:
    use_stub: ${USE_GLEAN_STUB}  # References .env variable
  max_docs: 12
  chunk_tokens: 2048
```

### Variable Substitution

YAML files support environment variable substitution using `${VAR_NAME}` syntax:
- `${USE_GLEAN_STUB}` - Replaced with the value from `.env` or system environment
- Falls back to defaults if not set (e.g., `USE_GLEAN_STUB` defaults to `true`)

## Configuration Loading Order

1. `.env` file is loaded (if `python-dotenv` is installed)
2. System environment variables override `.env` values
3. YAML files are loaded with variable substitution
4. Default values are used for any missing variables

## Testing Different Configurations

### Run with stub mode (default):
```bash
python -m my_agents.table_research tracking.AdClickEvent
```

### Run with real Glean API:
```bash
USE_GLEAN_STUB=false python -m my_agents.table_research tracking.AdClickEvent
```

### Run tests with custom settings:
```bash
USE_GLEAN_STUB=true LLM_PAR=8 pytest tests/table_research/
```

## Best Practices

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Always provide `.env.example`** - Document all variables with defaults
3. **Use environment variables for secrets** - Never hardcode API keys
4. **Use YAML for application settings** - Model names, thresholds, etc.
5. **Document all variables** - Include descriptions and valid values 