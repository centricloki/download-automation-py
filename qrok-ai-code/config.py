"""
Configuration file for download automation sites and email settings.

This module contains:
- SITES: Dictionary of all configured download sites with their specific settings
- EMAIL_CONFIG: SMTP configuration for sending email notifications

To add a new site, add an entry to the SITES dictionary with:
- url: The webpage URL to navigate to
- download_dir: Local directory to save downloaded files
- format: Primary export format (e.g., "XLSX", "CSV")
- fallback_format: Alternative format if primary fails
- Additional custom settings as needed
"""

# Site configurations - expandable dictionary
SITES = {
    "delaware_business_licenses": {
        # Delaware State Data Portal - Business Licenses dataset
        "url": "https://data.delaware.gov/Licenses-and-Certifications/Delaware-Business-Licenses/5zy2-grhr/data_preview",
        "download_dir": "downloads/delaware",
        "format": "XLSX",  # Excel format
        "fallback_format": "CSV for Excel",  # Fallback if XLSX unavailable
    },
    
    # Example: Add more sites here following the same pattern
    # "another_site": {
    #     "url": "https://example.com/data",
    #     "download_dir": "downloads/example",
    #     "format": "CSV",
    #     "fallback_format": "Excel",
    # },
}

# Email notification configuration
# For Gmail: Use App Password (not regular password)
# Generate at: https://myaccount.google.com/apppasswords
EMAIL_CONFIG = {
    "sender": "your_email@gmail.com",      # Sender email address
    "receiver": "your_email@gmail.com",     # Receiver email address
    "smtp_server": "smtp.gmail.com",        # SMTP server hostname
    "smtp_port": 587,                       # SMTP port (587 for TLS)
    "password": "your_app_password",        # App-specific password
}
