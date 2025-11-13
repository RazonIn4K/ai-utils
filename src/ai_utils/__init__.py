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


def split_into_chunks(text: str, max_tokens: int) -> list[str]:
    """
    Split long text into chunks of up to max_tokens without breaking words.

    This function divides text into smaller segments while ensuring that words
    remain intact. Each chunk will contain at most max_tokens words, making it
    useful for processing long documents in manageable pieces.

    Args:
        text: The input text to split into chunks
        max_tokens: Maximum number of tokens (words) per chunk

    Returns:
        List of text chunks, each containing at most max_tokens words

    Examples:
        >>> text = "This is a long sentence that needs to be split into chunks."
        >>> split_into_chunks(text, max_tokens=4)
        ['This is a long', 'sentence that needs to', 'be split into chunks.']
        >>> split_into_chunks("Short text", max_tokens=10)
        ['Short text']
        >>> split_into_chunks("One two three four five six", max_tokens=2)
        ['One two', 'three four', 'five six']
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError(f"max_tokens must be a positive integer")

    if not text.strip():
        return []

    # Split text into tokens (words)
    tokens = text.split()

    # If text is shorter than max_tokens, return it as a single chunk
    if len(tokens) <= max_tokens:
        return [text]

    # Split into chunks
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(' '.join(chunk_tokens))

    return chunks


def summarise_text(text: str, max_chars: int) -> str:
    """
    Reduce text length using a simple heuristic that preserves key content.

    This function uses a sentence-based heuristic to summarize text by keeping
    the first and last portions when the text exceeds max_chars. It attempts to
    preserve complete sentences and adds an ellipsis to indicate omitted content.

    Args:
        text: The input text to summarize
        max_chars: Maximum number of characters in the result

    Returns:
        Summarized text with approximately max_chars length

    Examples:
        >>> text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        >>> summarise_text(text, max_chars=50)
        'First sentence. ... Fourth sentence.'
        >>> summarise_text("Short text", max_chars=100)
        'Short text'
        >>> text = "Introduction here. Body content. More details. Conclusion."
        >>> summarise_text(text, max_chars=40)
        'Introduction here. ... Conclusion.'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(max_chars, int) or max_chars <= 0:
        raise ValueError(f"max_chars must be a positive integer")

    # If text is already short enough, return it
    if len(text) <= max_chars:
        return text

    # Split into sentences using basic sentence splitting
    # This handles periods followed by space and capital letter
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(sentence_pattern, text.strip())

    # If only one sentence, truncate it
    if len(sentences) == 1:
        if max_chars < 10:
            return text[:max_chars]
        return text[:max_chars - 3] + "..."

    # Try to keep first and last sentences
    ellipsis = " ... "
    first_sentence = sentences[0]
    last_sentence = sentences[-1]

    # If even first + last is too long, truncate
    combined = first_sentence + ellipsis + last_sentence
    if len(combined) <= max_chars:
        return combined

    # Try to fit as much of first sentence and last sentence as possible
    space_for_first = (max_chars - len(ellipsis) - len(last_sentence)) // 2
    space_for_last = max_chars - len(ellipsis) - space_for_first

    if space_for_first > 0 and space_for_last > 0:
        # Truncate first sentence
        first_part = first_sentence[:max(0, space_for_first - 3)].rstrip()
        if first_part and not first_part.endswith('.'):
            first_part += "..."

        # Truncate last sentence
        last_part = last_sentence[max(0, len(last_sentence) - space_for_last + 3):].lstrip()
        if last_part and len(last_sentence) > space_for_last:
            last_part = "..." + last_part

        return f"{first_part} {last_part}".strip()

    # Fallback: simple truncation
    return text[:max_chars - 3] + "..."


__all__ = [
    "clean_text",
    "safe_truncate_tokens",
    "merge_context_snippets",
    "split_into_chunks",
    "summarise_text",
]
