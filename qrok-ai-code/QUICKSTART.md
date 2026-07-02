# Quick Start Guide

## First Time Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure Email (Optional but Recommended)

Edit `config.py` with your email settings:

```python
EMAIL_CONFIG = {
    "sender": "your_email@gmail.com",
    "receiver": "your_email@gmail.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "password": "your_app_password",  # IMPORTANT: Use Gmail App Password
}
```

**How to get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Copy the 16-character password
4. Paste it in config.py

### Step 3: Test with One Site

```bash
python main.py --site delaware_business_licenses
```

You should see:
- Browser window opens
- Navigation to Delaware data portal
- Export dialog appears
- File downloads
- Email notification sent
- Console shows success message

### Step 4: Run All Sites

```bash
python main.py
```

## Common Commands

```bash
# Run all configured sites
python main.py

# Run specific site(s)
python main.py --site delaware_business_licenses
python main.py --site site1 site2 site3

# Run sites from file
python main.py --file sites.txt

# Check logs
cat logs/downloader.log      # Linux/Mac
type logs\downloader.log     # Windows
```

## Adding New Sites

1. Open `config.py`
2. Add new entry to SITES dictionary:

```python
SITES = {
    "my_new_site": {
        "url": "https://example.com/data",
        "download_dir": "downloads/example",
        "format": "CSV",
        "fallback_format": "Excel",
    },
    # ... existing sites ...
}
```

3. Customize download logic in `downloader.py` if needed
4. Test: `python main.py --site my_new_site`

## Troubleshooting Quick Fixes

**Browser won't open:**
```bash
playwright install chromium
```

**Email not sending:**
- Check SMTP credentials in config.py
- Use App Password for Gmail (not regular password)
- Verify firewall allows port 587

**Download fails:**
- Check website is accessible
- Increase timeout values in downloader.py
- Review logs/downloader.log for details

**Element not found:**
- Website UI may have changed
- Update selectors in downloader.py
- Run with headless=False to debug visually

## Project Structure Overview

```
your-project/
├── main.py              ← Run this file
├── config.py            ← Configure sites & email here
├── downloader.py        ← Core automation logic
├── utils.py             ← Helper functions
├── email_notifier.py    ← Email notifications
├── requirements.txt     ← Python packages
├── README.md           ← Full documentation
├── QUICKSTART.md       ← This file
├── logs/               ← Auto-created log files
└── downloads/          ← Auto-created download folder
```

## Next Steps

1. ✅ Test with included Delaware site
2. ✅ Configure email notifications
3. ✅ Add your own download sites
4. ✅ Set up scheduled runs (Task Scheduler/cron)
5. ✅ Monitor logs for success/failure

---

For detailed documentation, see README.md
