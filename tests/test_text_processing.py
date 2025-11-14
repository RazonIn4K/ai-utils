"""Tests for text processing utilities."""

import pytest
from ai_utils import (
    clean_text,
    estimate_token_count,
    safe_truncate_tokens,
    merge_context_snippets,
    split_into_chunks,
    summarise_text,
)


class TestCleanText:
    """Tests for clean_text function."""

    def test_basic_whitespace_removal(self):
        assert clean_text("  Hello   World  ") == "Hello World"

    def test_newline_normalization(self):
        assert clean_text("Line1\n\nLine2\n\n\nLine3") == "Line1 Line2 Line3"

    def test_tab_normalization(self):
        assert clean_text("Col1\t\t\tCol2\tCol3") == "Col1 Col2 Col3"

    def test_mixed_whitespace(self):
        assert clean_text("  Text\n\twith  \n  mixed\t\tspaces  ") == "Text with mixed spaces"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_only_whitespace(self):
        assert clean_text("   \n\n\t\t   ") == ""

    def test_unicode_text(self):
        assert clean_text("  Hello  世界  ") == "Hello 世界"

    def test_emoji_text(self):
        assert clean_text("  Hello  👋  World  🌍  ") == "Hello 👋 World 🌍"

    def test_multilingual(self):
        text = "  Bonjour  le  monde  "
        assert clean_text(text) == "Bonjour le monde"

        text = "  Привет  мир  "
        assert clean_text(text) == "Привет мир"

    def test_preserves_punctuation(self):
        assert clean_text("Hello,  world!  How  are  you?") == "Hello, world! How are you?"

    def test_type_error(self):
        with pytest.raises(TypeError):
            clean_text(123)  # type: ignore

        with pytest.raises(TypeError):
            clean_text(None)  # type: ignore


class TestEstimateTokenCount:
    """Tests for estimate_token_count function."""

    def test_basic_counting(self):
        assert estimate_token_count("Hello world") == 2

    def test_sentence_counting(self):
        assert estimate_token_count("This is a test sentence.") == 5

    def test_empty_string(self):
        assert estimate_token_count("") == 0

    def test_whitespace_only(self):
        assert estimate_token_count("   \n\n\t   ") == 0

    def test_single_word(self):
        assert estimate_token_count("Hello") == 1

    def test_unicode_tokens(self):
        # Each character/word counts as a token when space-separated
        assert estimate_token_count("Hello 世界 test") == 3

    def test_punctuation_attached(self):
        # Punctuation attached to words counts as same token
        assert estimate_token_count("Hello, world!") == 2

    def test_multiple_spaces(self):
        # Multiple spaces should still count correctly
        assert estimate_token_count("word1    word2     word3") == 3

    def test_newlines(self):
        assert estimate_token_count("line1\nline2\nline3") == 3

    def test_type_error(self):
        with pytest.raises(TypeError):
            estimate_token_count(123)  # type: ignore


class TestSafeTruncateTokens:
    """Tests for safe_truncate_tokens function."""

    def test_basic_truncation(self):
        text = "This is a test sentence with many words"
        result = safe_truncate_tokens(text, max_tokens=4)
        assert result == "This is a test"

    def test_no_truncation_needed(self):
        text = "Short text"
        result = safe_truncate_tokens(text, max_tokens=10)
        assert result == text

    def test_exact_token_count(self):
        text = "One two three four five"
        result = safe_truncate_tokens(text, max_tokens=5)
        assert result == text

    def test_empty_string(self):
        assert safe_truncate_tokens("", max_tokens=10) == ""

    def test_zero_tokens(self):
        assert safe_truncate_tokens("Hello world", max_tokens=0) == ""

    def test_one_token(self):
        result = safe_truncate_tokens("Hello world test", max_tokens=1)
        assert result == "Hello"

    def test_unicode_text(self):
        text = "Hello 世界 test message"
        result = safe_truncate_tokens(text, max_tokens=2)
        assert result == "Hello 世界"

    def test_preserves_word_boundaries(self):
        text = "This is a very long sentence"
        result = safe_truncate_tokens(text, max_tokens=3)
        assert result == "This is a"
        assert "very" not in result

    def test_type_error_text(self):
        with pytest.raises(TypeError):
            safe_truncate_tokens(123, max_tokens=5)  # type: ignore

    def test_value_error_negative_tokens(self):
        with pytest.raises(ValueError):
            safe_truncate_tokens("text", max_tokens=-1)

    def test_value_error_non_int(self):
        with pytest.raises(ValueError):
            safe_truncate_tokens("text", max_tokens=3.5)  # type: ignore


class TestMergeContextSnippets:
    """Tests for merge_context_snippets function."""

    def test_basic_merge(self):
        snippets = ["First", "Second", "Third"]
        result = merge_context_snippets(snippets)
        assert result == "First\n\nSecond\n\nThird"

    def test_custom_separator(self):
        snippets = ["A", "B", "C"]
        result = merge_context_snippets(snippets, separator=" | ")
        assert result == "A | B | C"

    def test_empty_list(self):
        assert merge_context_snippets([]) == ""

    def test_filters_empty_strings(self):
        snippets = ["First", "", "Second", "   ", "Third"]
        result = merge_context_snippets(snippets)
        assert result == "First\n\nSecond\n\nThird"

    def test_all_empty_strings(self):
        snippets = ["", "   ", "\n\n"]
        assert merge_context_snippets(snippets) == ""

    def test_whitespace_trimming(self):
        snippets = ["  First  ", "  Second  "]
        result = merge_context_snippets(snippets)
        assert result == "First\n\nSecond"

    def test_single_snippet(self):
        result = merge_context_snippets(["Only one"])
        assert result == "Only one"

    def test_unicode_snippets(self):
        snippets = ["Hello", "世界", "Test"]
        result = merge_context_snippets(snippets, separator=" - ")
        assert result == "Hello - 世界 - Test"

    def test_type_error_not_list(self):
        with pytest.raises(TypeError):
            merge_context_snippets("not a list")  # type: ignore

    def test_type_error_separator(self):
        with pytest.raises(TypeError):
            merge_context_snippets(["a", "b"], separator=123)  # type: ignore

    def test_non_string_items_filtered(self):
        snippets = ["First", 123, "Second", None, "Third"]  # type: ignore
        result = merge_context_snippets(snippets)
        # Non-strings should be filtered out
        assert "First" in result
        assert "Second" in result
        assert "Third" in result


class TestSplitIntoChunks:
    """Tests for split_into_chunks function."""

    def test_basic_split(self):
        text = "One two three four five six seven eight"
        chunks = split_into_chunks(text, max_tokens=3)
        assert len(chunks) == 3
        assert all(estimate_token_count(chunk) <= 3 for chunk in chunks)

    def test_paragraph_preservation(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = split_into_chunks(text, max_tokens=10)
        assert len(chunks) == 3

    def test_no_split_needed(self):
        text = "Short text"
        chunks = split_into_chunks(text, max_tokens=10)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_empty_string(self):
        chunks = split_into_chunks("", max_tokens=10)
        assert chunks == []

    def test_whitespace_only(self):
        chunks = split_into_chunks("   \n\n   ", max_tokens=10)
        assert chunks == []

    def test_long_paragraph_split(self):
        # Single paragraph that exceeds limit should be split
        long_para = " ".join([f"word{i}" for i in range(100)])
        chunks = split_into_chunks(long_para, max_tokens=20)
        assert len(chunks) > 1
        assert all(estimate_token_count(chunk) <= 20 for chunk in chunks)

    def test_mixed_paragraph_lengths(self):
        text = "Short.\n\n" + " ".join([f"word{i}" for i in range(50)]) + "\n\nAnother short."
        chunks = split_into_chunks(text, max_tokens=20)
        # Should have multiple chunks
        assert len(chunks) >= 2

    def test_unicode_text(self):
        text = "Hello 世界\n\nTest message\n\n更多文本"
        chunks = split_into_chunks(text, max_tokens=5)
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_type_error_text(self):
        with pytest.raises(TypeError):
            split_into_chunks(123, max_tokens=10)  # type: ignore

    def test_value_error_zero_tokens(self):
        with pytest.raises(ValueError):
            split_into_chunks("text", max_tokens=0)

    def test_value_error_negative_tokens(self):
        with pytest.raises(ValueError):
            split_into_chunks("text", max_tokens=-5)

    def test_single_token_limit(self):
        text = "word1 word2 word3 word4"
        chunks = split_into_chunks(text, max_tokens=1)
        assert len(chunks) == 4
        assert all(estimate_token_count(chunk) == 1 for chunk in chunks)


class TestSummariseText:
    """Tests for summarise_text function."""

    def test_basic_summarization(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = summarise_text(text, max_chars=50)
        assert len(result) <= 50
        assert "First sentence." in result or "First" in result
        assert "..." in result

    def test_no_summarization_needed(self):
        text = "Short text."
        result = summarise_text(text, max_chars=100)
        assert result == text

    def test_exact_length(self):
        text = "Exactly this."
        result = summarise_text(text, max_chars=len(text))
        assert result == text

    def test_single_sentence(self):
        text = "This is a single very long sentence that needs to be truncated."
        result = summarise_text(text, max_chars=30)
        assert len(result) <= 30
        assert result.endswith("...")

    def test_keeps_first_and_last(self):
        text = "First sentence. Middle content. Last sentence."
        result = summarise_text(text, max_chars=50)
        # Should try to keep first and last
        assert "First" in result or "Last" in result

    def test_very_short_limit(self):
        text = "This is a test sentence."
        result = summarise_text(text, max_chars=10)
        assert len(result) <= 10

    def test_empty_string(self):
        # Should handle gracefully
        text = ""
        result = summarise_text(text, max_chars=100)
        assert result == ""

    def test_unicode_text(self):
        text = "こんにちは世界。これはテストです。最後の文。"
        result = summarise_text(text, max_chars=20)
        assert len(result) <= 20

    def test_type_error_text(self):
        with pytest.raises(TypeError):
            summarise_text(123, max_chars=50)  # type: ignore

    def test_value_error_zero_chars(self):
        with pytest.raises(ValueError):
            summarise_text("text", max_chars=0)

    def test_value_error_negative_chars(self):
        with pytest.raises(ValueError):
            summarise_text("text", max_chars=-10)


class TestEdgeCases:
    """Test edge cases and multilingual support."""

    def test_very_long_text(self):
        """Test with very long text (1000+ words)."""
        long_text = " ".join([f"word{i}" for i in range(1000)])
        chunks = split_into_chunks(long_text, max_tokens=100)
        assert all(estimate_token_count(chunk) <= 100 for chunk in chunks)

    def test_mixed_languages(self):
        """Test with mixed language text."""
        text = "English text. 中文文本。Русский текст. النص العربي."
        cleaned = clean_text(text)
        assert "English" in cleaned
        assert "中文文本" in cleaned

    def test_emoji_handling(self):
        """Test handling of emojis."""
        text = "Hello 👋 World 🌍 Test 🚀"
        tokens = estimate_token_count(text)
        assert tokens == 6  # Each word/emoji counts as token

    def test_special_characters(self):
        """Test special characters and symbols."""
        text = "Test @mention #hashtag $price €100"
        cleaned = clean_text(text)
        assert "@mention" in cleaned
        assert "#hashtag" in cleaned

    def test_rtl_text(self):
        """Test right-to-left text (Arabic, Hebrew)."""
        text = "مرحبا بالعالم"
        cleaned = clean_text(text)
        assert cleaned == text.strip()

    def test_mixed_newline_types(self):
        """Test different newline types."""
        text = "Line1\nLine2\r\nLine3\rLine4"
        cleaned = clean_text(text)
        # All newlines should be normalized to spaces
        assert "Line1" in cleaned
        assert "Line4" in cleaned

    def test_extremely_long_word(self):
        """Test with unreasonably long 'word'."""
        long_word = "a" * 10000
        result = safe_truncate_tokens(long_word, max_tokens=1)
        assert result == long_word

    def test_repeated_punctuation(self):
        """Test repeated punctuation."""
        text = "Wait... what??? Really!!!"
        cleaned = clean_text(text)
        assert "Wait..." in cleaned
        assert "what???" in cleaned
