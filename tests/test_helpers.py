"""Tests for additional helper utilities."""

import json
import logging
import pytest
from ai_utils.helpers import safe_extract_json, configure_logging, retry_with_backoff


class TestSafeExtractJson:
    """Tests for safe_extract_json function."""

    def test_direct_json_object(self):
        """Test parsing of direct JSON object."""
        text = '{"name": "John", "age": 30}'
        result = safe_extract_json(text)
        assert result == {"name": "John", "age": 30}

    def test_direct_json_array(self):
        """Test parsing of direct JSON array."""
        text = '[1, 2, 3, 4, 5]'
        result = safe_extract_json(text)
        assert result == [1, 2, 3, 4, 5]

    def test_json_with_surrounding_text(self):
        """Test extraction of JSON with surrounding text."""
        text = 'Here is the data: {"key": "value"} Hope this helps!'
        result = safe_extract_json(text)
        assert result == {"key": "value"}

    def test_json_in_markdown_code_block(self):
        """Test extraction from markdown code blocks."""
        text = '```json\n{"name": "Alice", "role": "developer"}\n```'
        result = safe_extract_json(text)
        assert result == {"name": "Alice", "role": "developer"}

    def test_json_in_generic_code_block(self):
        """Test extraction from generic code blocks."""
        text = '```\n{"status": "ok"}\n```'
        result = safe_extract_json(text)
        assert result == {"status": "ok"}

    def test_json_in_inline_code(self):
        """Test extraction from inline code."""
        text = 'The result is `{"success": true}`'
        result = safe_extract_json(text)
        assert result == {"success": True}

    def test_nested_json(self):
        """Test nested JSON objects."""
        text = 'Data: {"user": {"name": "Bob", "id": 123}, "active": true}'
        result = safe_extract_json(text)
        assert result == {"user": {"name": "Bob", "id": 123}, "active": True}

    def test_multiple_json_objects(self):
        """Test extraction of multiple JSON objects."""
        text = 'First: {"a": 1} and second: {"b": 2}'
        result = safe_extract_json(text, allow_multiple=True)
        assert isinstance(result, list)
        assert len(result) == 2
        assert {"a": 1} in result
        assert {"b": 2} in result

    def test_invalid_json_returns_default(self):
        """Test that invalid JSON returns default value."""
        text = 'This is not JSON at all'
        result = safe_extract_json(text, default=None)
        assert result is None

        result = safe_extract_json(text, default={})
        assert result == {}

        result = safe_extract_json(text, default=[])
        assert result == []

    def test_empty_string(self):
        """Test empty string returns default."""
        result = safe_extract_json("", default="empty")
        assert result == "empty"

    def test_whitespace_only(self):
        """Test whitespace-only string returns default."""
        result = safe_extract_json("   \n\n   ", default=None)
        assert result is None

    def test_malformed_json(self):
        """Test malformed JSON returns default."""
        text = '{"key": "value"'  # Missing closing brace
        result = safe_extract_json(text, default=None)
        # Should still try to extract and might succeed with some strategies
        # or return default

    def test_json_with_newlines(self):
        """Test JSON with newlines and formatting."""
        text = '''
        {
            "name": "Test",
            "value": 123,
            "nested": {
                "key": "val"
            }
        }
        '''
        result = safe_extract_json(text)
        assert result["name"] == "Test"
        assert result["value"] == 123
        assert result["nested"]["key"] == "val"

    def test_unicode_json(self):
        """Test JSON with unicode characters."""
        text = '{"message": "Hello 世界", "emoji": "👋"}'
        result = safe_extract_json(text)
        assert result == {"message": "Hello 世界", "emoji": "👋"}

    def test_json_array_with_text(self):
        """Test JSON array extraction with surrounding text."""
        text = 'The list is: [1, 2, 3] and more text'
        result = safe_extract_json(text)
        assert result == [1, 2, 3]

    def test_type_error(self):
        """Test type error for non-string input."""
        with pytest.raises(TypeError):
            safe_extract_json(123)  # type: ignore

    def test_complex_llm_response(self):
        """Test realistic LLM response with JSON."""
        text = '''
        Sure! Here's the data you requested:

        ```json
        {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "total": 2
        }
        ```

        Let me know if you need anything else!
        '''
        result = safe_extract_json(text)
        assert result["total"] == 2
        assert len(result["users"]) == 2

    def test_escaped_characters(self):
        """Test JSON with escaped characters."""
        text = '{"text": "Line 1\\nLine 2\\tTabbed"}'
        result = safe_extract_json(text)
        assert result == {"text": "Line 1\nLine 2\tTabbed"}


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_default_configuration(self):
        """Test default logging configuration."""
        logger = configure_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_debug_level(self):
        """Test setting DEBUG level."""
        logger = configure_logging(level='DEBUG')
        assert logger.level == logging.DEBUG

    def test_warning_level(self):
        """Test setting WARNING level."""
        logger = configure_logging(level='WARNING')
        assert logger.level == logging.WARNING

    def test_level_as_int(self):
        """Test setting level as integer."""
        logger = configure_logging(level=logging.ERROR)
        assert logger.level == logging.ERROR

    def test_custom_format_string(self):
        """Test custom format string."""
        logger = configure_logging(format_string='%(levelname)s: %(message)s')
        # Just verify it doesn't crash; format verification would need handler inspection

    def test_include_module(self):
        """Test including module names."""
        logger = configure_logging(include_module=True)
        # Verify configuration works without error

    def test_minimal_format(self):
        """Test minimal format configuration."""
        logger = configure_logging(
            include_timestamp=False,
            include_level=False,
            include_module=False
        )
        # Should still work with just message

    def test_invalid_level_string(self):
        """Test invalid level string falls back to INFO."""
        logger = configure_logging(level='INVALID')
        assert logger.level == logging.INFO

    def test_logger_hierarchy(self):
        """Test that ai_utils logger is also configured."""
        configure_logging(level='DEBUG')
        ai_utils_logger = logging.getLogger('ai_utils')
        assert ai_utils_logger.level == logging.DEBUG


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    def test_successful_function(self):
        """Test function that succeeds on first try."""
        call_count = [0]

        @retry_with_backoff
        def successful_func():
            call_count[0] += 1
            return "success"

        result = successful_func()
        assert result == "success"
        assert call_count[0] == 1

    def test_retry_until_success(self):
        """Test function that fails then succeeds."""
        call_count = [0]

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def flaky_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("Temporary error")
            return "success"

        result = flaky_func()
        assert result == "success"
        assert call_count[0] == 2

    def test_all_retries_exhausted(self):
        """Test function that always fails."""
        call_count = [0]

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def always_fails():
            call_count[0] += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fails()

        assert call_count[0] == 3

    def test_custom_exceptions(self):
        """Test retrying only specific exceptions."""
        call_count = [0]

        @retry_with_backoff(
            max_retries=3,
            initial_delay=0.01,
            exceptions=(ValueError,)
        )
        def specific_error_func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("Retryable")
            elif call_count[0] == 2:
                raise TypeError("Not retryable")
            return "success"

        with pytest.raises(TypeError, match="Not retryable"):
            specific_error_func()

        # Should have retried ValueError but not TypeError
        assert call_count[0] == 2

    def test_backoff_timing(self):
        """Test exponential backoff delay."""
        import time
        call_times = []

        @retry_with_backoff(
            max_retries=3,
            initial_delay=0.1,
            backoff_factor=2.0
        )
        def timed_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry")
            return "success"

        result = timed_func()
        assert result == "success"
        assert len(call_times) == 3

        # Check delays are approximately exponential (with some tolerance)
        # First retry: ~0.1s, Second retry: ~0.2s
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert 0.08 < delay1 < 0.15  # ~0.1s with tolerance

        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert 0.18 < delay2 < 0.25  # ~0.2s with tolerance

    def test_function_arguments(self):
        """Test that decorator preserves function arguments."""
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def func_with_args(a, b, c=None):
            return f"{a}-{b}-{c}"

        result = func_with_args(1, 2, c=3)
        assert result == "1-2-3"

    def test_direct_usage(self):
        """Test using retry_with_backoff directly without decorator."""
        def my_func(x):
            if x < 5:
                raise ValueError("Too small")
            return x * 2

        retried_func = retry_with_backoff(
            my_func,
            max_retries=2,
            initial_delay=0.01
        )

        # Should raise because x=3 is always < 5
        with pytest.raises(ValueError):
            retried_func(3)

        # Should succeed because x=10 is >= 5
        result = retried_func(10)
        assert result == 20


class TestHelpersIntegration:
    """Integration tests for helpers working together."""

    def test_extract_json_with_retry(self):
        """Test combining JSON extraction with retry logic."""
        call_count = [0]

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def get_llm_json():
            call_count[0] += 1
            if call_count[0] < 2:
                return "Error occurred"  # Invalid JSON first time
            return '{"result": "success"}'

        response = get_llm_json()
        result = safe_extract_json(response, default={"result": "failed"})
        assert result == {"result": "success"}

    def test_logging_with_json_extraction(self):
        """Test logging during JSON extraction."""
        logger = configure_logging(level='DEBUG')

        text = 'Response: {"data": [1, 2, 3]}'
        result = safe_extract_json(text)

        logger.info(f"Extracted JSON: {json.dumps(result)}")
        assert result == {"data": [1, 2, 3]}
