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


def estimate_token_count(text: str) -> int:
    """
    Estimate the token count of text by splitting on whitespace.

    This is a simple approximation useful for chunking and processing workflows.
    It is NOT intended for accurate billing or API quota calculations, as different
    tokenizers (GPT, Claude, etc.) may count tokens differently.

    Args:
        text: The input text to estimate tokens for

    Returns:
        Approximate token count based on whitespace splitting

    Examples:
        >>> estimate_token_count("Hello world!")
        2
        >>> estimate_token_count("This is a test sentence.")
        5
        >>> estimate_token_count("")
        0
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not text.strip():
        return 0

    return len(text.split())


def safe_truncate_tokens(text: str, max_tokens: int) -> str:
    """
    Safely truncate text to a maximum number of tokens without splitting words.

    Uses whitespace-based tokenization as an approximation. The function ensures
    that words are not cut in the middle by truncating at word boundaries.

    Note: For very long inputs, consider using split_into_chunks() instead, which
    preserves paragraph structure and is better suited for processing multi-page
    documents.

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
    Split long text into chunks respecting paragraph boundaries when possible.

    This function intelligently splits text by first attempting to split on
    double-newlines (paragraph breaks). If a paragraph exceeds max_tokens,
    it falls back to word-based chunking for that paragraph. This preserves
    natural document structure while ensuring no chunk exceeds the token limit.

    Token counting uses estimate_token_count(), which is whitespace-based.

    Args:
        text: The input text to split into chunks
        max_tokens: Maximum number of tokens per chunk (estimated)

    Returns:
        List of text chunks, each containing at most max_tokens (estimated)

    Examples:
        >>> text = "First paragraph here.\\n\\nSecond paragraph here.\\n\\nThird paragraph."
        >>> chunks = split_into_chunks(text, max_tokens=10)
        >>> len(chunks)
        3
        >>> # If a paragraph is too long, it gets split further
        >>> long_para = "This is a very long paragraph " * 20
        >>> chunks = split_into_chunks(long_para, max_tokens=50)
        >>> all(estimate_token_count(chunk) <= 50 for chunk in chunks)
        True
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError(f"max_tokens must be a positive integer")

    if not text.strip():
        return []

    # Check if entire text fits in one chunk
    if estimate_token_count(text) <= max_tokens:
        return [text]

    # Split on double-newlines (paragraph boundaries)
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = []
    current_token_count = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        para_token_count = estimate_token_count(paragraph)

        # If this single paragraph exceeds max_tokens, split it further
        if para_token_count > max_tokens:
            # First, add any accumulated chunk
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_token_count = 0

            # Split the long paragraph into word-based chunks
            words = paragraph.split()
            word_chunk = []
            word_count = 0

            for word in words:
                if word_count + 1 > max_tokens:
                    chunks.append(' '.join(word_chunk))
                    word_chunk = [word]
                    word_count = 1
                else:
                    word_chunk.append(word)
                    word_count += 1

            if word_chunk:
                chunks.append(' '.join(word_chunk))

        # If adding this paragraph would exceed limit, start new chunk
        elif current_token_count + para_token_count > max_tokens:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_token_count = para_token_count

        # Otherwise, add to current chunk
        else:
            current_chunk.append(paragraph)
            current_token_count += para_token_count

    # Add any remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

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
    "estimate_token_count",
    "safe_truncate_tokens",
    "merge_context_snippets",
    "split_into_chunks",
    "summarise_text",
]
