"""
Example: JSON Extraction from LLM Responses

This example shows how to safely extract JSON from LLM responses
that may contain additional text or formatting.
"""

from ai_utils import safe_extract_json, configure_logging


def main():
    print("=" * 60)
    print("JSON EXTRACTION EXAMPLES")
    print("=" * 60)

    # Configure logging to see extraction attempts
    logger = configure_logging(level='INFO')

    # Example 1: Clean JSON response
    print("\n1. CLEAN JSON")
    print("-" * 60)

    clean_response = '{"name": "Alice", "age": 30, "city": "Paris"}'
    result = safe_extract_json(clean_response)
    print(f"Input:  {clean_response}")
    print(f"Output: {result}")

    # Example 2: JSON with explanatory text
    print("\n2. JSON WITH EXPLANATORY TEXT")
    print("-" * 60)

    llm_response = """
    Here's the information you requested:
    {"user": "Bob", "role": "developer", "active": true}
    Let me know if you need anything else!
    """
    result = safe_extract_json(llm_response)
    print(f"Input:  {repr(llm_response[:50])}...")
    print(f"Output: {result}")

    # Example 3: JSON in markdown code block
    print("\n3. JSON IN MARKDOWN CODE BLOCK")
    print("-" * 60)

    markdown_response = """
    Sure! Here's the data in JSON format:

    ```json
    {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ],
        "total": 2
    }
    ```

    Hope this helps!
    """
    result = safe_extract_json(markdown_response)
    print(f"Extracted items: {result.get('items', [])}")
    print(f"Total: {result.get('total', 0)}")

    # Example 4: Multiple JSON objects
    print("\n4. MULTIPLE JSON OBJECTS")
    print("-" * 60)

    multi_response = """
    First object: {"type": "A", "value": 1}
    Second object: {"type": "B", "value": 2}
    Third object: {"type": "C", "value": 3}
    """

    # Extract all JSON objects
    results = safe_extract_json(multi_response, allow_multiple=True)
    print(f"Found {len(results)} JSON objects:")
    for i, obj in enumerate(results, 1):
        print(f"  {i}. {obj}")

    # Example 5: Invalid JSON with default fallback
    print("\n5. INVALID JSON WITH FALLBACK")
    print("-" * 60)

    invalid_response = "Sorry, I couldn't process that request."
    result = safe_extract_json(invalid_response, default={"error": "No JSON found"})
    print(f"Input:  {invalid_response}")
    print(f"Output: {result}")

    # Example 6: Nested complex JSON
    print("\n6. NESTED COMPLEX JSON")
    print("-" * 60)

    complex_response = """
    ```
    {
        "analysis": {
            "sentiment": "positive",
            "confidence": 0.95,
            "keywords": ["great", "excellent", "amazing"]
        },
        "metadata": {
            "processed_at": "2024-01-15",
            "model": "gpt-4"
        }
    }
    ```
    """
    result = safe_extract_json(complex_response)
    print(f"Sentiment: {result.get('analysis', {}).get('sentiment')}")
    print(f"Confidence: {result.get('analysis', {}).get('confidence')}")
    print(f"Keywords: {result.get('analysis', {}).get('keywords')}")

    # Example 7: Real-world LLM structured output
    print("\n7. REAL-WORLD STRUCTURED OUTPUT")
    print("-" * 60)

    structured_response = """
    I'll extract the entities from that text for you:

    ```json
    {
        "people": ["John Smith", "Jane Doe"],
        "organizations": ["Acme Corp", "Tech Innovations Inc"],
        "locations": ["New York", "San Francisco"],
        "dates": ["2024-01-15", "2024-02-20"]
    }
    ```

    The extraction was successful with high confidence.
    """

    result = safe_extract_json(structured_response)

    if result:
        print("Extracted entities:")
        for category, entities in result.items():
            print(f"  {category.title()}: {', '.join(entities)}")
    else:
        print("No entities found")

    # Example 8: Error handling
    print("\n8. ERROR HANDLING IN PRODUCTION")
    print("-" * 60)

    def process_llm_response(response: str):
        """Example function showing production usage."""
        result = safe_extract_json(response, default=None)

        if result is None:
            logger.warning("Failed to extract JSON from response")
            return {"status": "error", "message": "Invalid response format"}

        logger.info(f"Successfully extracted JSON with {len(result)} keys")
        return {"status": "success", "data": result}

    # Test with valid and invalid responses
    valid = '{"status": "ok", "count": 42}'
    invalid = "This is just text, no JSON here"

    print("\nProcessing valid response:")
    print(f"  Result: {process_llm_response(valid)}")

    print("\nProcessing invalid response:")
    print(f"  Result: {process_llm_response(invalid)}")


if __name__ == "__main__":
    main()
