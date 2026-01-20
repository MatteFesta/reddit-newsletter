"""
Configuration loader for the Reddit Newsletter.
Loads settings from config/settings.yaml and provides defaults.
"""

import os
import yaml
from pathlib import Path

# Find the project root (where main.py lives)
PROJECT_ROOT = Path(__file__).parent.parent

def load_config():
    """
    Load configuration from settings.yaml.
    Returns a dictionary with all settings, using defaults if file is missing.
    """
    config_path = PROJECT_ROOT / "config" / "settings.yaml"
    
    # Default configuration (used if file doesn't exist or is incomplete)
    defaults = {
        "subreddits": ["LocalLLaMA", "AI_Agents", "PromptEngineering", "MachineLearning", "technews"],
        "fetch": {
            "posts_per_subreddit": 5,
            "time_period": "week",
            "delay_between_requests": 1.0,
            "max_retries": 3
        },
        "newsletter": {
            "stories_to_include": "5-7",
            "output_directory": "output/newsletters",
            "output_filename": "weekly_digest.md"
        },
        "email": {
            "subject": "🚀 The Weekly Sync",
            "send_on_completion": True
        }
    }
    
    if not config_path.exists():
        print(f"⚠️  Config file not found at {config_path}, using defaults.")
        return defaults
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
        
        # Merge user config with defaults (user settings override defaults)
        config = _deep_merge(defaults, user_config or {})
        return config
        
    except Exception as e:
        print(f"⚠️  Error loading config: {e}. Using defaults.")
        return defaults


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries. Values in 'override' take precedence.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_subreddits():
    """Convenience function to get just the subreddit list."""
    return load_config().get("subreddits", [])


def get_fetch_settings():
    """Convenience function to get fetch-related settings."""
    return load_config().get("fetch", {})


def get_email_settings():
    """Convenience function to get email-related settings."""
    return load_config().get("email", {})
