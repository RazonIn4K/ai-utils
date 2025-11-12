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
from ai_utils import clean_text, safe_truncate
```

### clean_text

Clean and normalize text by removing extra whitespace:

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

### safe_truncate

Safely truncate text to a maximum length with word boundary awareness:

```python
from ai_utils import safe_truncate

# Truncate long text
text = "This is a very long sentence that needs to be shortened"
truncated = safe_truncate(text, max_length=20)
print(truncated)  # Output: "This is a very..."

# Short text remains unchanged
text = "Short text"
truncated = safe_truncate(text, max_length=20)
print(truncated)  # Output: "Short text"

# Custom suffix
text = "This is a very long sentence"
truncated = safe_truncate(text, max_length=20, suffix="[more]")
print(truncated)  # Output: "This is a [more]"
```

## Features

- **clean_text**: Normalizes whitespace, removes extra spaces, newlines, and tabs
- **safe_truncate**: Intelligently truncates text at word boundaries when possible

## Requirements

- Python >= 3.8

## License

MIT