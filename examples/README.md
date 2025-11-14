# AI-Utils Examples

This directory contains practical examples demonstrating how to use the ai-utils library.

## Running the Examples

Make sure you have ai-utils installed:

```bash
pip install -e .
```

For LLM client examples, install with the `llm` extra:

```bash
pip install -e ".[llm]"
```

Then run any example:

```bash
python examples/01_text_processing.py
python examples/02_chunking_long_text.py
python examples/03_llm_client_usage.py
python examples/04_json_extraction.py
```

## Example Descriptions

### 01_text_processing.py
Basic text processing utilities:
- Cleaning messy text
- Estimating token counts
- Safe token truncation
- Merging context snippets

### 02_chunking_long_text.py
Document chunking techniques:
- Basic text chunking
- Paragraph-aware chunking
- Processing long transcripts
- Handling very long paragraphs
- Optimal chunk sizes for different use cases

### 03_llm_client_usage.py
LLM client wrapper demonstrations:
- Basic API calls with retry logic
- Processing document chunks
- Error handling
- Working with different providers (OpenAI, Azure, local models)

**Note**: Requires valid API credentials. Set environment variables:
```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4"
export LLM_API_KEY="your-key-here"
```

### 04_json_extraction.py
Safe JSON extraction from LLM responses:
- Extracting clean JSON
- Handling JSON with explanatory text
- Markdown code block extraction
- Multiple JSON objects
- Default fallbacks for invalid JSON
- Nested complex JSON
- Production error handling

## Tips

1. **Start simple**: Begin with `01_text_processing.py` to understand the basics
2. **Study chunking**: `02_chunking_long_text.py` is crucial for working with long documents
3. **API credentials**: For `03_llm_client_usage.py`, use environment variables or a `.env` file
4. **Combine utilities**: Most real-world use cases combine multiple functions

## Common Workflows

### Workflow 1: Processing a long document with an LLM

```python
from ai_utils import split_into_chunks, LLMClient, safe_extract_json

# 1. Split document
chunks = split_into_chunks(long_document, max_tokens=2000)

# 2. Process each chunk
client = LLMClient()
results = []
for chunk in chunks:
    response = client.generate(f"Analyze: {chunk}")
    data = safe_extract_json(response, default={})
    results.append(data)

# 3. Combine results
final_result = combine_results(results)
```

### Workflow 2: Cleaning and preparing text for embeddings

```python
from ai_utils import clean_text, split_into_chunks

# 1. Clean the text
cleaned = clean_text(raw_text)

# 2. Split into embedding-sized chunks
chunks = split_into_chunks(cleaned, max_tokens=500)

# 3. Generate embeddings
embeddings = [create_embedding(chunk) for chunk in chunks]
```

### Workflow 3: Extracting structured data from LLM responses

```python
from ai_utils import LLMClient, safe_extract_json, configure_logging

# Configure logging
logger = configure_logging(level='INFO')

# Make LLM call
client = LLMClient()
response = client.generate("Extract entities from: ..." )

# Safely extract JSON
entities = safe_extract_json(response, default={})
logger.info(f"Extracted {len(entities)} entities")
```
