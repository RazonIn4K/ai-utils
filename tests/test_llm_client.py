"""Tests for LLMClient."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Try to import LLMClient
try:
    from ai_utils import LLMClient
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    LLMClient = None


@pytest.mark.skipif(not HAS_REQUESTS, reason="requests library not installed")
class TestLLMClient:
    """Tests for LLMClient class."""

    def setup_method(self):
        """Set up test environment variables."""
        self.original_env = {
            'LLM_BASE_URL': os.environ.get('LLM_BASE_URL'),
            'LLM_MODEL': os.environ.get('LLM_MODEL'),
            'LLM_API_KEY': os.environ.get('LLM_API_KEY'),
        }
        os.environ['LLM_BASE_URL'] = 'https://api.test.com/v1'
        os.environ['LLM_MODEL'] = 'test-model'
        os.environ['LLM_API_KEY'] = 'test-key'

    def teardown_method(self):
        """Restore original environment variables."""
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_initialization_with_env_vars(self):
        """Test client initialization with environment variables."""
        client = LLMClient()
        assert client.base_url == 'https://api.test.com/v1'
        assert client.model == 'test-model'
        assert client.api_key == 'test-key'

    def test_initialization_with_overrides(self):
        """Test client initialization with parameter overrides."""
        client = LLMClient(
            base_url='https://custom.api.com',
            model='custom-model',
            api_key='custom-key'
        )
        assert client.base_url == 'https://custom.api.com'
        assert client.model == 'custom-model'
        assert client.api_key == 'custom-key'

    def test_initialization_missing_base_url(self):
        """Test that initialization fails without base_url."""
        os.environ.pop('LLM_BASE_URL', None)
        with pytest.raises(ValueError, match="base_url must be provided"):
            LLMClient()

    def test_initialization_missing_model(self):
        """Test that initialization fails without model."""
        os.environ.pop('LLM_MODEL', None)
        with pytest.raises(ValueError, match="model must be provided"):
            LLMClient()

    def test_initialization_missing_api_key(self):
        """Test that initialization fails without api_key."""
        os.environ.pop('LLM_API_KEY', None)
        with pytest.raises(ValueError, match="api_key must be provided"):
            LLMClient()

    def test_custom_retry_settings(self):
        """Test initialization with custom retry settings."""
        client = LLMClient(max_retries=5, initial_retry_delay=2.0)
        assert client.max_retries == 5
        assert client.initial_retry_delay == 2.0

    @patch('ai_utils.llm_client.requests.post')
    def test_successful_generate(self, mock_post):
        """Test successful text generation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Generated response'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LLMClient()
        result = client.generate("Test prompt")

        assert result == "Generated response"
        mock_post.assert_called_once()

        # Verify request structure
        call_args = mock_post.call_args
        assert 'json' in call_args.kwargs
        assert call_args.kwargs['json']['model'] == 'test-model'
        assert call_args.kwargs['json']['messages'][0]['content'] == "Test prompt"

    @patch('ai_utils.llm_client.requests.post')
    def test_generate_with_kwargs(self, mock_post):
        """Test generation with additional parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LLMClient()
        client.generate("Test", temperature=0.7, max_tokens=100)

        call_args = mock_post.call_args
        assert call_args.kwargs['json']['temperature'] == 0.7
        assert call_args.kwargs['json']['max_tokens'] == 100

    @patch('ai_utils.llm_client.requests.post')
    def test_empty_prompt_error(self, mock_post):
        """Test that empty prompt raises ValueError."""
        client = LLMClient()
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            client.generate("")

        with pytest.raises(ValueError, match="prompt cannot be empty"):
            client.generate("   ")

    @patch('ai_utils.llm_client.requests.post')
    def test_non_string_prompt_error(self, mock_post):
        """Test that non-string prompt raises TypeError."""
        client = LLMClient()
        with pytest.raises(TypeError, match="prompt must be a string"):
            client.generate(123)  # type: ignore

    @patch('ai_utils.llm_client.requests.post')
    @patch('ai_utils.llm_client.time.sleep')
    def test_retry_on_timeout(self, mock_sleep, mock_post):
        """Test retry logic on timeout."""
        import requests

        # First two attempts timeout, third succeeds
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Success after retry'}}]
        }
        mock_response.raise_for_status = Mock()

        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            mock_response
        ]

        client = LLMClient(max_retries=3)
        result = client.generate("Test")

        assert result == "Success after retry"
        assert mock_post.call_count == 3
        assert mock_sleep.call_count == 2  # Two retries with delays

    @patch('ai_utils.llm_client.requests.post')
    @patch('ai_utils.llm_client.time.sleep')
    def test_retry_exhaustion(self, mock_sleep, mock_post):
        """Test that all retries are exhausted."""
        import requests

        mock_post.side_effect = requests.exceptions.Timeout("Always timeout")

        client = LLMClient(max_retries=3)

        with pytest.raises(requests.exceptions.Timeout):
            client.generate("Test")

        assert mock_post.call_count == 3

    @patch('ai_utils.llm_client.requests.post')
    def test_no_retry_on_4xx_error(self, mock_post):
        """Test that 4xx errors (except 429) are not retried."""
        import requests

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_post.return_value = mock_response

        client = LLMClient(max_retries=3)

        with pytest.raises(requests.exceptions.HTTPError):
            client.generate("Test")

        # Should only be called once, no retries
        assert mock_post.call_count == 1

    @patch('ai_utils.llm_client.requests.post')
    @patch('ai_utils.llm_client.time.sleep')
    def test_retry_on_429_rate_limit(self, mock_sleep, mock_post):
        """Test retry on 429 rate limit error."""
        import requests

        # First attempt gets rate limited, second succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response_429
        )

        mock_response_success = Mock()
        mock_response_success.json.return_value = {
            'choices': [{'message': {'content': 'Success'}}]
        }
        mock_response_success.raise_for_status = Mock()

        mock_post.side_effect = [mock_response_429, mock_response_success]

        client = LLMClient(max_retries=3)
        result = client.generate("Test")

        assert result == "Success"
        assert mock_post.call_count == 2

    @patch('ai_utils.llm_client.requests.post')
    def test_exponential_backoff(self, mock_post):
        """Test exponential backoff delay calculation."""
        import requests
        import time

        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        client = LLMClient(max_retries=3, initial_retry_delay=1.0)

        with patch('ai_utils.llm_client.time.sleep') as mock_sleep:
            with pytest.raises(requests.exceptions.Timeout):
                client.generate("Test")

            # Verify exponential backoff: 1s, 2s
            assert mock_sleep.call_count == 2
            calls = [call.args[0] for call in mock_sleep.call_args_list]
            assert calls[0] == 1.0  # First retry: 1 * 2^0
            assert calls[1] == 2.0  # Second retry: 1 * 2^1

    @patch('ai_utils.llm_client.requests.post')
    def test_unexpected_response_format(self, mock_post):
        """Test handling of unexpected API response format."""
        mock_response = Mock()
        mock_response.json.return_value = {'unexpected': 'format'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LLMClient()

        with pytest.raises(ValueError, match="Unexpected API response format"):
            client.generate("Test")

    @patch('ai_utils.llm_client.requests.post')
    def test_empty_content_in_response(self, mock_post):
        """Test handling of empty content in API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': ''}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LLMClient()

        with pytest.raises(ValueError, match="API returned empty content"):
            client.generate("Test")

    def test_repr(self):
        """Test string representation of client."""
        client = LLMClient()
        repr_str = repr(client)
        assert 'LLMClient' in repr_str
        assert 'https://api.test.com/v1' in repr_str
        assert 'test-model' in repr_str

    @patch('ai_utils.llm_client.requests.post')
    def test_url_construction(self, mock_post):
        """Test that URL is constructed correctly."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test with trailing slash
        client = LLMClient(base_url='https://api.test.com/v1/')
        client.generate("Test")

        call_args = mock_post.call_args
        url = call_args.args[0]
        assert url == 'https://api.test.com/v1/chat/completions'

        # Test without trailing slash
        client = LLMClient(base_url='https://api.test.com/v1')
        mock_post.reset_mock()
        client.generate("Test")

        call_args = mock_post.call_args
        url = call_args.args[0]
        assert url == 'https://api.test.com/v1/chat/completions'

    @patch('ai_utils.llm_client.requests.post')
    def test_authorization_header(self, mock_post):
        """Test that authorization header is set correctly."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LLMClient()
        client.generate("Test")

        call_args = mock_post.call_args
        headers = call_args.kwargs['headers']
        assert headers['Authorization'] == 'Bearer test-key'
        assert headers['Content-Type'] == 'application/json'
