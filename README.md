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
    safe_truncate_tokens,
    merge_context_snippets,
    split_into_chunks,
    summarise_text,
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

## Features

- **clean_text**: Normalizes whitespace, removes extra spaces, newlines, and tabs
- **safe_truncate_tokens**: Intelligently truncates text to a token limit without splitting words
- **merge_context_snippets**: Combines multiple text snippets with customizable separators
- **split_into_chunks**: Divides long text into smaller chunks of specified token length
- **summarise_text**: Reduces text length using sentence-based heuristics (keeps first/last sentences)

## Requirements

- Python >= 3.8

## License

MIT