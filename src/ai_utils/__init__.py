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


def safe_truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Safely truncate text to a maximum length, adding a suffix if truncated.
    
    Ensures truncation happens at word boundaries when possible to avoid
    cutting words in the middle.
    
    Args:
        text: The input text to truncate
        max_length: Maximum length of the result (including suffix)
        suffix: String to append when text is truncated (default: "...")
        
    Returns:
        Truncated text with suffix if needed
        
    Examples:
        >>> safe_truncate("Hello World!", 10)
        'Hello...'
        >>> safe_truncate("Short", 10)
        'Short'
        >>> safe_truncate("Hello World!", 20)
        'Hello World!'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    
    if not isinstance(max_length, int) or max_length < 0:
        raise ValueError(f"max_length must be a non-negative integer")
    
    if len(text) <= max_length:
        return text
    
    # Account for suffix length
    truncate_at = max_length - len(suffix)
    
    if truncate_at <= 0:
        # If suffix is too long, just return the suffix truncated
        return suffix[:max_length]
    
    # Truncate to max length
    truncated = text[:truncate_at]
    
    # Try to truncate at word boundary
    last_space = truncated.rfind(' ')
    if last_space > 0:
        # If we found a space, truncate there for cleaner cut
        truncated = truncated[:last_space]
    
    return truncated + suffix


__all__ = ["clean_text", "safe_truncate"]
