# Playwright Download Automation Framework - Project Summary

## 🎯 What This Project Does

Automates file downloads from multiple websites through browser UI interactions, with:
- Parallel execution for efficiency
- Automatic retry on failures
- Email notifications on success/failure
- Comprehensive logging for monitoring
- Easy configuration for adding new sites

## 🏗️ Architecture Overview

### Core Components

**main.py** - Entry Point & CLI
- Parses command-line arguments
- Determines which sites to run
- Orchestrates parallel execution
- Displays results summary

**config.py** - Configuration Hub
- SITES dictionary: All download site configurations
- EMAIL_CONFIG: SMTP settings for notifications
- Easy to extend with new sites

**downloader.py** - Automation Engine
- AsyncPlaywrightDownloader class
- Browser management (launch/close)
- Site-specific download logic
- Error handling with retry logic
- Logging integration

**utils.py** - Helper Functions
- ensure_dir(): Create directories as needed
- wait_for_file(): Poll for download completion
- retry_with_backoff(): Exponential backoff retry mechanism

**email_notifier.py** - Notification System
- send_email_notification(): Async email with attachments
- Success/failure alerts
- Configurable SMTP settings

### Data Flow

```
User runs main.py
    ↓
Parse CLI arguments (--site, --file, or all)
    ↓
Load site configurations from config.py
    ↓
Create tasks for each site
    ↓
Execute in parallel with asyncio.gather()
    ↓
For each site:
    ├─ Launch browser
    ├─ Navigate to URL
    ├─ Perform UI interactions
    ├─ Trigger download
    ├─ Wait for completion
    ├─ Save file locally
    ├─ Send email notification
    └─ Close browser
    ↓
Display results summary
```

## 🔧 How to Use

### Basic Usage

```bash
# Run all configured sites
python main.py

# Run specific site(s)
python main.py --site delaware_business_licenses
python main.py --site site1 site2

# Run from text file
python main.py --file sites.txt
```

### Adding a New Download Site

1. Edit `config.py`:
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

2. If the site has different UI, customize `downloader.py`

3. Test:
```bash
python main.py --site my_new_site
```

### Customizing Download Logic

For sites with different workflows, modify the `download_site()` method in `downloader.py`:

```python
# Example selectors for different UI patterns
await page.get_by_role("button", name="Export").click()
await page.get_by_text("Download").click()
await page.locator(".download-button").click()
```

## ✨ Key Features Explained

### 1. Parallel Execution

All sites run concurrently using `asyncio.gather()`:
- Faster than sequential downloads
- Each site has independent browser instance
- Failures don't block other downloads

### 2. Retry with Exponential Backoff

Automatic retry on errors with increasing delays:
```
Attempt 1: Immediate
Attempt 2: After 1s
Attempt 3: After 2s
Attempt 4: After 4s
...
```

Configured in `utils.py`:
- `max_retries`: Maximum attempts
- `base_delay`: Starting delay
- `backoff_factor`: Multiplier (2.0 = exponential)

### 3. Dual Logging

Logs go to two places:
- **File**: `logs/downloader.log` (persistent)
- **Console**: Real-time output

Log levels:
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures requiring attention

### 4. Email Notifications

Automatic emails sent on:
- **Success**: File path + attachment
- **Failure**: Error details for debugging

Configure in `config.py` or use `.env` file.

### 5. Flexible Configuration

Three ways to specify sites:
1. Command line: `--site site1 site2`
2. Text file: `--file sites.txt`
3. All sites: Just run `python main.py`

## 📊 Monitoring & Debugging

### Check Logs

```bash
# View log file
cat logs/downloader.log          # Linux/Mac
type logs\downloader.log         # Windows

# Follow in real-time
tail -f logs/downloader.log      # Linux/Mac
```

### Log Output Example

```
2024-01-15 10:30:45,123 - INFO - [downloader] - Starting download for site: delaware_business_licenses
2024-01-15 10:30:46,456 - INFO - [downloader] - Launching browser (headless=False)...
2024-01-15 10:30:48,789 - INFO - [downloader] - Navigating to: https://data.delaware.gov/...
2024-01-15 10:30:52,012 - INFO - [downloader] - Page loaded successfully
2024-01-15 10:30:53,345 - INFO - [downloader] - Clicking Export button...
2024-01-15 10:30:55,678 - INFO - [downloader] - Selecting format: XLSX
2024-01-15 10:30:57,901 - INFO - [downloader] - Initiating download...
2024-01-15 10:31:02,234 - INFO - [downloader] - Download started: business_licenses.xlsx
2024-01-15 10:31:05,567 - INFO - [downloader] - ✅ Successfully downloaded: downloads/delaware/business_licenses.xlsx
2024-01-15 10:31:06,890 - INFO - [email_notifier] - 📧 Email notification sent to user@gmail.com
```

### Debug Mode

To see browser actions visually:

```python
# In downloader.py, launch() method
await self.launch(headless=False)  # Shows browser window
```

This helps identify:
- UI element selector issues
- Timing problems
- Website changes

## 🔒 Security Best Practices

### Credential Management

**Option 1: .env file (Recommended)**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your credentials
# .env is already in .gitignore
```

**Option 2: Environment variables**
```bash
export EMAIL_PASSWORD=your_password
python main.py
```

**Option 3: Config file (Less secure)**
Edit `config.py` directly (not recommended for production)

### File Permissions

Restrict access to sensitive files:
```bash
chmod 600 .env              # Linux/Mac
icacls .env /grant:r %USERNAME%:R  # Windows
```

## 🚀 Production Deployment

### Scheduled Runs

**Linux (cron):**
```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/project && python main.py >> logs/cron.log 2>&1
```

**Windows (Task Scheduler):**
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "main.py" -WorkingDirectory "C:\path\to\project"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "Download Automation" -Action $action -Trigger $trigger
```

### Docker Support (Future Enhancement)

Create Dockerfile for containerized deployment:
```dockerfile
FROM mcr.microsoft.com/playwright:v1.45.0
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## 📈 Performance Tuning

### Adjust Concurrency

Limit parallel downloads if needed:

```python
# In downloader.py, run_parallel()
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent downloads

async def limited_download(key, cfg, email_cfg):
    async with semaphore:
        return await downloader.download_site(key, cfg, email_cfg)
```

### Timeout Configuration

Adjust timeouts based on file sizes:

```python
# Small files: Reduce timeout
download_promise = page.expect_download(timeout=60000)  # 1 min

# Large files: Increase timeout
download_promise = page.expect_download(timeout=300000)  # 5 min
```

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Browser doesn't open | Run `playwright install chromium` |
| Element not found | Update selectors in downloader.py |
| Download timeout | Increase timeout value in downloader.py |
| Email fails | Verify SMTP credentials, use App Password |
| Permission denied | Check file permissions on downloads/ |
| Memory issues | Limit concurrent downloads with Semaphore |

## 📚 Learning Resources

- **Playwright Docs**: https://playwright.dev/python/docs/intro
- **Async IO**: https://docs.python.org/3/library/asyncio.html
- **SMTP Library**: https://aiosmtplib.readthedocs.io/

## 🎓 Code Walkthrough

### For Beginners

Start by reading these files in order:
1. `config.py` - Understand site configuration
2. `main.py` - See how execution flows
3. `utils.py` - Learn helper functions
4. `downloader.py` - Core automation logic
5. `email_notifier.py` - Notification system

### For Advanced Users

Focus on:
- `downloader.py` - Customize download logic
- `utils.py` - Modify retry behavior
- `run_parallel()` - Adjust concurrency

## 🔄 Maintenance Checklist

Weekly:
- [ ] Check logs/downloader.log for errors
- [ ] Verify downloads are completing
- [ ] Monitor disk space in downloads/

Monthly:
- [ ] Archive old downloads
- [ ] Review and update site configs
- [ ] Check for Playwright updates

Quarterly:
- [ ] Rotate email passwords
- [ ] Review and optimize performance
- [ ] Update dependencies

---

**Need Help?**
- Check README.md for detailed documentation
- See QUICKSTART.md for getting started
- Review logs/downloader.log for debugging
- Inspect elements on target website if selectors fail
