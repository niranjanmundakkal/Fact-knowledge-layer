"""
Unified LLM adapter supporting Gemini, Groq, OpenAI, and Offline fallback.
"""

import os
import json
import re
from typing import Optional, Dict, Any
from app.core.config import settings

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.gemini_key = api_key if (provider == "gemini" and api_key) else settings.GEMINI_API_KEY
        self.groq_key = api_key if (provider == "groq" and api_key) else settings.GROQ_API_KEY
        self.openai_key = api_key if (provider == "openai" and api_key) else settings.OPENAI_API_KEY
        
        self.gemini_model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self._init_client()

    def _init_client(self):
        self.gemini_client = None
        if self.gemini_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                print(f"[LLMClient] Failed to initialize Google GenAI: {e}")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from LLM with automatic provider routing."""
        # 1. Try Gemini
        if self.gemini_client and self.provider == "gemini":
            try:
                contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                # Use client generate_content
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=contents,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"[LLMClient] Gemini generate_text error: {e}")

        # 2. Try Groq
        if self.groq_key and self.provider == "groq":
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_key)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                chat = client.chat.completions.create(
                    messages=messages,
                    model="qwen/qwen3.6-27b",
                    temperature=0.1,
                    timeout=8.0
                )
                return chat.choices[0].message.content
            except Exception as e:
                print(f"[LLMClient] Groq generate_text error: {e}")

        return ""

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Any:
        """Generate and parse structured JSON output."""
        text = self.generate_text(prompt, system_prompt)
        if not text:
            return None

        # Clean JSON markdown blocks
        cleaned = text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback regex search for JSON array or object
            json_match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except Exception:
                    pass
        return None

llm_client = LLMClient()
