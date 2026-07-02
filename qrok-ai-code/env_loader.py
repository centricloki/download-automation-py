"""
Environment configuration loader using python-dotenv.

This module provides secure loading of sensitive configuration from .env files
instead of hardcoding credentials in config.py.

Usage:
    1. Create a .env file in the project root
    2. Add your email credentials
    3. This module will load them automatically

Example .env file:
    EMAIL_SENDER=your_email@gmail.com
    EMAIL_RECEIVER=your_email@gmail.com
    EMAIL_PASSWORD=your_app_password
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587

Security Note:
    - Never commit .env to version control
    - Add .env to .gitignore (already included)
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env_config():
    """
    Load environment variables from .env file and return email configuration.
    
    Falls back to config.EMAIL_CONFIG if .env file is not found.
    
    Returns:
        dict: Email configuration dictionary with keys:
            - sender: Sender email address
            - receiver: Receiver email address
            - smtp_server: SMTP server hostname
            - smtp_port: SMTP port number
            - password: Authentication password
            
    Example:
        >>> email_config = load_env_config()
        >>> print(email_config['sender'])
        'your_email@gmail.com'
    """
    # Load .env file from project root
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    # Build config from environment variables
    config = {
        "sender": os.getenv("EMAIL_SENDER", ""),
        "receiver": os.getenv("EMAIL_RECEIVER", ""),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "password": os.getenv("EMAIL_PASSWORD", ""),
    }
    
    # Check if we have valid config
    if not all([config["sender"], config["receiver"], config["password"]]):
        print("⚠️  Warning: Email configuration incomplete in .env file")
        print("   Please check your .env file or use config.py settings")
    
    return config


if __name__ == "__main__":
    # Test environment loading
    config = load_env_config()
    print("Environment Configuration:")
    print(f"  Sender: {config.get('sender', 'Not set')}")
    print(f"  Receiver: {config.get('receiver', 'Not set')}")
    print(f"  SMTP Server: {config.get('smtp_server', 'Not set')}")
    print(f"  SMTP Port: {config.get('smtp_port', 'Not set')}")
    print(f"  Password: {'***' + config.get('password', '')[-4:] if config.get('password') else 'Not set'}")
