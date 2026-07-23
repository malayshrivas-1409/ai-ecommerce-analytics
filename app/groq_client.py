"""
GROQ API Client Wrapper
Completely isolated from existing code
"""

import os
from groq import Groq
from app.logger import logger


class GroqClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Latest available GROQ model
    
    def invoke(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Call GROQ API and return response
        
        Args:
            prompt: The prompt to send to GROQ
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from GROQ
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            logger.info(f"GROQ API call successful - {self.model}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GROQ API error: {e}")
            raise
