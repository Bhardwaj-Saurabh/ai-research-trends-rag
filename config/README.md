# Configuration Files

This directory contains configuration files for the AI Research Trends RAG system.

## Files

### `example_queries.yaml`
Example queries for the frontend. These are displayed to users to help them get started.

**Structure:**
```yaml
basic_queries:
  - "Query 1"
  - "Query 2"

trend_queries:
  - "Trend query 1"

comparison_queries:
  - "Comparison query 1"
```

**Customization:**
Edit this file to add domain-specific example queries for your use case.

### `arxiv_categories.yaml`
arXiv category definitions and major AI/ML venues.

**Structure:**
```yaml
computer_science:
  cs.AI:
    name: "Artificial Intelligence"
    description: "..."

major_venues:
  - "NeurIPS"
  - "ICML"
```

**Customization:**
- Add/remove categories based on your research interests
- Update venue list for your field

## Environment Variables

All runtime configuration is managed through `.env` file. See `.env.example` for all available options.

### Key Configuration Groups

1. **API Keys**
   - OpenAI API key (required)
   - Semantic Scholar API key (optional, improves rate limits)
   - Opik API key (optional, for observability)

2. **Service URLs**
   - Processing Service
   - RAG Query Service
   - Qdrant Vector DB

3. **RAG Settings**
   - Retrieval parameters (top-k, similarity threshold)
   - LLM parameters (model, temperature, max tokens)
   - Prompt templates (can override defaults)

4. **Rate Limiting**
   - arXiv API limits
   - Semantic Scholar API limits
   - OpenAI API retry settings

5. **Feature Flags**
   - Enable/disable specific features
   - Useful for testing and gradual rollout

## Usage

### Loading Configuration

**Python services:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    # ... other settings

    class Config:
        env_file = ".env"
```

**YAML files:**
```python
import yaml

with open('config/example_queries.yaml') as f:
    queries = yaml.safe_load(f)
```

### Overriding Defaults

1. **Environment variables** (highest priority)
2. **.env file**
3. **Default values in code** (lowest priority)

Example:
```bash
# Override via environment
export RAG_TOP_K_RETRIEVAL=20

# Or in .env file
RAG_TOP_K_RETRIEVAL=20

# Or as command line arg
python script.py --top-k 20
```

## Best Practices

### 1. Never Commit Secrets
- `.env` is in `.gitignore`
- Only commit `.env.example` with placeholder values
- Use Azure Key Vault in production

### 2. Document All Options
- Add new options to `.env.example`
- Include comments explaining the option
- Provide sensible defaults

### 3. Validate Configuration
- Use Pydantic for type validation
- Fail fast if required values are missing
- Log warnings for deprecated options

### 4. Environment-Specific Configs
```
.env.development
.env.staging
.env.production
```

Load appropriate file based on `ENVIRONMENT` variable.

### 5. Prompt Engineering
- Keep prompts in separate files (`app/prompts.py`)
- Version control prompt changes
- A/B test different prompts
- Allow runtime overrides via env vars

## Customization Examples

### Custom Research Domain

If you're working in a different domain (e.g., biology, physics):

1. **Update `arxiv_categories.yaml`:**
```yaml
biology:
  q-bio.GN:
    name: "Genomics"
    description: "..."

major_venues:
  - "Nature"
  - "Cell"
```

2. **Update example queries:**
```yaml
basic_queries:
  - "What are recent advances in CRISPR technology?"
  - "Explain protein folding methods"
```

3. **Update prompts:**
```python
# In .env
RAG_SYSTEM_PROMPT=You are a biology research assistant specializing in genomics and proteomics...
```

### Custom LLM Settings

For different use cases:

**High accuracy (slower, more expensive):**
```bash
OPENAI_CHAT_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=4000
RAG_TOP_K_RETRIEVAL=15
```

**Fast responses (cheaper):**
```bash
OPENAI_CHAT_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
RAG_TOP_K_RETRIEVAL=5
```

## Validation

Run configuration validation:

```bash
# Check all required env vars are set
python scripts/validate_config.py

# Test loading all config files
python scripts/test_config.py
```

## Migration

When updating configuration:

1. Add new option to `.env.example`
2. Update `config.py` with new field
3. Document in this README
4. Add backward compatibility if needed
5. Update deployment scripts

## Security Notes

**Sensitive Values:**
- API keys
- Database passwords
- Connection strings

**Protection:**
- Store in Azure Key Vault (production)
- Use environment variables (development)
- Never log sensitive values
- Rotate keys regularly

**Example (using Key Vault):**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url=os.getenv("KEY_VAULT_URL"), credential=credential)

openai_key = client.get_secret("openai-api-key").value
```

## Troubleshooting

### Missing Configuration

**Error:** `ValidationError: OPENAI_API_KEY field required`

**Solution:**
```bash
# Check .env exists
ls -la .env

# Check value is set
grep OPENAI_API_KEY .env

# Verify it's loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### YAML Parse Errors

**Error:** `yaml.scanner.ScannerError`

**Solution:**
- Check YAML syntax (indentation, quotes)
- Validate with: `yamllint config/*.yaml`

### Wrong Values Loaded

**Error:** Configuration not updating

**Solution:**
- Restart services after changing .env
- Check environment variable precedence
- Clear cached settings (@lru_cache)

## References

- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [PyYAML](https://pyyaml.org/)
- [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/)
