# src/llm_config.py
"""多LLM提供商配置"""

import os
from typing import Dict, Any


class LLMConfig:
    """LLM 配置管理"""
    
    PROVIDERS = {
        "ollama": {
            "name": "Ollama",
            "default_model": "qwen2.5:0.5b",
            "url": "http://localhost:11434",
            "local": True
        },
        "openai": {
            "name": "OpenAI",
            "default_model": "gpt-3.5-turbo",
            "url": "https://api.openai.com/v1",
            "local": False
        }
    }
    
    def __init__(self):
        self.current_provider = os.getenv("LLM_PROVIDER", "ollama")
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY", "")
        }
    
    def get_current_provider(self) -> str:
        return self.current_provider
    
    def get_model(self) -> str:
        config = self.PROVIDERS.get(self.current_provider, self.PROVIDERS["ollama"])
        return config.get("default_model", "")
    
    def is_api_available(self, provider: str = None) -> bool:
        provider = provider or self.current_provider
        config = self.PROVIDERS.get(provider, {})
        
        if config.get("local", True):
            try:
                import requests
                resp = requests.get(config["url"], timeout=3)
                return resp.status_code == 200
            except:
                return False
        else:
            return bool(self.api_keys.get(provider, ""))


llm_config = LLMConfig()
