"""
Example: Chunking Long Documents

This example shows how to split long documents into manageable chunks
while preserving paragraph structure.
"""

from ai_utils import split_into_chunks, estimate_token_count


def main():
    print("=" * 60)
    print("DOCUMENT CHUNKING EXAMPLES")
    print("=" * 60)

    # Example 1: Simple text chunking
    print("\n1. BASIC CHUNKING")
    print("-" * 60)

    simple_text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10"
    chunks = split_into_chunks(simple_text, max_tokens=3)

    print(f"Original text ({estimate_token_count(simple_text)} tokens):")
    print(simple_text)
    print(f"\nSplit into {len(chunks)} chunks (max 3 tokens each):")
    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i} ({estimate_token_count(chunk)} tokens): {chunk}")

    # Example 2: Paragraph-aware chunking
    print("\n2. PARAGRAPH-AWARE CHUNKING")
    print("-" * 60)

    document = """
    Introduction: This is the first paragraph. It introduces the topic.

    Background: This paragraph provides background information about the subject matter.

    Analysis: Here we analyze the data and present our findings in detail.

    Conclusion: Finally, we summarize our key points and recommendations.
    """

    chunks = split_into_chunks(document.strip(), max_tokens=50)

    print(f"Document with {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks, 1):
        tokens = estimate_token_count(chunk)
        preview = chunk[:60] + "..." if len(chunk) > 60 else chunk
        print(f"\nChunk {i} ({tokens} tokens):")
        print(f"  {preview}")

    # Example 3: Long transcript chunking
    print("\n3. TRANSCRIPT CHUNKING")
    print("-" * 60)

    transcript = """
    Speaker 1: Welcome everyone to today's meeting. Let's discuss our Q4 goals.

    Speaker 2: Thank you for having me. I'd like to start by reviewing our progress so far.

    Speaker 1: That sounds great. Please go ahead.

    Speaker 2: We've completed 80% of our planned features and received positive user feedback. However, we're slightly behind on the mobile app development.

    Speaker 3: I can provide some context on the mobile delays. We encountered unexpected API limitations that required architectural changes.

    Speaker 1: I see. What's the estimated timeline for completion?

    Speaker 3: We should be back on track within two weeks. The new architecture is more robust and will prevent similar issues in the future.

    Speaker 2: That's reassuring. Let's make sure to document these learnings for the team.
    """

    # Chunk for processing with an LLM (e.g., 100 token chunks)
    chunks = split_into_chunks(transcript.strip(), max_tokens=100)

    print(f"Transcript split into {len(chunks)} chunks for LLM processing:\n")
    for i, chunk in enumerate(chunks, 1):
        tokens = estimate_token_count(chunk)
        lines = chunk.count('\n') + 1
        print(f"Chunk {i}: {tokens} tokens, {lines} lines")
        print(f"First line: {chunk.split(chr(10))[0][:50]}...")
        print()

    # Example 4: Handling very long paragraphs
    print("\n4. HANDLING LONG PARAGRAPHS")
    print("-" * 60)

    long_paragraph = " ".join([f"word{i}" for i in range(1, 101)])
    chunks = split_into_chunks(long_paragraph, max_tokens=20)

    print(f"Long paragraph (100 words) split into {len(chunks)} chunks of max 20 tokens:")
    for i, chunk in enumerate(chunks, 1):
        tokens = estimate_token_count(chunk)
        word_range = chunk.split()[0] + " ... " + chunk.split()[-1]
        print(f"  Chunk {i}: {tokens} tokens ({word_range})")

    # Example 5: Optimal chunk size for different LLMs
    print("\n5. OPTIMAL CHUNK SIZES FOR DIFFERENT USE CASES")
    print("-" * 60)

    sample_doc = "Lorem ipsum " * 200  # 400 words

    use_cases = [
        ("GPT-3.5 with room for response", 2000),
        ("GPT-4 with room for response", 4000),
        ("Embedding generation", 500),
        ("Quick summaries", 1000),
    ]

    for use_case, max_tokens in use_cases:
        chunks = split_into_chunks(sample_doc, max_tokens=max_tokens)
        print(f"{use_case:35s}: {len(chunks):2d} chunks of ~{max_tokens} tokens")


if __name__ == "__main__":
    main()
