"""
LLM client wrapper for OpenAI-compatible APIs with retry logic.
"""

import logging
import os
import time
from typing import Any, Optional

try:
    import requests
except ImportError:
    requests = None  # type: ignore

logger = logging.getLogger(__name__)


class LLMClient:
    """
    A generic LLM client for OpenAI-compatible API endpoints.

    This client supports automatic retries with exponential backoff and
    comprehensive error logging. It's designed to work with any OpenAI-style
    API (OpenAI, Azure, local models, etc.).

    Environment Variables:
        LLM_BASE_URL: Base URL for the API endpoint (e.g., "https://api.openai.com/v1")
        LLM_MODEL: Model name to use (e.g., "gpt-4", "claude-3-sonnet")
        LLM_API_KEY: API key for authentication

    Args:
        base_url: Optional override for LLM_BASE_URL environment variable
        model: Optional override for LLM_MODEL environment variable
        api_key: Optional override for LLM_API_KEY environment variable
        max_retries: Maximum number of retry attempts (default: 3)
        initial_retry_delay: Initial delay in seconds for exponential backoff (default: 1.0)

    Examples:
        >>> # Using environment variables
        >>> import os
        >>> os.environ['LLM_BASE_URL'] = 'https://api.openai.com/v1'
        >>> os.environ['LLM_MODEL'] = 'gpt-4'
        >>> os.environ['LLM_API_KEY'] = 'your-api-key'
        >>> client = LLMClient()
        >>> response = client.generate("What is the capital of France?")
        >>> print(response)
        'The capital of France is Paris.'

        >>> # Overriding settings
        >>> client = LLMClient(
        ...     base_url="https://api.anthropic.com/v1",
        ...     model="claude-3-sonnet-20240229",
        ...     api_key="your-anthropic-key"
        ... )
        >>> response = client.generate(
        ...     "Explain quantum computing",
        ...     max_tokens=500,
        ...     temperature=0.7
        ... )
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
    ):
        """Initialize the LLM client with configuration."""
        if requests is None:
            raise ImportError(
                "The 'requests' library is required for LLMClient. "
                "Install it with: pip install requests"
            )

        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.model = model or os.environ.get("LLM_MODEL")
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay

        if not self.base_url:
            raise ValueError(
                "base_url must be provided or LLM_BASE_URL environment variable must be set"
            )
        if not self.model:
            raise ValueError(
                "model must be provided or LLM_MODEL environment variable must be set"
            )
        if not self.api_key:
            raise ValueError(
                "api_key must be provided or LLM_API_KEY environment variable must be set"
            )

        logger.info(f"Initialized LLMClient with base_url={self.base_url}, model={self.model}")

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text from the LLM using the provided prompt.

        This method automatically retries failed requests with exponential backoff
        and logs all errors for debugging.

        Args:
            prompt: The input prompt/question for the LLM
            **kwargs: Additional parameters to pass to the API (e.g., temperature,
                     max_tokens, top_p, etc.)

        Returns:
            Generated text response from the LLM

        Raises:
            requests.exceptions.RequestException: If all retry attempts fail
            ValueError: If the API returns an unexpected response format

        Examples:
            >>> client = LLMClient()
            >>> response = client.generate("Hello, world!")
            >>> print(response)

            >>> # With additional parameters
            >>> response = client.generate(
            ...     "Write a haiku about coding",
            ...     temperature=0.9,
            ...     max_tokens=100
            ... )
        """
        if not isinstance(prompt, str):
            raise TypeError(f"prompt must be a string, got {type(prompt).__name__}")

        if not prompt.strip():
            raise ValueError("prompt cannot be empty")

        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url.rstrip('/')}/chat/completions"

        # Retry loop with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries}: Sending request to {url}")

                response = requests.post(url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()

                data = response.json()

                # Extract the generated text
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        logger.info(f"Successfully generated response ({len(content)} chars)")
                        return content
                    else:
                        raise ValueError("API returned empty content")
                else:
                    raise ValueError(f"Unexpected API response format: {data}")

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} timed out: {e}")

            except requests.exceptions.HTTPError as e:
                last_exception = e
                status_code = e.response.status_code if e.response else "unknown"
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed with HTTP {status_code}: {e}")

                # Don't retry on 4xx errors (except 429 rate limit)
                if e.response and 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    logger.error("Client error detected, not retrying")
                    raise

            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed with request error: {e}")

            except (ValueError, KeyError) as e:
                last_exception = e
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed with parsing error: {e}")

            # Calculate exponential backoff delay
            if attempt < self.max_retries - 1:
                delay = self.initial_retry_delay * (2**attempt)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)

        # All retries exhausted
        error_msg = f"All {self.max_retries} retry attempts failed"
        logger.error(error_msg)
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(error_msg)

    def __repr__(self) -> str:
        """Return a string representation of the client."""
        return f"LLMClient(base_url='{self.base_url}', model='{self.model}')"
