# ai-utils

A small Python package with helpful AI utility functions for text processing.

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

## Usage

### Import the utilities

```python
from ai_utils import (
    clean_text,
    estimate_token_count,
    safe_truncate_tokens,
    merge_context_snippets,
    split_into_chunks,
    summarise_text,
    LLMClient,
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

Safely truncate text to a maximum number of tokens without splitting words:

```python
from ai_utils import safe_truncate_tokens

# Truncate to 5 tokens (words)
text = "This is a very long sentence that needs to be shortened"
truncated = safe_truncate_tokens(text, max_tokens=5)
print(truncated)  # Output: "This is a very long"

# Short text remains unchanged
text = "Short text"
truncated = safe_truncate_tokens(text, max_tokens=10)
print(truncated)  # Output: "Short text"

# Truncate to exact token count
text = "One two three four five six"
truncated = safe_truncate_tokens(text, max_tokens=3)
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

Split long text into manageable chunks without breaking words:

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

chunks = split_into_chunks(long_text, max_tokens=15)
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: {chunk}\n")

# Output:
# Chunk 1: Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with
#
# Chunk 2: the interactions between computers and human language. In particular, how to program computers to
#
# Chunk 3: process and analyze large amounts of natural language data. The goal is a computer
# ...

# Process API responses in smaller chunks
api_response = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod"
chunks = split_into_chunks(api_response, max_tokens=5)
print(chunks)
# Output: ['Lorem ipsum dolor sit amet', 'consectetur adipiscing elit sed do', 'eiusmod']
```

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

# Step 2: Split into processable chunks
chunks = split_into_chunks(cleaned, max_tokens=10)
print(f"\nSplit into {len(chunks)} chunks")

# Step 3: Process each chunk (e.g., truncate if needed)
processed_chunks = [safe_truncate_tokens(chunk, max_tokens=8) for chunk in chunks]

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

transcript = """
This is a long transcript from an interview.
It has multiple paragraphs and sections.

The interviewer asked many questions.
The respondent gave detailed answers.

This continues for many pages...
"""

token_count = estimate_token_count(transcript)
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

# Split into chunks of approximately 100 tokens each
chunks = split_into_chunks(transcript, max_tokens=100)

print(f"Split transcript into {len(chunks)} chunks\n")

# Verify each chunk is within the limit
for i, chunk in enumerate(chunks, 1):
    token_count = estimate_token_count(chunk)
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
chunks = split_into_chunks(long_document, max_tokens=MAX_TOKENS_PER_CHUNK)

print(f"Processing {len(chunks)} chunks...")

# Process each chunk with your LLM
results = []
for i, chunk in enumerate(chunks, 1):
    print(f"\nProcessing chunk {i}/{len(chunks)}...")
    print(f"Chunk size: {estimate_token_count(chunk)} tokens")

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

# Initialize client
client = LLMClient()

# Long document to process
long_document = """
[Your long transcript or article with many paragraphs...]
"""

# Split into manageable chunks
chunks = split_into_chunks(long_document, max_tokens=2000)

print(f"Processing {len(chunks)} chunks...")

# Process each chunk
summaries = []
for i, chunk in enumerate(chunks, 1):
    print(f"\nProcessing chunk {i}/{len(chunks)} ({estimate_token_count(chunk)} tokens)...")

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
- **Monitor costs**: Use `estimate_token_count()` to estimate usage before making API calls.
- **Log errors**: Enable logging to debug issues: `logging.basicConfig(level=logging.INFO)`
- **Secure API keys**: Never commit API keys to version control. Always use environment variables or secure vaults.

## Features

### Text Processing
- **clean_text**: Normalizes whitespace, removes extra spaces, newlines, and tabs
- **estimate_token_count**: Approximates token count using whitespace splitting (for chunking, not billing)
- **safe_truncate_tokens**: Intelligently truncates text to a token limit without splitting words
- **merge_context_snippets**: Combines multiple text snippets with customizable separators
- **split_into_chunks**: Intelligently divides long text into chunks while preserving paragraph structure
- **summarise_text**: Reduces text length using sentence-based heuristics (keeps first/last sentences)

### LLM Integration
- **LLMClient**: Robust wrapper for OpenAI-compatible APIs with automatic retry logic, exponential backoff, and comprehensive error handling

## Requirements

- Python >= 3.8
- `requests` (optional, required for LLMClient only)

To install with LLM support:
```bash
pip install requests
# or
pip install git+https://github.com/RazonIn4K/ai-utils.git
pip install requests
```

## License

MIT