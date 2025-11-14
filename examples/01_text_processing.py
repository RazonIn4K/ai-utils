"""
Example: Text Processing Utilities

This example demonstrates the core text processing functions.
"""

from ai_utils import (
    clean_text,
    estimate_token_count,
    safe_truncate_tokens,
    merge_context_snippets,
)


def main():
    print("=" * 60)
    print("TEXT PROCESSING EXAMPLES")
    print("=" * 60)

    # Example 1: Clean messy text
    print("\n1. CLEANING MESSY TEXT")
    print("-" * 60)
    messy_text = """
        This is   some text    with


        irregular    spacing and
        \t\ttabs    everywhere!
    """
    cleaned = clean_text(messy_text)
    print(f"Original:\n{repr(messy_text)}\n")
    print(f"Cleaned:\n{cleaned}")

    # Example 2: Estimate token counts
    print("\n2. ESTIMATING TOKEN COUNTS")
    print("-" * 60)
    texts = [
        "Hello world!",
        "This is a longer sentence with more words.",
        "AI and ML are transforming technology.",
    ]
    for text in texts:
        count = estimate_token_count(text)
        print(f"{count:3d} tokens: {text}")

    # Example 3: Truncate text safely
    print("\n3. SAFE TOKEN TRUNCATION")
    print("-" * 60)
    long_text = "The quick brown fox jumps over the lazy dog repeatedly in the forest"
    for max_tokens in [3, 5, 10]:
        truncated = safe_truncate_tokens(long_text, max_tokens=max_tokens)
        actual_tokens = estimate_token_count(truncated)
        print(f"Max {max_tokens} tokens ({actual_tokens} actual): {truncated}")

    # Example 4: Merge context snippets
    print("\n4. MERGING CONTEXT SNIPPETS")
    print("-" * 60)

    # Code documentation snippets
    snippets = [
        "Function: calculate_total(items: list) -> float",
        "Description: Calculates the total price of all items",
        "Returns: Total price as a float",
        "",  # This will be filtered out
        "Example: calculate_total([10, 20, 30]) -> 60.0"
    ]

    merged = merge_context_snippets(snippets, separator="\n")
    print("Merged documentation:")
    print(merged)

    print("\n" + "=" * 60)
    print("With custom separator:")
    print("=" * 60)

    merged_custom = merge_context_snippets(snippets, separator=" | ")
    print(merged_custom)


if __name__ == "__main__":
    main()
