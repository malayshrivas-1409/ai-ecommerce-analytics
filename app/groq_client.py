"""
GROQ API Client Wrapper with Bedrock Fallback
GROK is PRIMARY. Bedrock (Llama 70B) is FALLBACK ONLY.
Bedrock is only called if GROK fails.
"""

import os
import json
from groq import Groq
from app.logger import logger


class GroqClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # PRIMARY: GROQ model
        
        # Initialize Bedrock FALLBACK if configured
        self.bedrock_client = None
        self.bedrock_model = os.getenv("AWS_BEDROCK_MODEL", "meta.llama3-70b-instruct-v1:0")
        
        # Only initialize if fallback is enabled
        if os.getenv("AI_PROVIDER") in ["groq_with_bedrock_fallback"]:
            try:
                import boto3
                self.bedrock_client = boto3.client('bedrock-runtime', region_name=os.getenv("AWS_REGION", "us-east-1"))
                logger.info("Bedrock fallback client initialized (used only if GROQ fails)")
            except Exception as e:
                logger.warning(f"Bedrock fallback not available: {e}")
    
    def invoke(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Call GROQ API first (PRIMARY).
        If GROQ fails, fallback to Bedrock (SECONDARY).
        Bedrock is NEVER called unless GROQ fails.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from GROQ or Bedrock (fallback)
        """
        try:
            # PRIMARY: Try GROQ first
            logger.info(f"Attempting GROQ (primary)")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            logger.info(f"✅ GROQ call successful (primary provider used)")
            return response.choices[0].message.content
            
        except Exception as grok_error:
            # GROQ failed, log the error
            logger.warning(f"GROQ failed: {grok_error}. Attempting fallback...")
            
            # FALLBACK: Try Bedrock only if GROQ fails
            if self.bedrock_client:
                try:
                    logger.info(f"Calling Bedrock fallback (only because GROQ failed)")
                    result = self._invoke_bedrock(prompt, max_tokens)
                    logger.info(f"✅ Bedrock fallback successful")
                    return result
                except Exception as bedrock_error:
                    logger.error(f"Both GROQ and Bedrock failed: GROQ={grok_error}, Bedrock={bedrock_error}")
                    raise Exception(f"All AI providers failed. Primary (GROQ): {grok_error}")
            else:
                logger.error(f"GROQ failed and Bedrock fallback not available: {grok_error}")
                raise
    
    def _invoke_bedrock(self, prompt: str, max_tokens: int) -> str:
        """
        Call Bedrock - FALLBACK ONLY
        This is only invoked if GROQ fails.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text from Bedrock
        """
        try:
            body = json.dumps({
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract text based on model response format
            if 'generation' in response_body:
                return response_body['generation']
            elif 'generations' in response_body:
                return response_body['generations'][0]['text']
            else:
                return str(response_body)
                
        except Exception as e:
            logger.error(f"Bedrock fallback failed: {e}")
            raise
