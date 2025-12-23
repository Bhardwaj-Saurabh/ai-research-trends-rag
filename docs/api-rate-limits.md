# API Rate Limits and Best Practices

This document outlines the rate limits for external APIs we use and how we handle them.

## Overview

Our system integrates with several external APIs that have rate limits. Respecting these limits is crucial to:
- Avoid getting blocked or banned
- Be a good API citizen
- Ensure reliable operation

## API Rate Limits

### 1. arXiv API

**Official Policy:**
- No hard rate limit, but they request a **3-second delay between requests**
- Bulk downloads should be done during off-peak hours (US night time)
- They can block IPs that make excessive requests

**Our Implementation:**
- **Minimum delay:** 3 seconds between requests
- **Max requests:** 20 per minute (conservative limit)
- **Retry logic:** 3 retries with exponential backoff
- **User-Agent:** Custom user agent identifying our application

**Best Practices:**
```python
from rate_limiter import arxiv_rate_limiter

@arxiv_rate_limiter
def fetch_from_arxiv(url):
    # This will automatically wait 3 seconds between calls
    response = requests.get(url)
    return response
```

### 2. Semantic Scholar API

**Official Limits:**

**Free Tier (No API Key):**
- **100 requests per 5 minutes** (300 seconds)
- Effectively: 1 request every 3 seconds

**With API Key:**
- **5,000 requests per 5 minutes** (300 seconds)
- Effectively: 16.67 requests per second
- Get API key at: https://www.semanticscholar.org/product/api#api-key

**Our Implementation:**
- **Free tier:** 100 requests per 5 minutes, 3-second minimum delay
- **With API key:** 5,000 requests per 5 minutes, 0.1-second minimum delay
- **Retry logic:** 3 retries with exponential backoff
- **HTTP 429 handling:** Automatic backoff on rate limit errors

**Best Practices:**
```python
from rate_limiter import semantic_scholar_rate_limiter

@semantic_scholar_rate_limiter
def enrich_paper(arxiv_id, api_key=None):
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key

    response = requests.get(
        f"https://api.semanticscholar.org/v1/paper/arXiv:{arxiv_id}",
        headers=headers
    )
    return response.json()
```

### 3. OpenAI API

**Official Limits:**
Tier-based limits (depends on your OpenAI account):

**Free Trial:**
- **RPM (Requests Per Minute):** 3
- **TPM (Tokens Per Minute):** 40,000
- **RPD (Requests Per Day):** 200

**Tier 1 ($5+ spent):**
- **RPM:** 500
- **TPM:** 60,000

**Tier 2 ($50+ spent):**
- **RPM:** 5,000
- **TPM:** 450,000

**Our Implementation:**
- Uses `tenacity` library for automatic retries
- Exponential backoff on rate limit errors
- Configurable retry attempts (default: 3)

**Best Practices:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def generate_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response['data'][0]['embedding']
```

## Rate Limiter Implementation

We've implemented a token bucket rate limiter in `scripts/rate_limiter.py`:

### Features

1. **Token Bucket Algorithm**
   - Tracks requests in a sliding time window
   - Automatically waits when limit is reached
   - Enforces minimum delay between requests

2. **Decorator Pattern**
   ```python
   @rate_limiter
   def my_api_call():
       # Rate limiting handled automatically
       pass
   ```

3. **Retry Logic**
   ```python
   @with_retry(max_retries=3, backoff=2.0)
   def fragile_api_call():
       # Automatic retries with exponential backoff
       pass
   ```

### Usage Example

```python
from rate_limiter import (
    arxiv_rate_limiter,
    semantic_scholar_rate_limiter,
    with_retry
)

@arxiv_rate_limiter
@with_retry(max_retries=3, backoff=2.0)
def fetch_papers():
    # This function will:
    # 1. Wait 3 seconds between calls
    # 2. Limit to 20 requests per minute
    # 3. Retry up to 3 times on failure
    # 4. Use exponential backoff between retries
    pass
```

## Time Estimates

### Ingesting Papers with Citations

**Scenario:** Ingest 100 papers with Semantic Scholar enrichment

**Time breakdown:**
1. **arXiv fetch:** ~3 seconds (single API call)
2. **Semantic Scholar enrichment:** ~5 minutes
   - 100 requests × 3 seconds = 300 seconds = 5 minutes
3. **Processing service:** ~2 minutes
   - 100 papers × 1 second = 100 seconds
4. **Total:** ~7-8 minutes for 100 papers

**With API Key (Semantic Scholar):**
- Semantic Scholar: ~10 seconds (100 × 0.1s)
- **Total:** ~2-3 minutes for 100 papers

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Semantic Scholar API Key (optional, increases rate limits)
SEMANTIC_SCHOLAR_API_KEY=your_api_key_here

# Processing service URL
PROCESSING_SERVICE_URL=http://localhost:8000
```

### Getting API Keys

**Semantic Scholar:**
1. Visit: https://www.semanticscholar.org/product/api#api-key
2. Sign up for a free account
3. Request an API key
4. Add to `.env`: `SEMANTIC_SCHOLAR_API_KEY=your_key`

**Benefits:**
- 50x higher rate limit (5,000 vs 100 per 5 min)
- Faster ingestion times
- Priority support

## Monitoring Rate Limits

### Check Logs

Our ingestion script logs rate limit info:

```
INFO - ⏱️  Rate limiting enabled: 3s between requests, max 20/minute
INFO - Enriching paper 1/100: 2401.12345
INFO - Rate limit reached. Waiting 12.3 seconds...
```

### Handle Rate Limit Errors

**HTTP 429 (Too Many Requests):**
- Automatic retry with exponential backoff
- Logs warning message
- Waits before retrying

## Best Practices

### 1. Use API Keys When Available
- Get Semantic Scholar API key (free)
- Reduces ingestion time significantly
- More reliable for large batches

### 2. Batch Processing
```bash
# Bad: Ingest 1,000 papers at once
python scripts/ingest_arxiv_papers_v2.py --max-results 1000

# Good: Ingest in smaller batches
for i in {1..10}; do
    python scripts/ingest_arxiv_papers_v2.py --max-results 100
    sleep 60  # Wait between batches
done
```

### 3. Off-Peak Hours
- Run large ingestions during off-peak hours
- arXiv: US night time (2 AM - 6 AM EST)
- Reduces load on their servers

### 4. Skip Citation Enrichment for Testing
```bash
# Skip Semantic Scholar enrichment (faster)
python scripts/ingest_arxiv_papers_v2.py --max-results 50 --no-citations
```

### 5. Monitor Your Usage
- Check OpenAI usage: https://platform.openai.com/usage
- Monitor logs for rate limit warnings
- Adjust batch sizes if needed

## Troubleshooting

### "Rate limit exceeded" Error

**arXiv:**
```
Error: Too many requests to arXiv API
```
**Solution:** Wait 5 minutes, then resume with smaller batches

**Semantic Scholar:**
```
HTTP 429: Too Many Requests
```
**Solution:**
1. Get an API key (recommended)
2. Or reduce batch size to 50-100 papers
3. Wait 5 minutes between batches

**OpenAI:**
```
RateLimitError: Rate limit reached
```
**Solution:**
1. Check your tier at platform.openai.com
2. Wait a minute
3. Reduce concurrent requests

### IP Blocked by arXiv

**Symptoms:** Requests timeout or return HTTP 403

**Solution:**
1. Wait 24 hours
2. Use a different IP or VPN
3. Contact arXiv support if persistent
4. Always respect the 3-second delay

## Production Deployment

### Azure Function Timer Trigger

For scheduled ingestion, use conservative limits:

```python
# Azure Function configuration
{
  "schedule": "0 0 2 * * 0",  # Weekly, Sunday 2 AM EST
  "maxConcurrentInvocations": 1,  # One at a time
  "batchSize": 100  # Conservative batch size
}
```

### Monitoring

Set up alerts for:
- Rate limit errors (HTTP 429)
- Ingestion failures
- Processing delays

## Summary

| API | Free Limit | With API Key | Min Delay | Retry Logic |
|-----|-----------|--------------|-----------|-------------|
| arXiv | 20/min | N/A | 3s | 3 retries, exp backoff |
| Semantic Scholar | 100/5min | 5,000/5min | 3s (free), 0.1s (key) | 3 retries, exp backoff |
| OpenAI | Tier-based | Tier-based | None | Built-in retry |

**Key Takeaways:**
- ✅ Always use rate limiters
- ✅ Get Semantic Scholar API key
- ✅ Monitor logs for rate limit warnings
- ✅ Use smaller batches for testing
- ✅ Schedule large ingestions during off-peak hours
