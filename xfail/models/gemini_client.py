import os
from typing import Optional
import google.generativeai as genai


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash"
        self.client = genai.GenerativeModel(self.model_name)

    def call(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> dict:
        text_content = "\n".join([m["content"] for m in messages])
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        response = self.client.generate_content(
            text_content,
            generation_config=generation_config,
            stream=False,
        )
        
        return {
            "role": "assistant",
            "content": response.text,
            "model": self.model_name,
            "stop_reason": response.candidates[0].finish_reason.name if response.candidates else "unknown",
            "usage": {
                "input_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "output_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0,
            }
        }
