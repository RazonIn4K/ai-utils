"""
ai-utils: A small Python package with helpful AI utility functions.
"""

__version__ = "0.1.0"

import json
import math
import os
import re
from importlib import resources
from pathlib import Path

# Import LLMClient if requests is available
try:
    from .llm_client import LLMClient
    _has_llm_client = True
except ImportError:
    _has_llm_client = False
    LLMClient = None  # type: ignore

# Import additional helpers
from .helpers import safe_extract_json, configure_logging, retry_with_backoff

_DEFAULT_MODEL = "gpt-3.5-turbo"
_DEFAULT_CHARS_PER_TOKEN = 4.0
_MIN_CHARS_PER_TOKEN = 2.5
_MODEL_CHAR_PER_TOKEN: dict[str, float] = {
    "gpt-4.1": 3.2,
    "gpt-4o": 3.4,
    "gpt-4": 3.7,
    "gpt-3.5": 4.0,
    "gpt-3": 4.2,
    "text-davinci": 4.0,
    "claude-3": 3.1,
    "claude-2": 3.3,
    "claude": 3.4,
    "command-r": 3.2,
}

_MODEL_PRICING_USD: dict[str, dict[str, float]] = {
    "gpt-4.1": {"input": 0.010, "output": 0.030},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4": {"input": 0.030, "output": 0.060},
    "gpt-3.5": {"input": 0.0015, "output": 0.002},
    "claude-3": {"input": 0.003, "output": 0.015},
    "claude-2": {"input": 0.008, "output": 0.024},
    "command-r": {"input": 0.0025, "output": 0.0035},
    "gpt-4o-mini": {"input": 0.0006, "output": 0.0024},
}


def _load_pricing_config() -> dict[str, dict[str, float]]:
    env_path = os.environ.get("AI_UTILS_PRICING_CONFIG")
    paths = []
    if env_path:
        paths.append(Path(env_path))
    try:
        default_path = resources.files(__package__).joinpath("pricing_config.json")
        paths.append(Path(str(default_path)))
    except FileNotFoundError:
        pass

    for path in paths:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
                models = data.get("models") if isinstance(data, dict) else None
                if isinstance(models, dict):
                    return models  # type: ignore[return-value]
        except Exception:
            continue
    return {}


_CONFIG_PRICING = _load_pricing_config()

_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?。！？])\s+|[\r\n]+", re.UNICODE)


def _normalized_model_name(model: str) -> str:
    normalized = model.strip()
    if not normalized:
        raise ValueError("model must be a non-empty string")
    return normalized


def _chars_per_token_for_model(model: str) -> float:
    normalized = model.lower()
    for prefix, ratio in _MODEL_CHAR_PER_TOKEN.items():
        if normalized.startswith(prefix):
            return max(_MIN_CHARS_PER_TOKEN, ratio)
    return _DEFAULT_CHARS_PER_TOKEN


def _pricing_for_model(model: str, pricing_overrides: dict[str, dict[str, float]] | None = None) -> dict[str, float]:
    lookup: dict[str, dict[str, float]] = {}
    lookup.update(_MODEL_PRICING_USD)
    lookup.update(_CONFIG_PRICING)
    if pricing_overrides:
        lookup.update(pricing_overrides)

    normalized = model.lower()
    for prefix, pricing in lookup.items():
        if normalized.startswith(prefix.lower()):
            return {
                "input": max(0.0, pricing.get("input", 0.0)),
                "output": max(0.0, pricing.get("output", pricing.get("input", 0.0))),
            }
    raise ValueError(f"No pricing data available for model '{model}'")


def _split_sentences(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    sentences = [segment.strip() for segment in _SENTENCE_SPLIT_PATTERN.split(stripped) if segment.strip()]
    return sentences or [stripped]


def _truncate_segment(segment: str, token_limit: int, model: str) -> str:
    if token_limit <= 0 or not segment.strip():
        return ""
    words = segment.split()
    stripped = segment.strip()
    if words and len(words) > token_limit:
        return " ".join(words[:token_limit])
    if words:
        if len(words) == 1 and words[0] == stripped:
            approx_chars = max(1, int(token_limit * _chars_per_token_for_model(model)))
            return stripped[:approx_chars]
        if estimate_token_count(stripped, model=model) <= token_limit:
            return stripped
        approx_chars = max(1, int(token_limit * _chars_per_token_for_model(model)))
        return stripped[:approx_chars]

    approx_chars = max(1, int(token_limit * _chars_per_token_for_model(model)))
    return stripped[:approx_chars]


def _split_segment_into_chunks(segment: str, max_tokens: int, model: str) -> list[str]:
    """Split a single sentence/segment into smaller chunks that fit max_tokens."""
    stripped = segment.strip()
    if not stripped:
        return []

    words = stripped.split()
    if not words or (len(words) == 1 and words[0] == stripped):
        approx_chars = max(1, int(max_tokens * _chars_per_token_for_model(model)))
        return [stripped[i : i + approx_chars] for i in range(0, len(stripped), approx_chars)]

    chunks: list[str] = []
    current_words: list[str] = []

    for word in words:
        candidate_words = current_words + [word]
        candidate_text = " ".join(candidate_words)
        if current_words and estimate_token_count(candidate_text, model=model) > max_tokens:
            chunks.append(" ".join(current_words))
            current_words = [word]
        else:
            current_words = candidate_words

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def _calculate_overlap_segments(segments: list[str], overlap_tokens: int, model: str) -> tuple[list[str], int]:
    if overlap_tokens <= 0 or not segments:
        return [], 0
    overlap_segments: list[str] = []
    used_tokens = 0
    for segment in reversed(segments):
        token_count = estimate_token_count(segment, model=model)
        if token_count == 0:
            continue
        overlap_segments.append(segment)
        used_tokens += token_count
        if used_tokens >= overlap_tokens:
            break
    overlap_segments.reverse()
    return overlap_segments, used_tokens


def _join_segments(segments: list[str]) -> str:
    return " ".join(segment.strip() for segment in segments).strip()


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


def estimate_token_count(text: str, model: str = _DEFAULT_MODEL) -> int:
    """
    Estimate the token count of text using lightweight heuristics.

    The calculation blends whitespace token counts with an approximate
    characters-per-token ratio tuned for popular LLM families. The result is
    sufficient for chunking and guardrail logic without depending on model-
    specific tokenizers.

    Args:
        text: The text to estimate tokens for.
        model: The target model name (used to select a heuristic ratio).

    Returns:
        Estimated token count for the provided model.

    Examples:
        >>> estimate_token_count("Hello world!", model="gpt-3.5-turbo")
        2
        >>> estimate_token_count("This is a test sentence.", model="gpt-4o")
        5
        >>> estimate_token_count("", model="gpt-3.5-turbo")
        0
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    normalized_model = _normalized_model_name(model)

    if not text.strip():
        return 0

    whitespace_tokens = len(text.split())
    chars_per_token = _chars_per_token_for_model(normalized_model.lower())
    approx_by_chars = max(1, math.ceil(len(text) / chars_per_token))

    return max(whitespace_tokens, approx_by_chars)


def safe_truncate_tokens(text: str, max_tokens: int, model: str = _DEFAULT_MODEL) -> str:
    """
    Truncate text to a target token budget while respecting sentence boundaries.

    The function prioritizes returning whole sentences whenever possible. When a
    single sentence exceeds the budget, it degrades gracefully by truncating on
    word boundaries (or individual characters for languages without whitespace),
    guaranteeing that no multi-byte characters are split.

    Args:
        text: The text to truncate.
        max_tokens: Maximum estimated tokens allowed in the result.
        model: Target model name used for token estimation heuristics.

    Returns:
        Truncated text that respects sentence and word boundaries where possible.

    Examples:
        >>> safe_truncate_tokens("Hello world. Second sentence.", 3, model="gpt-3.5-turbo")
        'Hello world.'
        >>> safe_truncate_tokens("Short", 10, model="gpt-3.5-turbo")
        'Short'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(max_tokens, int) or max_tokens < 0:
        raise ValueError("max_tokens must be a non-negative integer")

    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    normalized_model = _normalized_model_name(model)

    if not text.strip() or max_tokens == 0:
        return ""

    sentences = _split_sentences(text)
    truncated_segments: list[str] = []
    tokens_used = 0

    for sentence in sentences:
        sentence_tokens = estimate_token_count(sentence, model=normalized_model)
        if sentence_tokens == 0:
            continue

        if tokens_used + sentence_tokens <= max_tokens:
            truncated_segments.append(sentence)
            tokens_used += sentence_tokens
            continue

        remaining = max_tokens - tokens_used
        if remaining <= 0:
            break
        partial = _truncate_segment(sentence, remaining, normalized_model)
        if partial:
            truncated_segments.append(partial)
        break

    if not truncated_segments:
        return _truncate_segment(text, max_tokens, normalized_model)

    return _join_segments(truncated_segments)


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


def split_into_chunks(
    text: str,
    max_tokens: int,
    overlap_tokens: int = 0,
    model: str = _DEFAULT_MODEL,
) -> list[str]:
    """
    Split text into overlapping chunks sized for RAG and automation workflows.

    Args:
        text: Source document or API response to split.
        max_tokens: Maximum estimated tokens per chunk.
        overlap_tokens: Tokens to repeat between consecutive chunks for context.
        model: Target model name used for token estimation.

    Returns:
        List of chunk strings that include the requested overlap.

    Examples:
        >>> text = "First paragraph. Second paragraph. Third paragraph."
        >>> chunks = split_into_chunks(text, max_tokens=8, overlap_tokens=2)
        >>> len(chunks) >= 2
        True
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer")

    if not isinstance(overlap_tokens, int) or overlap_tokens < 0:
        raise ValueError("overlap_tokens must be a non-negative integer")

    if overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be smaller than max_tokens")

    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    normalized_model = _normalized_model_name(model)

    if not text.strip():
        return []

    sentences = _split_sentences(text)
    segments: list[str] = []
    for sentence in sentences:
        if not sentence:
            continue
        if estimate_token_count(sentence, model=normalized_model) <= max_tokens:
            segments.append(sentence)
        else:
            segments.extend(_split_segment_into_chunks(sentence, max_tokens, normalized_model))

    chunks: list[str] = []
    current_segments: list[str] = []
    current_tokens = 0

    def flush_chunk(add_overlap: bool) -> None:
        nonlocal current_segments, current_tokens
        if not current_segments:
            return
        chunks.append(_join_segments(current_segments))
        if add_overlap and overlap_tokens > 0:
            overlap_segments, _ = _calculate_overlap_segments(current_segments, overlap_tokens, normalized_model)
            current_segments = overlap_segments.copy()
            current_tokens = sum(
                estimate_token_count(seg, model=normalized_model) for seg in current_segments
            )
        else:
            current_segments = []
            current_tokens = 0

    for segment in segments:
        seg_tokens = estimate_token_count(segment, model=normalized_model)
        if seg_tokens == 0:
            continue

        if current_tokens + seg_tokens > max_tokens and current_segments:
            flush_chunk(add_overlap=True)

        if seg_tokens > max_tokens:
            smaller_chunks = _split_segment_into_chunks(segment, max_tokens, normalized_model)
            for small in smaller_chunks:
                small_tokens = estimate_token_count(small, model=normalized_model)
                if current_tokens + small_tokens > max_tokens and current_segments:
                    flush_chunk(add_overlap=True)
                current_segments.append(small)
                current_tokens += small_tokens
                if current_tokens >= max_tokens:
                    flush_chunk(add_overlap=True)
            continue

        current_segments.append(segment)
        current_tokens += seg_tokens

    flush_chunk(add_overlap=False)

    return chunks


def estimate_llm_cost(
    text: str,
    model: str,
    *,
    expected_response_tokens: int | None = None,
    pricing_overrides: dict[str, dict[str, float]] | None = None,
) -> float:
    """
    Estimate the USD cost for a single LLM call.

    Args:
        text: Prompt text being sent to the model.
        model: Target model name used for both token estimation and pricing lookup.
        expected_response_tokens: Optional expected completion tokens. When omitted,
            a conservative 25%% of the prompt tokens is assumed.
        pricing_overrides: Optional mapping of model prefixes to ``{"input": x, "output": y}``
            values expressed in USD per 1K tokens.

    Returns:
        Estimated dollar cost for the request (prompt + completion).

    Examples:
        >>> estimate_llm_cost("Hello world", model="gpt-4o")
        5e-06
        >>> estimate_llm_cost("Hello", model="custom-model", pricing_overrides={"custom": {"input": 0.002}})
        2e-06
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str for text, got {type(text).__name__}")

    if not isinstance(model, str):
        raise TypeError(f"model must be str, got {type(model).__name__}")

    normalized_model = _normalized_model_name(model)
    prompt_tokens = estimate_token_count(text, model=normalized_model)

    if expected_response_tokens is not None:
        if not isinstance(expected_response_tokens, int) or expected_response_tokens < 0:
            raise ValueError("expected_response_tokens must be a non-negative integer or None")
        completion_tokens = expected_response_tokens
    else:
        completion_tokens = math.ceil(prompt_tokens * 0.25)

    pricing = _pricing_for_model(normalized_model, pricing_overrides)
    prompt_cost = (prompt_tokens / 1000) * pricing["input"]
    completion_cost = (completion_tokens / 1000) * pricing["output"]
    return round(prompt_cost + completion_cost, 8)

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
    # Text processing
    "clean_text",
    "estimate_token_count",
    "safe_truncate_tokens",
    "merge_context_snippets",
    "split_into_chunks",
    "estimate_llm_cost",
    "summarise_text",
    # LLM integration
    "LLMClient",
    # Additional helpers
    "safe_extract_json",
    "configure_logging",
    "retry_with_backoff",
]
