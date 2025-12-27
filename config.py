"""Configuration management with environment variable validation."""
import os
from typing import Optional
from pathlib import Path


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Config:
    """Application configuration with validation."""

    # API Keys (required)
    GEMINI_API_KEY: str
    TAVILY_API_KEY: str

    # Model Configuration
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    THINKING_LEVEL: str = "medium"

    # Safety Limits
    MAX_TOOL_ITERATIONS: int = 20

    # Output Configuration
    REPORTS_DIR: Path = Path("reports")

    def __init__(self):
        """Initialize and validate configuration."""
        self._load_env_file()
        self._validate()

    def _load_env_file(self):
        """Load .env file if exists, or Streamlit secrets."""
        # Try Streamlit secrets first (for cloud deployment)
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                # Running in Streamlit, use secrets
                return
        except ImportError:
            pass

        # Try python-dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # python-dotenv not installed, will use environment variables directly
            pass

    def _validate(self):
        """Validate all required configuration."""
        # Try Streamlit secrets first
        gemini_key = None
        tavily_key = None

        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                gemini_key = st.secrets.get('GEMINI_API_KEY', '').strip()
                tavily_key = st.secrets.get('TAVILY_API_KEY', '').strip()
        except (ImportError, FileNotFoundError, AttributeError):
            pass

        # Fall back to environment variables
        if not gemini_key:
            gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
        if not tavily_key:
            tavily_key = os.environ.get('TAVILY_API_KEY', '').strip()

        # Validate GEMINI_API_KEY
        if not gemini_key or gemini_key == 'default_value':
            raise ConfigurationError(
                "GEMINI_API_KEY is required. Set it in .env file, environment variables, or Streamlit secrets."
            )

        # Validate TAVILY_API_KEY
        if not tavily_key or tavily_key == 'default_value':
            raise ConfigurationError(
                "TAVILY_API_KEY is required. Set it in .env file, environment variables, or Streamlit secrets."
            )

        self.GEMINI_API_KEY = gemini_key
        self.TAVILY_API_KEY = tavily_key

        # Load optional configurations from environment
        self.GEMINI_MODEL = os.environ.get('GEMINI_MODEL', self.GEMINI_MODEL)
        self.THINKING_LEVEL = os.environ.get('THINKING_LEVEL', self.THINKING_LEVEL)
        self.MAX_TOOL_ITERATIONS = int(os.environ.get('MAX_TOOL_ITERATIONS', str(self.MAX_TOOL_ITERATIONS)))

        # Create reports directory if it doesn't exist
        self.REPORTS_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_instance(cls) -> 'Config':
        """Get singleton config instance."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance


# Singleton access function
def get_config() -> Config:
    """Get validated configuration instance."""
    return Config.get_instance()
