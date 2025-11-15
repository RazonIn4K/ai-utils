"""Additional utility helpers for AI workflows."""

import json
import logging
import re
import sys
from typing import Any, Callable, Optional, Union


class _RetryResultTrigger(Exception):
    """Internal exception raised when retry_on_result requests a retry."""


def safe_extract_json(
    text: str,
    default: Any = None,
    allow_multiple: bool = False
) -> Union[dict, list, Any]:
    """
    Safely extract JSON from text that may contain additional content.

    This is particularly useful for extracting JSON from LLM responses that might
    include explanatory text before or after the JSON content. The function tries
    multiple strategies to find and parse valid JSON.

    Args:
        text: The input text that may contain JSON
        default: Value to return if no valid JSON is found (default: None)
        allow_multiple: If True, returns list of all found JSON objects (default: False)

    Returns:
        Parsed JSON object(s), or default value if parsing fails

    Examples:
        >>> text = 'Here is the data: {"name": "John", "age": 30}'
        >>> safe_extract_json(text)
        {'name': 'John', 'age': 30}

        >>> text = 'Error: invalid input'
        >>> safe_extract_json(text, default={})
        {}

        >>> text = '```json\\n{"key": "value"}\\n```'
        >>> safe_extract_json(text)
        {'key': 'value'}

        >>> text = 'First: {"a": 1} Second: {"b": 2}'
        >>> safe_extract_json(text, allow_multiple=True)
        [{'a': 1}, {'b': 2}]
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if not text.strip():
        return default

    # Strategy 1: Try direct JSON parsing
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code blocks
    code_block_patterns = [
        r'```json\s*(.*?)\s*```',  # ```json ... ```
        r'```\s*(.*?)\s*```',       # ``` ... ```
        r'`(.*?)`',                 # ` ... `
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    parsed = json.loads(match.strip())
                    if allow_multiple:
                        continue  # Keep looking for more
                    return parsed
                except json.JSONDecodeError:
                    continue

    # Strategy 3: Find JSON object/array patterns
    # Look for {...} or [...]
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested objects
        r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',  # Nested arrays
    ]

    found_objects = []

    for pattern in json_patterns:
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match.group())
                if allow_multiple:
                    found_objects.append(parsed)
                else:
                    return parsed
            except json.JSONDecodeError:
                continue

    if allow_multiple and found_objects:
        return found_objects

    # Strategy 4: Try to extract content between first { and last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        potential_json = text[first_brace:last_brace + 1]
        try:
            return json.loads(potential_json)
        except json.JSONDecodeError:
            pass

    # Strategy 5: Try with [ and ]
    first_bracket = text.find('[')
    last_bracket = text.rfind(']')

    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        potential_json = text[first_bracket:last_bracket + 1]
        try:
            return json.loads(potential_json)
        except json.JSONDecodeError:
            pass

    # All strategies failed
    return default


def configure_logging(
    level: Union[str, int] = logging.INFO,
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    include_level: bool = True,
    include_module: bool = False,
    stream: Any = None
) -> logging.Logger:
    """
    Configure logging with sensible defaults for AI workflows.

    This helper makes it easy to set up consistent logging across your projects
    without having to remember the logging configuration details.

    Args:
        level: Logging level (default: logging.INFO). Can be string or int.
               Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        format_string: Custom format string. If None, builds from other params.
        include_timestamp: Include timestamp in log messages (default: True)
        include_level: Include log level in messages (default: True)
        include_module: Include module name in messages (default: False)
        stream: Output stream (default: sys.stdout)

    Returns:
        Configured root logger

    Examples:
        >>> import logging
        >>> logger = configure_logging()
        >>> logger.info("Application started")

        >>> # Debug level with module names
        >>> logger = configure_logging(level='DEBUG', include_module=True)
        >>> logger.debug("Debug message from module")

        >>> # Custom format
        >>> logger = configure_logging(
        ...     format_string='[%(levelname)s] %(message)s',
        ...     level=logging.WARNING
        ... )
    """
    # Convert string level to logging constant
    if isinstance(level, str):
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        level = level_map.get(level.upper(), logging.INFO)

    # Build format string if not provided
    if format_string is None:
        parts = []

        if include_timestamp:
            parts.append('%(asctime)s')

        if include_level:
            parts.append('[%(levelname)s]')

        if include_module:
            parts.append('%(name)s')

        parts.append('%(message)s')

        format_string = ' - '.join(parts)

    # Configure logging
    logging.basicConfig(
        level=level,
        format=format_string,
        stream=stream or sys.stdout,
        force=True  # Reconfigure if already configured
    )

    logger = logging.getLogger()

    # Also set level for ai_utils loggers specifically
    ai_utils_logger = logging.getLogger('ai_utils')
    ai_utils_logger.setLevel(level)

    return logger


def retry_with_backoff(
    func=None,
    *,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    retry_on_result: Optional[Callable[[Any], bool]] = None,
):
    """
    Decorator for retrying a function with exponential backoff.

    Can be used as ``@retry_with_backoff(...)`` or ``retry_with_backoff(fn, ...)``.
    For complex scenarios consider using :class:`LLMClient`, which integrates
    configurable retry logic.

    Args:
        func: Function to wrap. When omitted this returns a decorator.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds before retrying.
        backoff_factor: Multiplier applied to the delay after each retry.
        exceptions: Tuple of exception classes that trigger a retry.
        retry_on_result: Optional predicate that returns True when the
            function result should trigger a retry even if no exception was
            raised. Defaults to flagging string responses that contain the
            word "error" (case-insensitive).

    Returns:
        Wrapped function with retry logic or the decorator itself.
    """

    import functools
    import time

    def decorator(target_func):
        result_checker = retry_on_result

        if result_checker is None:
            def _default_checker(result: Any) -> bool:
                return isinstance(result, str) and "error" in result.lower()

            result_checker = _default_checker

        @functools.wraps(target_func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    result = target_func(*args, **kwargs)
                    if result_checker and result_checker(result):
                        raise _RetryResultTrigger("Result triggered retry_with_backoff")
                    return result
                except exceptions as exc:  # type: ignore[misc]
                    last_exception = exc
                except _RetryResultTrigger as exc:
                    last_exception = exc

                if last_exception is None:
                    continue

                if attempt < max_retries - 1:
                    delay = initial_delay * (backoff_factor ** attempt)
                    logging.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {last_exception}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logging.error(f"All {max_retries} retry attempts failed")

            if last_exception:
                raise last_exception
            raise RuntimeError(f"Failed after {max_retries} attempts")

        return wrapper

    if func is None:
        return decorator

    if not callable(func):
        raise TypeError("retry_with_backoff expects a callable or is used as a decorator")

    return decorator(func)


__all__ = [
    "safe_extract_json",
    "configure_logging",
    "retry_with_backoff",
]
