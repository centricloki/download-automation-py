# Playwright Download Automation Framework

A scalable, production-ready Python automation framework for downloading files from multiple websites using Playwright's async API.

## 🌟 Features

- **Async/Await Support**: Leverages Playwright's async API for efficient parallel downloads
- **Parallel Execution**: Run multiple site downloads concurrently using asyncio
- **Error Retry Logic**: Automatic retry with exponential backoff on failures
- **Comprehensive Logging**: Dual logging to both file (`logs/downloader.log`) and console
- **Email Notifications**: Automatic email alerts on success/failure with optional file attachments
- **Flexible Configuration**: Easy-to-extend configuration for adding new download sites
- **CLI Interface**: Simple command-line interface for running single or multiple sites
- **Scalable Architecture**: Modular design makes it easy to add custom download workflows

## 📁 Project Structure

```
download-automation-py/
├── main.py                 # Entry point with CLI argument parsing
├── config.py               # Site configurations and email settings
├── downloader.py           # Core Playwright automation class
├── utils.py                # Helper functions (retry logic, file handling)
├── email_notifier.py       # Async email notification module
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── logs/                  # Log files directory (auto-created)
│   └── downloader.log
└── downloads/             # Downloaded files directory (auto-created)
    └── delaware/          # Site-specific download folders
```

## 🚀 Quick Start

### 1. Installation

Install Playwright and dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Email Settings (Optional)

Edit `config.py` with your email SMTP settings:

```python
EMAIL_CONFIG = {
    "sender": "your_email@gmail.com",
    "receiver": "your_email@gmail.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "password": "your_app_password",  # Use Gmail App Password
}
```

**For Gmail users:**
- Generate an App Password at: https://myaccount.google.com/apppasswords
- Do NOT use your regular Gmail password

### 3. Add Download Sites

Edit `config.py` to add your download sites:

```python
SITES = {
    "delaware_business_licenses": {
        "url": "https://data.delaware.gov/...",
        "download_dir": "downloads/delaware",
        "format": "XLSX",
        "fallback_format": "CSV for Excel",
    },
    # Add more sites here...
}
```

### 4. Run Downloads

#### Run all configured sites (parallel):
```bash
python main.py
```

#### Run a specific site:
```bash
python main.py --site delaware_business_licenses
```

#### Run multiple specific sites:
```bash
python main.py --site delaware_business_licenses another_site
```

#### Run sites from a text file:
```bash
python main.py --file sites.txt
```

Example `sites.txt`:
```text
# One site key per line
# Lines starting with # are comments
delaware_business_licenses
another_site
```

## 📖 Usage Examples

### Example 1: Delaware Business Licenses Download

The included configuration automates the Delaware Open Data portal:

1. Opens: https://data.delaware.gov/Licenses-and-Certifications/Delaware-Business-Licenses/5zy2-grhr/data_preview
2. Clicks: Export button
3. Selects: XLSX format
4. Checks: All Data option
5. Clicks: Download button
6. Saves: File to `downloads/delaware/` folder

### Example 2: Adding a New Site

To add a new download site, edit `config.py`:

```python
SITES = {
    "my_new_site": {
        "url": "https://example.com/data",
        "download_dir": "downloads/example",
        "format": "CSV",
        "fallback_format": "Excel",
    }
}
```

Then customize the download logic in `downloader.py` if the UI interactions differ.

## 🔧 Configuration Reference

### Site Configuration Options

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `url` | str | Yes | Target webpage URL |
| `download_dir` | str | Yes | Local directory to save downloaded files |
| `format` | str | Yes | Primary export format (e.g., "XLSX", "CSV") |
| `fallback_format` | str | No | Alternative format if primary fails |

### Email Configuration Options

| Key | Type | Description |
|-----|------|-------------|
| `sender` | str | Sender's email address |
| `receiver` | str | Recipient's email address |
| `smtp_server` | str | SMTP server hostname |
| `smtp_port` | int | SMTP port (587 for TLS) |
| `password` | str | SMTP authentication password |

## 🛠️ Advanced Customization

### Custom Download Logic

For sites with different UI patterns, modify the `download_site()` method in `downloader.py`:

```python
# Example: Different button names or selectors
await page.get_by_role("button", name="Your Button").click()
await page.get_by_text("Your Option").check()
```

### Retry Logic Configuration

Adjust retry behavior in `utils.py`:

```python
await retry_with_backoff(
    download_function,
    max_retries=5,           # Number of attempts
    base_delay=2.0,          # Initial delay
    max_delay=120.0,         # Maximum delay cap
    backoff_factor=2.0       # Exponential multiplier
)
```

### Logging Configuration

Modify logging settings in `downloader.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,     # Change log level
    format='...',            # Customize log format
    handlers=[...]           # Add/remove log handlers
)
```

## 📊 Logging and Monitoring

### Log Files

All activities are logged to:
- **File**: `logs/downloader.log` (persistent log)
- **Console**: Real-time output during execution

### Log Format

```
2024-01-15 10:30:45,123 - INFO - [downloader] - Starting download for site: delaware_business_licenses
2024-01-15 10:30:46,456 - INFO - [downloader] - Navigating to: https://...
```

### Email Notifications

Automatic emails are sent on:
- **Success**: Includes file path and attachment
- **Failure**: Includes error details for troubleshooting

## 🐛 Troubleshooting

### Common Issues

**Issue: Browser doesn't open**
```bash
# Reinstall Playwright browsers
playwright install chromium
```

**Issue: Download timeout**
- Increase timeout in `downloader.py`: `timeout=180000` → higher value
- Check internet connection
- Verify website is accessible

**Issue: Email not sending**
- Verify SMTP credentials in `config.py`
- For Gmail: Use App Password, not regular password
- Check firewall allows outbound SMTP (port 587)

**Issue: Element not found errors**
- Website UI may have changed
- Update selectors in `downloader.py`
- Use browser devtools to inspect elements

### Debug Mode

Run with visible browser for debugging:

```python
# In downloader.py, change headless parameter
await self.launch(headless=False)  # Shows browser window
```

## 📝 Best Practices

1. **Version Control**: Add `downloads/` and `logs/` to `.gitignore`
2. **Email Security**: Use environment variables for sensitive credentials
3. **Testing**: Test with one site before running all sites
4. **Monitoring**: Check `logs/downloader.log` regularly
5. **Maintenance**: Update site configs when websites change

## 🔒 Security Considerations

- **Never commit passwords** to version control
- Use environment variables or `.env` files for credentials
- Consider using a secrets manager for production
- Restrict file permissions on log files (may contain sensitive data)

## 🤝 Contributing

To add new features or improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for automation purposes. Modify and distribute as needed.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `logs/downloader.log`
3. Verify configuration in `config.py`

## 🎯 Future Enhancements

Potential improvements:
- [ ] Database integration for download history
- [ ] Web dashboard for monitoring
- [ ] Scheduled downloads with cron/Task Scheduler
- [ ] Proxy support for geo-restricted sites
- [ ] CAPTCHA solving integration
- [ ] REST API endpoint for remote triggering
- [ ] Docker containerization

---

**Built with ❤️ using Playwright and Python Async IO**
