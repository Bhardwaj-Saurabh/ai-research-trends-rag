#!/usr/bin/env python3
"""
Configuration validation script.

Validates that all required environment variables are set and configuration
files are properly formatted.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_success(message):
    """Print success message in green."""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    """Print error message in red."""
    print(f"{RED}✗{RESET} {message}")


def print_warning(message):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠{RESET} {message}")


def check_required_env_vars():
    """Check that all required environment variables are set."""
    print("\n" + "="*60)
    print("Checking Required Environment Variables")
    print("="*60 + "\n")

    required_vars = [
        ("OPENAI_API_KEY", "OpenAI API key for embeddings and chat"),
    ]

    optional_vars = [
        ("SEMANTIC_SCHOLAR_API_KEY", "Semantic Scholar API key (improves rate limits)"),
        ("OPIK_API_KEY", "Opik API key for LLM observability"),
        ("COSMOS_ENDPOINT", "Azure Cosmos DB endpoint"),
        ("COSMOS_KEY", "Azure Cosmos DB key"),
    ]

    all_valid = True

    # Check required variables
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if not value or value.startswith("your_"):
            print_error(f"{var_name}: NOT SET")
            print(f"         {description}")
            all_valid = False
        else:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print_success(f"{var_name}: {masked_value}")

    print()

    # Check optional variables
    print("Optional Variables:")
    for var_name, description in optional_vars:
        value = os.getenv(var_name)
        if not value or value.startswith("your_"):
            print_warning(f"{var_name}: Not set (optional)")
        else:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print_success(f"{var_name}: {masked_value}")

    return all_valid


def check_config_files():
    """Check that configuration files exist and are valid."""
    print("\n" + "="*60)
    print("Checking Configuration Files")
    print("="*60 + "\n")

    config_files = [
        "config/example_queries.yaml",
        "config/arxiv_categories.yaml",
    ]

    all_valid = True

    for config_file in config_files:
        filepath = project_root / config_file

        if not filepath.exists():
            print_error(f"{config_file}: File not found")
            all_valid = False
            continue

        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)

            print_success(f"{config_file}: Valid YAML")

            # Additional validation for specific files
            if "example_queries.yaml" in config_file:
                if "basic_queries" not in data:
                    print_warning(f"  Missing 'basic_queries' section")
                else:
                    print(f"  Found {len(data['basic_queries'])} basic queries")

            if "arxiv_categories.yaml" in config_file:
                if "computer_science" not in data:
                    print_warning(f"  Missing 'computer_science' section")
                else:
                    cs_cats = len(data['computer_science'])
                    print(f"  Found {cs_cats} computer science categories")

        except yaml.YAMLError as e:
            print_error(f"{config_file}: Invalid YAML")
            print(f"  Error: {str(e)}")
            all_valid = False
        except Exception as e:
            print_error(f"{config_file}: Error reading file")
            print(f"  Error: {str(e)}")
            all_valid = False

    return all_valid


def check_service_configs():
    """Check that service configuration files are valid."""
    print("\n" + "="*60)
    print("Checking Service Configurations")
    print("="*60 + "\n")

    services = [
        ("services/processing-service/app/config.py", "Processing Service"),
        ("services/rag-query-service/app/config.py", "RAG Query Service"),
        ("services/frontend/config.py", "Frontend"),
    ]

    all_valid = True

    for config_path, service_name in services:
        filepath = project_root / config_path

        if not filepath.exists():
            print_error(f"{service_name}: Config file not found")
            all_valid = False
            continue

        try:
            # Try to import and instantiate settings
            # This will fail if there are syntax errors or missing required env vars

            if "processing-service" in config_path:
                sys.path.insert(0, str(filepath.parent.parent))
                from app.config import Settings
                settings = Settings()
                print_success(f"{service_name}: Configuration valid")
                print(f"  Qdrant URL: {settings.qdrant_url}")
                print(f"  Embedding model: {settings.openai_embedding_model}")

            elif "rag-query-service" in config_path:
                sys.path.insert(0, str(filepath.parent.parent))
                from app.config import Settings
                settings = Settings()
                print_success(f"{service_name}: Configuration valid")
                print(f"  Chat model: {settings.openai_chat_model}")
                print(f"  Top-k retrieval: {settings.top_k_retrieval}")

        except Exception as e:
            print_error(f"{service_name}: Configuration error")
            print(f"  Error: {str(e)}")
            all_valid = False

    return all_valid


def check_prompts():
    """Check that prompt templates are valid."""
    print("\n" + "="*60)
    print("Checking Prompt Templates")
    print("="*60 + "\n")

    prompts_file = project_root / "services/rag-query-service/app/prompts.py"

    if not prompts_file.exists():
        print_error("Prompts file not found")
        return False

    try:
        sys.path.insert(0, str(prompts_file.parent.parent))
        from app.prompts import PromptTemplates

        # Check that key templates exist
        templates = [
            "SYSTEM_PROMPT",
            "RAG_PROMPT_TEMPLATE",
            "TREND_PROMPT_TEMPLATE",
            "COMPARISON_PROMPT_TEMPLATE"
        ]

        for template_name in templates:
            if hasattr(PromptTemplates, template_name):
                template = getattr(PromptTemplates, template_name)
                preview = template[:50] + "..." if len(template) > 50 else template
                print_success(f"{template_name}: Defined")
                print(f"  Preview: {preview}")
            else:
                print_error(f"{template_name}: Not found")
                return False

        return True

    except Exception as e:
        print_error(f"Error loading prompts: {str(e)}")
        return False


def main():
    """Run all validation checks."""
    print("\n" + "="*60)
    print("AI Research Trends RAG - Configuration Validation")
    print("="*60)

    checks = [
        ("Environment Variables", check_required_env_vars),
        ("Configuration Files", check_config_files),
        ("Prompt Templates", check_prompts),
    ]

    # Skip service config checks if OpenAI key is not set
    # (will fail anyway)
    if os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY").startswith("your_"):
        checks.append(("Service Configurations", check_service_configs))

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Unexpected error in {check_name}: {str(e)}")
            results.append((check_name, False))

    # Summary
    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60 + "\n")

    all_passed = all(result for _, result in results)

    for check_name, result in results:
        if result:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")

    print()

    if all_passed:
        print_success("All validation checks passed! ✓")
        print("\nYou can now start the services:")
        print("  1. Start Qdrant: docker-compose up -d qdrant")
        print("  2. Start Processing Service: cd services/processing-service && uvicorn main:app --reload")
        print("  3. Start RAG Service: cd services/rag-query-service && uvicorn main:app --reload --port 8001")
        print("  4. Start Frontend: cd services/frontend && streamlit run app.py")
        return 0
    else:
        print_error("Some validation checks failed.")
        print("\nPlease fix the issues above before starting the services.")
        print("See docs/local-testing-guide.md for help.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
