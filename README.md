# ai-utils

[![PyPI - Git Install](https://img.shields.io/badge/PyPI-git--install-2ba84a)](#installation)

A small Python package with helpful AI utility functions for text processing.

**This repo is part of my Upwork portfolio for general automation scripting, token management, and AI workflow utilities.**

---

## 🚀 Quick Demo

**Prerequisites:**
- Python 3.8+
- No API keys needed (utilities work offline)

**Run the demo:**
```bash
# Install the package
pip install -e .

# Run the text processing example
python examples/01_text_processing.py
```

**Expected Output:**
```
============================================================
TEXT PROCESSING EXAMPLES
============================================================

1. CLEANING MESSY TEXT
------------------------------------------------------------
Original: '\n        This is   some text    with\n\n\n        irregular    spacing...'
Cleaned: This is some text with irregular spacing and tabs everywhere!

2. ESTIMATING TOKEN COUNTS
------------------------------------------------------------
  3 tokens: Hello world!
 10 tokens: This is a longer sentence with more words.
  8 tokens: AI and ML are transforming technology.

3. SAFE TOKEN TRUNCATION
------------------------------------------------------------
Max 3 tokens (3 actual): The quick brown
Max 5 tokens (5 actual): The quick brown fox jumps
...
```

**What this proves:**
- Text cleaning and normalization utilities
- Token counting for LLM cost estimation
- Safe truncation for automation guardrails
- Perfect for general automation scripting jobs where clients need token management and text processing utilities

**Next Steps:**
- See `examples/` directory for more demos
- See `docs/upwork/UPWORK_AUTOMATION_SCRIPTS.md` for Upwork summary

---

## Installation

You can install the package directly from the repository:

```bash
pip install git+https://github.com/RazonIn4K/ai-utils.git
```

Or install it in development mode:

```bash
git clone https://github.com/RazonIn4K/ai-utils.git
cd ai-utils
pip install -e .
```

### Installing from PyPI

The project is structured for PyPI distribution. Once the package is published,
you will be able to install it via:

```bash
pip install ai-utils
```

## Common Use Cases

### Automation guardrails

Ensure outbound automation or agent responses stay within a safe token budget before posting to chat tools or CRMs:

```python
from ai_utils import estimate_token_count, safe_truncate_tokens

AUTOMATION_MODEL = "gpt-3.5-turbo"

def prepare_update(message: str) -> str:
    tokens = estimate_token_count(message, model=AUTOMATION_MODEL)
    if tokens <= 350:
        return message

    return safe_truncate_tokens(
        message,
        max_tokens=350,
        model=AUTOMATION_MODEL,
    )
```

### Retrieval pipelines

Chunk source documents with overlaps so downstream embeddings or rerankers keep sufficient context:

```python
from ai_utils import split_into_chunks, estimate_token_count

RAG_MODEL = "gpt-3.5-turbo"

def build_chunks(document: str) -> list[str]:
    chunks = split_into_chunks(
        document,
        max_tokens=350,
        overlap_tokens=50,
        model=RAG_MODEL,
    )
    return [c for c in chunks if estimate_token_count(c, model=RAG_MODEL) >= 10]
```

## Integration Recipes

### chatbot-templates

Use overlapping chunks to populate chatbot-templates memory stores and apply safe
truncation before each outbound response:

```python
from ai_utils import split_into_chunks, safe_truncate_tokens

SYSTEM_MODEL = "gpt-4o-mini"

def hydrate_template(transcript: str) -> list[str]:
    chunks = split_into_chunks(transcript, max_tokens=400, overlap_tokens=60, model=SYSTEM_MODEL)
    safe_chunks = [safe_truncate_tokens(chunk, max_tokens=380, model=SYSTEM_MODEL) for chunk in chunks]
    return safe_chunks
```

### csbrainai

csbrainai expects chunk metadata and cost estimates before storing passages.
Combine chunking, token counting, and the cost helper to enforce ingestion budgets:

```python
from ai_utils import split_into_chunks, estimate_token_count, estimate_llm_cost

MODEL = "gpt-3.5-turbo"

def prepare_csbrainai_payload(document: str) -> list[dict]:
    payload = []
    for chunk in split_into_chunks(document, max_tokens=300, overlap_tokens=40, model=MODEL):
        payload.append({
            "content": chunk,
            "tokens": estimate_token_count(chunk, model=MODEL),
            "estimated_cost": estimate_llm_cost(chunk, model=MODEL, expected_response_tokens=100),
        })
    return payload
```

### automation-templates

automation-templates workflows often fan out across multiple downstream calls.
Estimate the cost of each step before dispatching background jobs:

```python
from ai_utils import estimate_token_count, estimate_llm_cost

AUTOMATION_MODEL = "gpt-4o"

def enforce_budget(task: dict) -> None:
    prompt = task["prompt"]
    tokens = estimate_token_count(prompt, model=AUTOMATION_MODEL)
    projected = estimate_llm_cost(prompt, model=AUTOMATION_MODEL, expected_response_tokens=tokens // 2)
    if projected > task.get("max_cost", 0.10):
        raise ValueError("Projected automation cost exceeds ceiling")
```

### data-pipeline-starters

Before large backfills, data-pipeline-starters can simulate spend by chunking
each document and summing anticipated LLM calls:

```python
from ai_utils import split_into_chunks, estimate_llm_cost

PIPELINE_MODEL = "gpt-4o-mini"

def plan_ingest(documents: list[str]) -> float:
    total_cost = 0.0
    for doc in documents:
        for chunk in split_into_chunks(doc, max_tokens=500, overlap_tokens=80, model=PIPELINE_MODEL):
            total_cost += estimate_llm_cost(chunk, model=PIPELINE_MODEL, expected_response_tokens=200)
    return total_cost
```

### Integrating with ops/reporting stack

The cost dashboard (`examples/05_cost_dashboard.py`) can emit summaries as
human-readable text, CSV, or JSON via `--output-format` and `--output-path`, so
you can feed spend data directly into ops-hub, Looker, or other reporting tools.

## Usage

### Import the utilities

```python
from ai_utils import (
    # Text processing
    clean_text,
    estimate_token_count,
    safe_truncate_tokens,
    merge_context_snippets,
    split_into_chunks,
    summarise_text,
    # LLM integration
    LLMClient,
    # Additional helpers
    safe_extract_json,
    configure_logging,
    retry_with_backoff,
)
```

### clean_text

Clean and normalize text by removing extra whitespace and newlines:

```python
from ai_utils import clean_text

# Remove extra whitespace
text = "  Hello   World!  "
cleaned = clean_text(text)
print(cleaned)  # Output: "Hello World!"

# Normalize newlines and tabs
text = "Multiple\n\nlines\n\nhere"
cleaned = clean_text(text)
print(cleaned)  # Output: "Multiple lines here"
```

### safe_truncate_tokens

Safely truncate text to a maximum number of tokens without splitting words. Pass
the target `model` so the heuristic matches your deployment:

```python
from ai_utils import safe_truncate_tokens

# Truncate to 5 tokens (words)
text = "This is a very long sentence that needs to be shortened"
MODEL = "gpt-3.5-turbo"
truncated = safe_truncate_tokens(text, max_tokens=5, model=MODEL)
print(truncated)  # Output: "This is a very long"

# Short text remains unchanged
text = "Short text"
truncated = safe_truncate_tokens(text, max_tokens=10, model=MODEL)
print(truncated)  # Output: "Short text"

# Truncate to exact token count
text = "One two three four five six"
truncated = safe_truncate_tokens(text, max_tokens=3, model=MODEL)
print(truncated)  # Output: "One two three"
```

### merge_context_snippets

Merge multiple context snippets into a single string:

```python
from ai_utils import merge_context_snippets

# Merge with default separator (double newline)
snippets = ["First context snippet", "Second context snippet", "Third snippet"]
merged = merge_context_snippets(snippets)
print(merged)
# Output:
# First context snippet
#
# Second context snippet
#
# Third snippet

# Use custom separator
snippets = ["Hello", "World", "Python"]
merged = merge_context_snippets(snippets, separator=" | ")
print(merged)  # Output: "Hello | World | Python"

# Empty snippets are automatically filtered out
snippets = ["Content 1", "", "Content 2", "   ", "Content 3"]
merged = merge_context_snippets(snippets, separator="\n---\n")
print(merged)
# Output:
# Content 1
# ---
# Content 2
# ---
# Content 3
```

### split_into_chunks

Split long text into manageable chunks without breaking words. Provide an
`overlap_tokens` budget to include trailing context in the next chunk:

```python
from ai_utils import split_into_chunks

# Split a long document into chunks of 50 tokens each
long_text = """
Natural language processing (NLP) is a subfield of linguistics, computer science,
and artificial intelligence concerned with the interactions between computers and
human language. In particular, how to program computers to process and analyze
large amounts of natural language data. The goal is a computer capable of
understanding the contents of documents, including the contextual nuances of
the language within them.
"""

chunks = split_into_chunks(long_text, max_tokens=15, overlap_tokens=5, model="gpt-3.5-turbo")
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: {chunk}\n")

# Output:
# Chunk 1: Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with
#
# Chunk 2: the interactions between computers and human language. In particular, how to program computers to
#
# Chunk 3: process and analyze large amounts of natural language data. The goal is a computer
# ...

# Process API responses in smaller chunks with lightweight overlap
api_response = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod"
chunks = split_into_chunks(api_response, max_tokens=5, overlap_tokens=1)
print(chunks)
# Output: ['Lorem ipsum dolor sit amet', 'consectetur adipiscing elit sed do', 'eiusmod']
```

### estimate_llm_cost

Approximate the USD cost for a request using heuristic token counts and
model-specific pricing. Combine with scheduling data to forecast monthly spend:

```python
from ai_utils import estimate_llm_cost

prompt = "Summarize the most recent customer transcript in 5 bullet points."
cost = estimate_llm_cost(prompt, model="gpt-4o", expected_response_tokens=200)
print(f"Estimated cost: ${cost:.4f}")

# Forecast monthly spend for a workflow
REQUESTS_PER_DAY = 200
WORKING_DAYS = 22
monthly_cost = cost * REQUESTS_PER_DAY * WORKING_DAYS
print(f"Projected monthly spend: ${monthly_cost:.2f}")

# See examples/05_cost_dashboard.py for a CSV-driven dashboard demo.
```

### Updating pricing configuration

Pricing defaults live in `ai_utils/pricing_config.json`. To override them without
touching code, edit that file (when working from source) or point the
`AI_UTILS_PRICING_CONFIG` environment variable to a JSON file with the structure:

```json
{
  "models": {
    "gpt-4.5": {"input": 0.012, "output": 0.036},
    "new-model": {"input": 0.001, "output": 0.002}
  }
}
```

The overrides are merged with the built-in defaults, so you only need to list
new models or pricing updates when vendors release changes.

### summarise_text

Reduce text length using smart heuristics that preserve important content:

```python
from ai_utils import summarise_text

# Summarize a long paragraph by keeping first and last sentences
long_paragraph = """
Climate change is one of the most pressing issues of our time. Scientists have been
studying this phenomenon for decades. The evidence shows rising global temperatures.
Ice caps are melting at unprecedented rates. Sea levels continue to rise steadily.
Many species face extinction due to habitat loss. Urgent action is needed now.
"""

summary = summarise_text(long_paragraph, max_chars=100)
print(summary)
# Output: "Climate change is one of the most pressing issues of our time. ... Urgent action is needed now."

# Works well with shorter character limits
article_intro = "The new technology promises to revolutionize healthcare. Researchers are excited."
short_summary = summarise_text(article_intro, max_chars=50)
print(short_summary)
# Output: "The new technology ... are excited."

# Preserves short text unchanged
short_text = "Brief message here."
summary = summarise_text(short_text, max_chars=100)
print(summary)  # Output: "Brief message here."
```

### Combining Multiple Functions

Here's a practical example using multiple utilities together:

```python
from ai_utils import (
    clean_text,
    split_into_chunks,
    merge_context_snippets,
    safe_truncate_tokens,
    summarise_text,
)

MODEL = "gpt-3.5-turbo"

# Process a messy document
raw_text = """
    This is   a document with    irregular spacing.


    It has multiple    paragraphs with      inconsistent formatting.
    We want to clean    and process it.
"""

# Step 1: Clean the text
cleaned = clean_text(raw_text)
print("Cleaned:", cleaned)
# Output: "This is a document with irregular spacing. It has multiple paragraphs with inconsistent formatting. We want to clean and process it."

# Step 2: Split into processable chunks with overlap
chunks = split_into_chunks(cleaned, max_tokens=10, overlap_tokens=2, model=MODEL)
print(f"\nSplit into {len(chunks)} chunks")

# Step 3: Process each chunk (e.g., truncate if needed)
processed_chunks = [safe_truncate_tokens(chunk, max_tokens=8, model=MODEL) for chunk in chunks]

# Step 4: Merge back together with custom separator
final_text = merge_context_snippets(processed_chunks, separator=" [...] ")
print("\nFinal:", final_text)

# Step 5: Create a summary if still too long
if len(final_text) > 100:
    summary = summarise_text(final_text, max_chars=100)
    print("\nSummary:", summary)
```

## Working with long texts

When processing long documents like transcripts, articles, or books, you often need to split them into chunks that fit within LLM context windows. The `estimate_token_count` and `split_into_chunks` functions work together to handle this intelligently.

### Estimating token counts

Use `estimate_token_count` to get a rough approximation of how many tokens are in your text. This is useful for planning your chunking strategy, but remember it's not exact for billing purposes.

```python
from ai_utils import estimate_token_count

MODEL = "gpt-3.5-turbo"

transcript = """
This is a long transcript from an interview.
It has multiple paragraphs and sections.

The interviewer asked many questions.
The respondent gave detailed answers.

This continues for many pages...
"""

token_count = estimate_token_count(transcript, model=MODEL)
print(f"Estimated tokens: {token_count}")
# Output: Estimated tokens: 26
```

### Splitting long documents into chunks

The `split_into_chunks` function intelligently divides long text into manageable pieces while preserving paragraph structure. It splits on double-newlines (paragraph breaks) when possible, and only falls back to word-based splitting when individual paragraphs exceed the token limit.

```python
from ai_utils import split_into_chunks, estimate_token_count

# Sample long transcript
transcript = """
Speaker 1: Welcome to today's discussion about artificial intelligence and its impact on society. We have several experts joining us to share their insights.

Speaker 2: Thank you for having me. I think AI is transforming every industry we can think of, from healthcare to transportation. The pace of change is unprecedented.

Speaker 1: That's a great point. Can you elaborate on the healthcare applications?

Speaker 2: Certainly. In healthcare, AI is being used for diagnostic imaging, drug discovery, and personalized treatment plans. Machine learning models can now detect diseases earlier and more accurately than ever before.

Speaker 3: I'd like to add that we also need to consider the ethical implications. As AI systems become more powerful, we must ensure they're used responsibly and don't perpetuate existing biases.

Speaker 1: Absolutely. Ethics and governance are critical topics. How do you think we should approach regulation?

Speaker 3: It's a delicate balance. We need frameworks that protect people while still allowing innovation to flourish. Different countries are taking different approaches, and we're still learning what works best.
"""

# Split into chunks of approximately 100 tokens each with overlap
chunks = split_into_chunks(transcript, max_tokens=100, overlap_tokens=20, model=MODEL)

print(f"Split transcript into {len(chunks)} chunks\n")

# Verify each chunk is within the limit
for i, chunk in enumerate(chunks, 1):
    token_count = estimate_token_count(chunk, model=MODEL)
    print(f"Chunk {i}: {token_count} tokens")
    print(f"Preview: {chunk[:100]}...\n")
```

### Processing chunks with an LLM

Here's a complete example showing how to process a long document with an LLM by chunking it first:

```python
from ai_utils import split_into_chunks, estimate_token_count

# Your long document
long_document = """
[Imagine this is a 50-page transcript or article with many paragraphs...]

Paragraph 1 content here.

Paragraph 2 content here.

Paragraph 3 content here.
[... many more paragraphs ...]
"""

# Split into chunks that fit within your LLM's context window
# For example, if you want to leave room for prompts and responses,
# you might use a conservative limit like 2000 tokens per chunk
MAX_TOKENS_PER_CHUNK = 2000
OVERLAP = 200
chunks = split_into_chunks(
    long_document,
    max_tokens=MAX_TOKENS_PER_CHUNK,
    overlap_tokens=OVERLAP,
    model=MODEL,
)

print(f"Processing {len(chunks)} chunks...")

# Process each chunk with your LLM
results = []
for i, chunk in enumerate(chunks, 1):
    print(f"\nProcessing chunk {i}/{len(chunks)}...")
    print(f"Chunk size: {estimate_token_count(chunk, model=MODEL)} tokens")

    # Example: Call your LLM API
    # This is pseudocode - replace with your actual LLM API call
    # response = llm_api.complete(
    #     prompt=f"Summarize the following text:\n\n{chunk}",
    #     max_tokens=150
    # )

    # For demonstration purposes:
    response = f"Summary of chunk {i}: [LLM response would go here]"
    results.append(response)

    print(f"Response: {response}")

# Combine results if needed
print(f"\n{'='*50}")
print("All summaries:")
for i, result in enumerate(results, 1):
    print(f"{i}. {result}")
```

The key benefits of this approach:

- **Preserves structure**: Paragraph boundaries are maintained when possible, keeping related content together
- **Flexible**: Works with any LLM by letting you specify the token limit
- **Efficient**: Only splits paragraphs when absolutely necessary
- **Predictable**: Each chunk respects the token limit, preventing API errors

## Using the LLMClient

The `LLMClient` class provides a robust wrapper for OpenAI-compatible API endpoints with automatic retry logic and comprehensive error handling.

### Configuration

The client reads configuration from environment variables:

```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4"
export LLM_API_KEY="your-api-key-here"
```

You can also override these settings when creating the client:

```python
from ai_utils import LLMClient

# Using environment variables
client = LLMClient()

# Or override specific settings
client = LLMClient(
    base_url="https://api.anthropic.com/v1",
    model="claude-3-sonnet-20240229",
    api_key="your-key-here"
)
```

### Basic usage

```python
from ai_utils import LLMClient

# Initialize the client
client = LLMClient()

# Generate a response
response = client.generate("What is the capital of France?")
print(response)
# Output: "The capital of France is Paris."

# With additional parameters
response = client.generate(
    "Explain machine learning in simple terms",
    temperature=0.7,
    max_tokens=200
)
print(response)
```

### Retry logic and error handling

The client automatically retries failed requests with exponential backoff:

```python
import logging
from ai_utils import LLMClient

# Enable logging to see retry attempts
logging.basicConfig(level=logging.INFO)

client = LLMClient(max_retries=5, initial_retry_delay=2.0)

try:
    response = client.generate("Your prompt here")
    print(response)
except Exception as e:
    print(f"All retries failed: {e}")
```

### Processing chunks with LLMClient

Combine chunking with LLM processing for long documents:

```python
from ai_utils import split_into_chunks, estimate_token_count, LLMClient
import os

# Set up environment
os.environ['LLM_BASE_URL'] = 'https://api.openai.com/v1'
os.environ['LLM_MODEL'] = 'gpt-4'
os.environ['LLM_API_KEY'] = 'your-api-key'
MODEL = os.environ['LLM_MODEL']

# Initialize client
client = LLMClient()

# Long document to process
long_document = """
[Your long transcript or article with many paragraphs...]
"""

# Split into manageable chunks with a 200-token overlap
chunks = split_into_chunks(long_document, max_tokens=2000, overlap_tokens=200, model=MODEL)

print(f"Processing {len(chunks)} chunks...")

# Process each chunk
summaries = []
for i, chunk in enumerate(chunks, 1):
    print(f"\nProcessing chunk {i}/{len(chunks)} ({estimate_token_count(chunk, model=MODEL)} tokens)...")

    try:
        summary = client.generate(
            f"Summarize the following text concisely:\n\n{chunk}",
            temperature=0.3,
            max_tokens=150
        )
        summaries.append(summary)
        print(f"✓ Chunk {i} summarized")
    except Exception as e:
        print(f"✗ Chunk {i} failed: {e}")
        summaries.append(f"[Error processing chunk {i}]")

# Combine all summaries
final_summary = "\n\n".join(summaries)
print("\n" + "="*50)
print("FINAL SUMMARY:")
print(final_summary)
```

### Working with different LLM providers

The client works with any OpenAI-compatible API:

```python
from ai_utils import LLMClient

# OpenAI
openai_client = LLMClient(
    base_url="https://api.openai.com/v1",
    model="gpt-4-turbo-preview",
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Azure OpenAI
azure_client = LLMClient(
    base_url="https://your-resource.openai.azure.com/openai/deployments",
    model="gpt-4",
    api_key=os.environ.get("AZURE_OPENAI_KEY")
)

# Local model (e.g., via LM Studio, Ollama with OpenAI compatibility)
local_client = LLMClient(
    base_url="http://localhost:1234/v1",
    model="local-model",
    api_key="not-needed"  # Local models often don't need a key
)

# Use any client the same way
response = openai_client.generate("Hello!")
```

### Best practices

- **Set appropriate timeouts**: The default timeout is 60 seconds. Adjust if needed for longer requests.
- **Handle rate limits**: The client automatically retries on 429 errors with exponential backoff.
- **Monitor costs**: Use `estimate_token_count(text, model=...)` and `estimate_llm_cost(...)` to approximate usage before making API calls.
- **Log errors**: Enable logging to debug issues: `logging.basicConfig(level=logging.INFO)`
- **Secure API keys**: Never commit API keys to version control. Always use environment variables or secure vaults.

## Features

### Text Processing
- **clean_text**: Normalizes whitespace, removes extra spaces, newlines, and tabs
- **estimate_token_count**: Approximates token count using whitespace + model heuristics (chunking guardrail)
- **safe_truncate_tokens**: Intelligently truncates text to a token limit using sentence-first heuristics
- **merge_context_snippets**: Combines multiple text snippets with customizable separators
- **split_into_chunks**: Intelligently divides long text into chunks while preserving paragraph structure
- **summarise_text**: Reduces text length using sentence-based heuristics (keeps first/last sentences)
- **estimate_llm_cost**: Forecasts per-request USD costs using heuristics and model pricing tables

### LLM Integration
- **LLMClient**: Robust wrapper for OpenAI-compatible APIs with automatic retry logic, exponential backoff, and comprehensive error handling

### Additional Helpers
- **safe_extract_json**: Intelligently extract JSON from LLM responses that may contain additional text or markdown formatting
- **configure_logging**: Quick logging setup with sensible defaults for AI workflows
- **retry_with_backoff**: Decorator for adding retry logic with exponential backoff to any function

## Developer Experience

- Fully typed public APIs with descriptive docstrings so IDEs (PyCharm, VS Code) and static analyzers (pyright, mypy) surface completions and doc hints in-line.

## Testing

This package includes comprehensive unit tests with >90% coverage.

### Running Tests

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=ai_utils --cov-report=html

# Run specific test file
pytest tests/test_text_processing.py

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_clean"
```

### Test Structure

```
tests/
├── test_text_processing.py  # Tests for text utilities
├── test_llm_client.py        # Tests for LLMClient (requires requests)
└── test_helpers.py           # Tests for additional helpers
```

Tests cover:
- ✅ All core functions with typical inputs
- ✅ Edge cases (empty strings, whitespace-only, very long text)
- ✅ Unicode and multilingual text (emoji, Chinese, Arabic, Russian)
- ✅ Error handling (type errors, value errors)
- ✅ LLM client retry logic and error scenarios
- ✅ JSON extraction from various formats

## Examples

Check out the `examples/` directory for practical demonstrations:

- `01_text_processing.py` - Basic text utilities
- `02_chunking_long_text.py` - Document chunking techniques
- `03_llm_client_usage.py` - LLM client with retry logic
- `04_json_extraction.py` - Extracting JSON from LLM responses

Run any example:
```bash
python examples/01_text_processing.py
```

## Requirements

- Python >= 3.8
- `requests` (optional, required for LLMClient only)

### Installation

Install the base package:
```bash
pip install git+https://github.com/RazonIn4K/ai-utils.git
```

With LLM client support:
```bash
pip install "git+https://github.com/RazonIn4K/ai-utils.git#egg=ai-utils[llm]"
```

For development:
```bash
git clone https://github.com/RazonIn4K/ai-utils.git
cd ai-utils
pip install -e ".[dev]"
```

## Publishing to PyPI

To publish this package to PyPI:

1. Update version in `pyproject.toml`
2. Build the package:
   ```bash
   python -m build
   ```
3. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Submit a pull request

## License

MIT
