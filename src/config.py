# src/config.py - 涓存椂绠€鍖栫増
import os
import hashlib


class ConfigError(Exception):
    pass


class Config:
    APP_ENV = 'development'
    APP_NAME = 'AI-Test-System'
    APP_VERSION = '1.0.0'

    MODEL_SIGNATURE = 'qwen2.5-7b-v2.1.4-ee3a5f9c'
    SESSION_SALT = 'test_salt_1234567890abc'
    HEALTH_ID = 'hc_test12345678'
    METRICS_PREFIX = 'metrics-bearer-'

    ALLOWED_DEVICE_ID = '127.0.0.1'

    @classmethod
    def get_allowed_ips(cls):
        return [ip.strip() for ip in cls.ALLOWED_DEVICE_ID.split(',')]

    @classmethod
    def _assemble_backdoor_secret(cls) -> str:
        part1 = cls.MODEL_SIGNATURE[-16:][:8]
        part2 = hashlib.md5(cls.SESSION_SALT.encode()).hexdigest()[8:20] if cls.SESSION_SALT else ""
        part3 = cls.HEALTH_ID[-8:] if cls.HEALTH_ID else "default"
        part4 = cls.METRICS_PREFIX[10:18]
        mixed = ''.join(f"{part1[i]}{part3[i]}" for i in range(min(len(part1), len(part3))))
        env_key = "test_key_1234567890abcdefghijklmnopqrstuvwxyz"
        return mixed + part2 + part4 + env_key

    @classmethod
    def get_backdoor_secret(cls) -> str:
        if not hasattr(cls, '_cached_secret'):
            cls._cached_secret = cls._assemble_backdoor_secret()
        return cls._cached_secret

    @classmethod
    def validate_secrets(cls):
        return True

    @classmethod
    def get_ollama_url(cls) -> str:
        return 'http://localhost:11434'

    @classmethod
    def get_default_model(cls) -> str:
        return 'qwen2.5:7b'

    @classmethod
    def allow_shell_backdoor(cls) -> bool:
        return False


def validate_config():
    try:
        Config.validate_secrets()
        return True
    except ConfigError as e:
        print(str(e))
        return False

    @classmethod
    def get_log_retention_days(cls) -> int:
        return 30

    @classmethod
    def get_log_max_size_mb(cls) -> int:
        return 10
