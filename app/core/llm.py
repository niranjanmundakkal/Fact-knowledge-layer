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
        self.cooldowns: Dict[str, float] = {}
        self._init_client()

    def _init_client(self):
        self.gemini_client = None
        if self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                self.gemini_client = genai.Client(
                    api_key=self.gemini_key,
                    http_options=types.HttpOptions(timeout=10000)
                )
            except Exception as e:
                print(f"[LLMClient] Failed to initialize Google GenAI: {e}")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from LLM with automatic provider routing and resilient fallback."""
        import time

        # Helper for Gemini
        def _call_gemini():
            if time.time() < self.cooldowns.get("gemini", 0):
                return ""
            if self.gemini_client:
                try:
                    contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                    response = self.gemini_client.models.generate_content(
                        model=self.gemini_model,
                        contents=contents,
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        self.cooldowns["gemini"] = time.time() + 3600
                        print(f"[LLMClient] Gemini quota exhausted (429); cooling down for 1 hour.")
                    elif "503" in err_str or "504" in err_str:
                        self.cooldowns["gemini"] = time.time() + 300
                        print(f"[LLMClient] Gemini unavailable (503/504); cooling down for 5 minutes.")
                    else:
                        print(f"[LLMClient] Gemini generate_text error: {e}")
            return ""

        # Helper for Groq
        def _call_groq():
            if time.time() < self.cooldowns.get("groq", 0):
                return ""
            if self.groq_key:
                try:
                    from groq import Groq
                    client = Groq(api_key=self.groq_key, max_retries=0)
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    chat = client.chat.completions.create(
                        messages=messages,
                        model="openai/gpt-oss-20b",
                        temperature=0.1,
                        max_tokens=800,
                        timeout=5.0
                    )
                    if chat and chat.choices:
                        return chat.choices[0].message.content or ""
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "rate_limit" in err_str.lower() or "tokens" in err_str or "timed out" in err_str.lower():
                        self.cooldowns["groq"] = time.time() + 300
                        print(f"[LLMClient] Groq rate limit / timeout; cooling down for 5 minutes.")
                    else:
                        print(f"[LLMClient] Groq generate_text error: {e}")
            return ""

        # Routing order based on primary provider
        order = []
        if self.provider == "gemini":
            order = [_call_gemini, _call_groq]
        elif self.provider == "groq":
            order = [_call_groq, _call_gemini]
        else:
            order = [_call_groq, _call_gemini]

        for caller in order:
            res = caller()
            if res and res.strip():
                return res

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
