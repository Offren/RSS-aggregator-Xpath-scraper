import random
import logging
from typing import Dict, Optional
from config import USER_AGENTS

def get_headers() -> Dict[str, str]:
    """Generate headers with a random user agent."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def setup_logging() -> None:
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )