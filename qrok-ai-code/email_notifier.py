"""
Email notification module for download automation.

This module provides async email notification functionality using SMTP.
Supports:
- Plain text email messages
- File attachments (for sending downloaded files)
- TLS encryption for secure transmission

Configuration is loaded from config.EMAIL_CONFIG dictionary.
"""

import asyncio
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import aiosmtplib


async def send_email_notification(
    subject: str, 
    body: str, 
    attachment_path: str = None, 
    config: dict = None
) -> bool:
    """
    Send an email notification with optional file attachment.
    
    Constructs and sends an email using the provided SMTP configuration.
    Supports attaching downloaded files to the notification email.
    
    Args:
        subject: Email subject line
        body: Email body text (plain text)
        attachment_path: Optional path to file to attach
        config: SMTP configuration dictionary with keys:
            - sender: Sender's email address
            - receiver: Recipient's email address
            - smtp_server: SMTP server hostname (e.g., "smtp.gmail.com")
            - smtp_port: SMTP port number (e.g., 587 for TLS)
            - password: SMTP authentication password/app password
            
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Example:
        >>> await send_email_notification(
        ...     subject="Download Complete",
        ...     body="File downloaded successfully",
        ...     attachment_path="downloads/delaware/data.xlsx",
        ...     config=email_config
        ... )
    """
    # Skip if no configuration provided
    if not config:
        logging.warning("No email configuration provided. Skipping notification.")
        return False
    
    try:
        # Create multipart email message
        msg = MIMEMultipart()
        msg['From'] = config["sender"]
        msg['To'] = config["receiver"]
        msg['Subject'] = subject
        
        # Attach the plain text body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach file if provided
        if attachment_path:
            file_path = Path(attachment_path)
            
            if file_path.exists():
                # Read file and create MIME attachment
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=file_path.name)
                
                # Set attachment header with filename
                part['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
                msg.attach(part)
                
                logging.info(f"Attached file: {file_path.name}")
            else:
                logging.warning(f"Attachment not found: {attachment_path}")
        
        # Send email via SMTP using async library
        await aiosmtplib.send(
            msg,
            hostname=config["smtp_server"],
            port=config["smtp_port"],
            username=config["sender"],
            password=config["password"],
            start_tls=True  # Enable TLS encryption
        )
        
        logging.info(f"📧 Email notification sent to {config['receiver']}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}", exc_info=True)
        return False
