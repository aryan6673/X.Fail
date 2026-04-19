import os
from typing import Optional
from openai import OpenAI


class XAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        self.model = "grok-3"

    def call(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 4096) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return {
            "role": "assistant",
            "content": response.choices[0].message.content,
            "model": self.model,
            "stop_reason": response.choices[0].finish_reason,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        }
