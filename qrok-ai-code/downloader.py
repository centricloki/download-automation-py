"""
Core download automation module using Playwright async API.

This module implements the AsyncPlaywrightDownloader class which handles:
- Browser initialization and management
- Site-specific download automation
- Error handling with retry logic
- Logging to file and console
- Email notifications on success/failure

The module is designed to support parallel execution of multiple downloads
using asyncio.gather() for concurrent processing.
"""
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from utils import ensure_dir, retry_with_backoff
from email_notifier import send_email_notification

# Configure logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs/downloader.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AsyncPlaywrightDownloader:
    """
    Asynchronous Playwright-based downloader for automating file downloads.
    """

    async def launch(
        self,
        headless: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080
    ) -> tuple:
        logging.info(f"Launching browser (headless={headless})...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": viewport_width, "height": viewport_height}
        )
        page = await context.new_page()
        logging.info("Browser launched successfully")
        return playwright, browser, context, page

    async def download_site(
        self,
        site_key: str,
        config: dict,
        email_config: dict,
        max_retries: int = 3
    ) -> str:
        log_msg = f"Starting download for site: {site_key}"
        logging.info(log_msg)

        playwright, browser, context, page = await self.launch(headless=False)

        try:
            # Step 1: Navigate to target URL
            logging.info(f"Navigating to: {config['url']}")
            await page.goto(
                config["url"],
                wait_until="networkidle",
                timeout=60000
            )
            logging.info("Page loaded successfully")

            # Step 2: Click Export button to open export dialog
            logging.info("Clicking Export button...")
            await page.get_by_role("button", name="Export").click()

            # Wait for the dialog to appear to ensure DOM is ready
            export_dialog = page.locator("forge-dialog[aria-labelledby='export-dialog-title']")
            await export_dialog.wait_for(state="visible", timeout=10000)
            logging.info("Export dialog opened successfully.")

            # Debug screenshot
            await page.screenshot(path=f"debug_{site_key}_after_export.png")
            logging.info(f"Debug screenshot saved: debug_{site_key}_after_export.png")

            # Step 3: Select export format (try primary, then fallback)
            async def select_export_format(format_name):
                logging.info(f"Attempting to select format: {format_name}")
                format_dropdown = page.locator('[data-testid="export-type-select"]')
                
                # Check if dropdown is already open to avoid accidentally closing it
                is_expanded = await format_dropdown.get_attribute("aria-expanded") == "true"
                
                if not is_expanded:
                    await format_dropdown.click()
                    await page.wait_for_timeout(1000) # Wait for overlay to render
                
                # Target the visible <button role="option"> in the overlay to avoid 
                # strict mode violations with hidden <forge-option> elements.
                option_selector = page.locator('button[role="option"]').filter(has_text=format_name)
                
                try:
                    await option_selector.first.wait_for(state="visible", timeout=5000)
                    await option_selector.first.click()
                    logging.info(f"Format '{format_name}' selected successfully.")
                except PlaywrightTimeoutError:
                    logging.warning(f"Overlay option not found for '{format_name}'. Retrying dropdown click...")
                    await format_dropdown.click(force=True)
                    await page.wait_for_timeout(1000)
                    
                    await option_selector.first.wait_for(state="visible", timeout=5000)
                    await option_selector.first.click()

            try:
                logging.info(f"Selecting format: {config['format']}")
                await select_export_format(config["format"])
            except Exception as e:
                fallback = config.get("fallback_format", "CSV for Excel")
                logging.warning(f"Primary format failed ({e}), trying fallback: {fallback}")
                try:
                    await select_export_format(fallback)
                except Exception as fallback_error:
                    logging.error(f"Fallback format selection also failed: {fallback_error}")
                    raise

            # Step 4: Select "All data" option
            logging.info("Selecting 'All data' option...")
            try:
                # Try radio button first, then checkbox, then generic text
                all_data_radio = page.get_by_role("radio", name="All data")
                if await all_data_radio.count() > 0:
                    await all_data_radio.check()
                else:
                    await page.get_by_text("All data", exact=True).first.check()
            except Exception as e:
                logging.warning(f"Could not select 'All data' via check(): {e}. Trying click()...")
                try:
                    await page.get_by_text("All data", exact=True).first.click()
                except Exception as e2:
                    logging.warning(f"Could not select 'All data': {e2}. It might already be selected.")

            # Step 5: Click Download button to start download
            logging.info("Initiating download...")
            download_btn = page.get_by_role("button", name="Download")
            
            # Use async with to properly manage the download event listener
            # This prevents the "Future exception was never retrieved" asyncio error
            async with page.expect_download(timeout=180000) as download_info:
                await download_btn.click()
            
            download = await download_info.value
            suggested_filename = download.suggested_filename
            logging.info(f"Download started: {suggested_filename}")

            # Step 6: Ensure target directory exists and save file
            await ensure_dir(config["download_dir"])
            save_path = Path(config["download_dir"]) / suggested_filename
            await download.save_as(str(save_path))

            success_msg = f"✅ Successfully downloaded: {save_path}"
            logging.info(success_msg)

            # Step 7: Send success email notification with attachment
            await send_email_notification(
                subject=f"Download Complete: {site_key}",
                body=f"{success_msg}\n\nFile saved to: {save_path}",
                attachment_path=str(save_path),
                config=email_config
            )

            return str(save_path)

        except Exception as e:
            error_msg = f"❌ Download failed for {site_key}: {type(e).__name__}: {e}"
            logging.error(error_msg, exc_info=True)

            # Send failure email notification
            try:
                await send_email_notification(
                    subject=f"Download Failed: {site_key}",
                    body=f"{error_msg}\n\nPlease check logs/downloader.log for details.",
                    config=email_config
                )
            except Exception as email_err:
                logging.error(f"Also failed to send error email: {email_err}")

            raise

        finally:
            logging.info(f"Closing browser for {site_key}...")
            try:
                await context.close()
                await browser.close()
                await playwright.stop()
            except Exception as close_err:
                logging.warning(f"Error closing browser: {close_err}")
            logging.info(f"Browser closed for {site_key}")

async def run_parallel(sites: dict, email_config: dict) -> list:
    logging.info(f"🚀 Starting parallel downloads for {len(sites)} site(s)")

    tasks = [
        AsyncPlaywrightDownloader().download_site(key, cfg, email_config)
        for key, cfg in sites.items()
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if not isinstance(r, Exception))
    fail_count = sum(1 for r in results if isinstance(r, Exception))

    logging.info(f"Parallel downloads complete: {success_count} succeeded, {fail_count} failed")

    return results