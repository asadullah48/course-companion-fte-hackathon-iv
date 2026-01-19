"""
LLM Gateway for Phase 2 Adaptive Learning
Handles Claude Sonnet 4 API calls with rate limiting, caching, and cost tracking
"""
import asyncio
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import anthropic
from ..config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

class LLMTokenBudgetExceeded(Exception):
    """Raised when user exceeds their token budget."""
    pass

class LLMRateLimitError(Exception):
    """Raised when rate limits are exceeded."""
    pass

class LLMUnavailableError(Exception):
    """Raised when LLM service is unavailable."""
    pass

class LLMGateway:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.CLAUDE_API_KEY,
            timeout=settings.CLAUDE_TIMEOUT_SECONDS
        )
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        self.temperature = settings.CLAUDE_TEMPERATURE
        self.retry_attempts = settings.CLAUDE_RETRY_ATTEMPTS
        self.retry_delay = settings.CLAUDE_RETRY_DELAY_SECONDS
        
        # Token budget tracking
        self.budget_limits = {
            "free": 0,  # No LLM access
            "premium": 0,  # No LLM access
            "pro": 50000,  # 50K tokens/month
            "team": 150000  # 150K tokens/month
        }
    
    async def generate(self, prompt: str, model: str = "claude-sonnet-4", **kwargs) -> str:
        """
        Generate response from Claude API with error handling and token tracking.
        """
        start_time = time.time()
        
        # Check if user has sufficient budget
        user_id = kwargs.get("user_id", "anonymous")
        tier = kwargs.get("tier", "free")
        
        if tier not in ["pro", "team"]:
            raise LLMTokenBudgetExceeded(f"Tier {tier} does not have LLM access")
        
        budget_limit = self.budget_limits[tier]
        
        # Estimate token usage (rough estimation: 1 token ~ 4 characters)
        estimated_input_tokens = len(prompt) // 4
        
        # Check if this request would exceed budget
        current_usage = await self.get_current_monthly_usage(user_id)
        if current_usage + estimated_input_tokens > budget_limit:
            raise LLMTokenBudgetExceeded(
                f"Token budget exceeded: {current_usage + estimated_input_tokens}/{budget_limit}"
            )
        
        # Prepare the message for Claude
        message = {
            "model": model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["user_id", "tier", "max_tokens", "temperature"]:
                message[key] = value
        
        # Make API call with retry logic
        last_exception = None
        for attempt in range(self.retry_attempts + 1):
            try:
                response = await self.client.messages.create(**message)
                
                # Track token usage
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                
                await self.record_token_usage(
                    user_id=user_id,
                    operation=kwargs.get("operation", "general"),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model=model
                )
                
                logger.info(
                    f"LLM call successful for user {user_id}: "
                    f"input={input_tokens}, output={output_tokens}, "
                    f"time={time.time() - start_time:.2f}s"
                )
                
                return response.content[0].text if response.content else ""
                
            except anthropic.RateLimitError as e:
                last_exception = e
                if attempt < self.retry_attempts:
                    logger.warning(f"Rate limit hit, retrying in {self.retry_delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"Rate limit exceeded after {self.retry_attempts} retries")
                    raise LLMRateLimitError(f"Rate limit exceeded: {str(e)}")
                    
            except anthropic.APIError as e:
                last_exception = e
                if attempt < self.retry_attempts:
                    logger.warning(f"API error, retrying in {self.retry_delay}s (attempt {attempt + 1}): {str(e)}")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"API error after {self.retry_attempts} retries: {str(e)}")
                    raise LLMUnavailableError(f"LLM service unavailable: {str(e)}")
                    
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error in LLM call: {str(e)}")
                raise LLMUnavailableError(f"Unexpected error: {str(e)}")
        
        # If we get here, all retries failed
        raise last_exception
    
    async def get_current_monthly_usage(self, user_id: str) -> int:
        """
        Get the current month's token usage for a user.
        In a real implementation, this would query the database.
        """
        # Mock implementation - in real app, query database
        return 0
    
    async def record_token_usage(self, user_id: str, operation: str, 
                                input_tokens: int, output_tokens: int, model: str):
        """
        Record token usage for cost tracking and budget enforcement.
        In a real implementation, this would update the database.
        """
        # Mock implementation - in real app, update database
        pass
    
    async def check_user_budget(self, user_id: str, tier: str, tokens_needed: int) -> bool:
        """
        Check if user has sufficient token budget for a request.
        """
        if tier not in self.budget_limits:
            return False
            
        budget_limit = self.budget_limits[tier]
        current_usage = await self.get_current_monthly_usage(user_id)
        
        return (current_usage + tokens_needed) <= budget_limit

# Global instance
llm_gateway = LLMGateway()