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
from ai_utils import clean_text, safe_truncate_tokens, merge_context_snippets
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

## Features

- **clean_text**: Normalizes whitespace, removes extra spaces, newlines, and tabs
- **safe_truncate_tokens**: Intelligently truncates text to a token limit without splitting words
- **merge_context_snippets**: Combines multiple text snippets with customizable separators

## Requirements

- Python >= 3.8

## License

MIT