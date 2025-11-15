"""
Example: Using LLMClient

This example demonstrates how to use the LLMClient wrapper for
making robust API calls with automatic retries.

Note: This example requires the requests library and valid API credentials.
Run: pip install ai-utils[llm]
"""

import os
from ai_utils import LLMClient, split_into_chunks, estimate_token_count

TOKEN_MODEL = "gpt-3.5-turbo"


def example_basic_usage():
    """Basic LLM client usage."""
    print("=" * 60)
    print("BASIC LLM CLIENT USAGE")
    print("=" * 60)

    # Set up environment variables (in practice, use .env file or similar)
    os.environ['LLM_BASE_URL'] = 'https://api.openai.com/v1'
    os.environ['LLM_MODEL'] = 'gpt-3.5-turbo'
    os.environ['LLM_API_KEY'] = 'your-api-key-here'  # Replace with real key

    try:
        # Initialize client
        client = LLMClient()
        print(f"Initialized: {client}\n")

        # Simple question
        print("Asking a simple question...")
        response = client.generate("What is the capital of France?")
        print(f"Response: {response}\n")

        # With custom parameters
        print("Generating creative text...")
        response = client.generate(
            "Write a haiku about programming",
            temperature=0.9,
            max_tokens=50
        )
        print(f"Haiku: {response}\n")

    except Exception as e:
        print(f"Note: This example requires valid API credentials.")
        print(f"Error: {e}")


def example_processing_chunks():
    """Process long document in chunks."""
    print("\n" + "=" * 60)
    print("PROCESSING DOCUMENT CHUNKS WITH LLM")
    print("=" * 60)

    # Sample long document
    document = """
    Artificial Intelligence has transformed how we approach problem-solving.

    Machine learning models can now understand context and generate human-like text.

    The applications range from customer service to content creation.

    However, we must consider ethical implications and potential biases.

    The future of AI depends on responsible development and deployment.
    """

    # Split into chunks
    chunks = split_into_chunks(document.strip(), max_tokens=50, overlap_tokens=10)

    print(f"Document split into {len(chunks)} chunks\n")

    try:
        client = LLMClient()

        summaries = []
        for i, chunk in enumerate(chunks, 1):
            token_count = estimate_token_count(chunk, model=TOKEN_MODEL)
            print(f"Processing chunk {i}/{len(chunks)} ({token_count} tokens)...")

            # In real usage, this would make actual API calls
            # summary = client.generate(f"Summarize: {chunk}", max_tokens=30)
            # summaries.append(summary)

            # For demo without API key:
            print(f"  Would send: {chunk[:50]}...")
            summaries.append(f"[Summary of chunk {i}]")

        print("\nAll chunks processed!")
        print("Summaries:", summaries)

    except Exception as e:
        print(f"Note: This example requires valid API credentials.")
        print(f"Simulating output without actual API calls.")


def example_error_handling():
    """Demonstrate error handling and retries."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING AND RETRIES")
    print("=" * 60)

    try:
        # Client with custom retry settings
        client = LLMClient(
            max_retries=5,
            initial_retry_delay=2.0
        )

        print("Client configured with:")
        print(f"  - Max retries: {client.max_retries}")
        print(f"  - Initial delay: {client.initial_retry_delay}s")
        print(f"  - Backoff: exponential (2x)\n")

        # The client will automatically retry on failures
        # response = client.generate("Test prompt")

        print("Retry logic:")
        print("  1. Attempt 1: If fails, wait 2s")
        print("  2. Attempt 2: If fails, wait 4s")
        print("  3. Attempt 3: If fails, wait 8s")
        print("  4. Attempt 4: If fails, wait 16s")
        print("  5. Attempt 5: If fails, raise exception")

    except Exception as e:
        print(f"\nNote: {e}")


def example_multiple_providers():
    """Use different LLM providers."""
    print("\n" + "=" * 60)
    print("WORKING WITH DIFFERENT PROVIDERS")
    print("=" * 60)

    providers = {
        "OpenAI": {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY", "sk-..."),
        },
        "Azure OpenAI": {
            "base_url": "https://your-resource.openai.azure.com/openai/deployments",
            "model": "gpt-4",
            "api_key": os.getenv("AZURE_OPENAI_KEY", "..."),
        },
        "Local (LM Studio)": {
            "base_url": "http://localhost:1234/v1",
            "model": "local-model",
            "api_key": "not-needed",
        },
    }

    for provider_name, config in providers.items():
        print(f"\n{provider_name}:")
        print(f"  URL: {config['base_url']}")
        print(f"  Model: {config['model']}")

        try:
            client = LLMClient(**config)
            print(f"  Status: ✓ Initialized")
            # response = client.generate("Hello!")
        except Exception as e:
            print(f"  Status: ✗ {e}")


def main():
    """Run all examples."""
    print("\n" + "🤖 " * 20 + "\n")
    example_basic_usage()
    example_processing_chunks()
    example_error_handling()
    example_multiple_providers()
    print("\n" + "🤖 " * 20 + "\n")


if __name__ == "__main__":
    main()
