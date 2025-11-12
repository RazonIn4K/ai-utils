"""
ai-utils: A small Python package with helpful AI utility functions.
"""

__version__ = "0.1.0"

import re


def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and special characters.
    
    Args:
        text: The input text to clean
        
    Returns:
        Cleaned text with normalized whitespace
        
    Examples:
        >>> clean_text("  Hello   World!  ")
        'Hello World!'
        >>> clean_text("Multiple\\n\\nlines\\n\\nhere")
        'Multiple lines here'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    
    # Replace multiple whitespace (including newlines, tabs) with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    return text


def safe_truncate_tokens(text: str, max_tokens: int) -> str:
    """
    Safely truncate text to a maximum number of tokens without splitting words.

    Uses whitespace-based tokenization as an approximation. The function ensures
    that words are not cut in the middle by truncating at word boundaries.

    Args:
        text: The input text to truncate
        max_tokens: Maximum number of tokens (approximately word-based)

    Returns:
        Truncated text that respects word boundaries

    Examples:
        >>> safe_truncate_tokens("Hello World! This is a test.", 3)
        'Hello World! This'
        >>> safe_truncate_tokens("Short", 10)
        'Short'
        >>> safe_truncate_tokens("One two three four five", 3)
        'One two three'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(max_tokens, int) or max_tokens < 0:
        raise ValueError(f"max_tokens must be a non-negative integer")

    if not text or max_tokens == 0:
        return ""

    # Split text into tokens (words) while preserving whitespace information
    tokens = text.split()

    # If we have fewer tokens than the limit, return original text
    if len(tokens) <= max_tokens:
        return text

    # Take only the first max_tokens words and join them back
    truncated_tokens = tokens[:max_tokens]
    return ' '.join(truncated_tokens)


def merge_context_snippets(snippets: list[str], separator: str = "\n\n") -> str:
    """
    Merge multiple context snippets into a single string with a separator.

    Filters out empty or whitespace-only snippets and joins the remaining
    snippets with the specified separator.

    Args:
        snippets: List of text snippets to merge
        separator: String to use between snippets (default: double newline)

    Returns:
        Merged string with all non-empty snippets separated by the separator

    Examples:
        >>> merge_context_snippets(["First snippet", "Second snippet"])
        'First snippet\\n\\nSecond snippet'
        >>> merge_context_snippets(["Hello", "", "World"], separator=" | ")
        'Hello | World'
        >>> merge_context_snippets([], separator="---")
        ''
    """
    if not isinstance(snippets, list):
        raise TypeError(f"Expected list, got {type(snippets).__name__}")

    if not isinstance(separator, str):
        raise TypeError(f"Expected str for separator, got {type(separator).__name__}")

    # Filter out empty or whitespace-only snippets
    non_empty_snippets = [s.strip() for s in snippets if isinstance(s, str) and s.strip()]

    # Join with the separator
    return separator.join(non_empty_snippets)


__all__ = ["clean_text", "safe_truncate_tokens", "merge_context_snippets"]
