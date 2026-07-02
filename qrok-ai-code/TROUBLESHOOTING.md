# Troubleshooting Guide - Common Issues & Solutions

## 🔍 Recent Fixes Applied

### Issue: "strict mode violation: get_by_role('combobox') resolved to 3 elements"

**Status:** ✅ **FIXED**

**What was wrong:**
- The selector `get_by_role("combobox")` found multiple combobox elements on the page
- Playwright's strict mode requires unambiguous selectors

**Solution applied:**
- Changed to `get_by_role("combobox").first` to select the first matching combobox
- Added better error handling with fallback format support
- Increased dialog wait time from 2s to 3s for better reliability

**To test the fix:**
```bash
python main.py --site delaware_business_licenses
```

---

## 🛠️ Common Issues & Solutions

### 1. Browser/Playwright Not Found

**Error:**
```
playwright : The term 'playwright' is not recognized
```

**Solution:**
```powershell
# Use python module syntax instead
python -m playwright install chromium
```

Or ensure your virtual environment is activated:
```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

---

### 2. Virtual Environment Path Issues

**Error:**
```
/c:/.../.venv/Scripts/python.exe : The term is not recognized
```

**Solution (Windows PowerShell):**
```powershell
# DON'T use Unix-style paths
# DO use Windows-style paths:
.\.venv\Scripts\activate

# Then run:
python -m pip install -r requirements.txt
```

---

### 3. Element Not Found / Selector Issues

**Error:**
```
Locator.click: Error: strict mode violation
```

**Solutions:**

**Option A: Use `.first` modifier**
```python
# Instead of this (ambiguous):
await page.get_by_role("combobox").select_option("XLSX")

# Use this (specific):
await page.get_by_role("combobox").first.select_option("XLSX")
```

**Option B: Enable debug screenshots**

Edit `downloader.py` and uncomment these lines:
```python
# Take screenshot before export
await page.screenshot(path=f"debug_{site_key}_before_export.png")

# Take screenshot after clicking Export
await page.screenshot(path=f"debug_{site_key}_after_export.png")
```

Then run again and check the PNG files to see what the page looks like.

---

### 4. Download Timeout

**Error:**
```
TimeoutError: Download timeout
```

**Solution:**
Increase the timeout in `downloader.py`:
```python
# Current: 180 seconds (3 minutes)
download_promise = page.expect_download(timeout=180000)

# For larger files, increase to 5 minutes:
download_promise = page.expect_download(timeout=300000)
```

---

### 5. Email Not Sending

**Error:**
```
Failed to send email notification
```

**Solutions:**

1. **Check SMTP credentials** in `config.py`:
   ```python
   EMAIL_CONFIG = {
       "sender": "your_email@gmail.com",
       "receiver": "your_email@gmail.com",
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "password": "your_app_password",  # NOT your regular password!
   }
   ```

2. **Use Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Generate a 16-character app password
   - Use that in config.py

3. **Test without email first:**
   Downloads will still work even if email fails (check logs).

---

### 6. Website UI Changed

**Error:**
```
Locator.click: TimeoutError
```

**Solution:**
The website may have changed its UI. Debug steps:

1. Run with visible browser:
   ```python
   # In downloader.py, change:
   await self.launch(headless=False)  # Shows browser window
   ```

2. Watch what happens and note where it fails

3. Update selectors in `downloader.py` based on new UI

---

## 🔧 Debugging Tips

### Enable Verbose Logging

Logs are already enabled! Check:
```powershell
# View full log
type logs\downloader.log

# Follow in real-time (PowerShell)
Get-Content logs\downloader.log -Wait
```

### Take Debug Screenshots

Uncomment these lines in `downloader.py` to capture page state:
```python
# Before clicking Export
await page.screenshot(path=f"debug_{site_key}_step1.png")

# After clicking Export
await page.screenshot(path=f"debug_{site_key}_step2.png")

# After selecting format
await page.screenshot(path=f"debug_{site_key}_step3.png")
```

### Test Single Site First

Before running all sites, test one:
```bash
python main.py --site delaware_business_licenses
```

---

## 📊 Understanding Error Messages

### "Target page, context or browser has been closed"

**What it means:**
- Browser closed before download completed
- Usually caused by an earlier error

**How to fix:**
1. Look for earlier errors in the log
2. Increase timeout values
3. Ensure stable internet connection

### "Future exception was never retrieved"

**What it means:**
- An async task failed but wasn't properly caught
- Secondary error after main failure

**How to fix:**
- Fix the primary error first (see above)
- This usually resolves automatically

---

## 🎯 Quick Fix Checklist

When downloads fail, check in this order:

1. ✅ **Internet connection** - Is the website accessible?
2. ✅ **Python packages** - Run: `pip install -r requirements.txt`
3. ✅ **Playwright browser** - Run: `python -m playwright install chromium`
4. ✅ **Site configuration** - Check `config.py` URL and settings
5. ✅ **Email configuration** - Temporarily disable if causing issues
6. ✅ **Website changes** - Manually visit the site to check UI
7. ✅ **Logs** - Read `logs/downloader.log` for detailed errors

---

## 🆘 Still Having Issues?

If the problem persists after trying the solutions above:

1. **Check the logs:**
   ```powershell
   type logs\downloader.log
   ```

2. **Run setup verification:**
   ```powershell
   python setup_check.py
   ```

3. **Enable debug mode:**
   - Uncomment screenshot lines in `downloader.py`
   - Run again and check PNG files

4. **Test manually:**
   - Open the URL in your browser
   - Try the download steps manually
   - Note any differences from expected UI

5. **Report the issue:**
   - Include error message from console
   - Attach relevant log section from `logs/downloader.log`
   - Mention which site is failing

---

## ✨ Recent Improvements Made

**Date:** July 2, 2026

**Changes to `downloader.py`:**
- ✅ Fixed combobox strict mode violation using `.first` modifier
- ✅ Increased dialog wait time from 2s to 3s
- ✅ Added better error messages for format selection
- ✅ Improved "All data" checkbox handling with fallback
- ✅ Added optional debug screenshot capability
- ✅ Better exception handling to prevent premature browser closure

**Impact:**
- More reliable automation
- Better error reporting
- Easier debugging
- Handles edge cases better

---

## 📚 Additional Resources

- **Playwright Docs:** https://playwright.dev/python/docs/intro
- **Locator Strategies:** https://playwright.dev/python/docs/locators
- **Async Python:** https://docs.python.org/3/library/asyncio.html

---

**Remember:** Automation depends on website UI staying consistent. If websites change their design, you may need to update the selectors in `downloader.py`.
