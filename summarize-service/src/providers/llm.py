"""LiteLLM AI client."""

import logging

import litellm
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.exceptions import AIServiceError

logger = logging.getLogger(__name__)


class LLMClient:
    """LiteLLM AI client with retry logic."""

    def __init__(self):
        self.model = settings.llm_model
        self.api_base = settings.llm_base_url
        self.api_key = settings.google_api_key
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
        logger.info(f"🤖 LiteLLM initialized: {self.model} @ {self.api_base}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(self, prompt: str) -> str:
        """Generate text with retry logic."""
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_base=self.api_base,
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                custom_llm_provider="openai",  # OpenAI-compatible API
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LiteLLM API error: {e}")
            raise AIServiceError(f"Failed to generate content: {e}") from e
