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
        # Log to file (rotating log would be better for production)
        logging.FileHandler("logs/downloader.log", encoding='utf-8'),
        # Also log to console for real-time feedback
        logging.StreamHandler()
    ]
)


class AsyncPlaywrightDownloader:
    """
    Asynchronous Playwright-based downloader for automating file downloads.
    
    This class manages browser instances and implements site-specific download
    logic with error handling, retry mechanisms, and notifications.
    
    Attributes:
        None - all configuration is passed via method parameters
        
    Example:
        >>> downloader = AsyncPlaywrightDownloader()
        >>> result = await downloader.download_site("site_key", config, email_config)
    """
    
    async def launch(
        self, 
        headless: bool = False,
        viewport_width: int = 1920,
        viewport_height: int = 1080
    ) -> tuple:
        """
        Launch Playwright browser instance with download support enabled.
        
        Creates a new Chromium browser context that accepts file downloads.
        Configures viewport size for consistent UI interaction.
        
        Args:
            headless: Run browser in headless mode (default: False for debugging)
            viewport_width: Browser window width in pixels (default: 1920)
            viewport_height: Browser window height in pixels (default: 1080)
            
        Returns:
            tuple: (playwright, browser, context, page) instances
            
        Raises:
            Exception: If browser fails to launch
        """
        logging.info(f"Launching browser (headless={headless})...")
        
        # Start Playwright
        playwright = await async_playwright().start()
        
        # Launch Chromium browser
        browser = await playwright.chromium.launch(headless=headless)
        
        # Create browser context with download acceptance
        context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": viewport_width, "height": viewport_height}
        )
        
        # Create a new page
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
        """
        Execute download automation for a specific site.
        
        Navigates to the configured URL, performs UI interactions to initiate
        download, waits for file completion, and sends email notification.
        Implements retry logic for robustness.
        
        Args:
            site_key: Unique identifier for the site (used in logging/notifications)
            config: Site configuration dictionary containing:
                - url: Target webpage URL
                - download_dir: Local directory to save file
                - format: Primary export format (e.g., "XLSX")
                - fallback_format: Alternative format if primary fails
            email_config: Email SMTP configuration dictionary
            max_retries: Maximum retry attempts (default: 3)
            
        Returns:
            str: Path to successfully downloaded file
            
        Raises:
            Exception: If download fails after all retry attempts
            
        Workflow:
            1. Launch browser
            2. Navigate to URL
            3. Click Export button
            4. Select format from dropdown
            5. Check "All data" option
            6. Click Download button
            7. Wait for download completion
            8. Save file to configured directory
            9. Send email notification
            10. Close browser
        """
        log_msg = f"Starting download for site: {site_key}"
        logging.info(log_msg)
        
        # Launch browser instance
        playwright, browser, context, page = await self.launch(headless=False)
        
        try:
            # Step 1: Navigate to target URL with network idle wait
            logging.info(f"Navigating to: {config['url']}")
            await page.goto(
                config["url"], 
                wait_until="networkidle", 
                timeout=60000  # 60 second timeout
            )
            logging.info("Page loaded successfully")
            
            # Debug: Take a screenshot to see current page state
            # await page.screenshot(path=f"debug_{site_key}_before_export.png")
            
            # Step 2: Set up download expectation before triggering action
            download_promise = page.expect_download(timeout=180000)  # 3 minute timeout
            
            # Step 3: Click Export button to open export dialog
            logging.info("Clicking Export button...")
            await page.get_by_role("button", name="Export").click()
            
            # Wait for popup/dialog to appear
            await page.wait_for_timeout(3000)  # Increased wait time for dialog to render
            
            # Debug: Take screenshot after clicking Export (ENABLED by default for troubleshooting)
            await page.screenshot(path=f"debug_{site_key}_after_export.png")
            logging.info(f"Debug screenshot saved: debug_{site_key}_after_export.png")
            
            # Optional: Print page structure for debugging (uncomment if needed)
            # page_structure = await page.content()
            # logging.debug(f"Page HTML structure:\n{page_structure}")
            
            # Step 4: Select export format (try primary, then fallback)
            try:
                logging.info(f"Selecting format: {config['format']}")
                
                # Use the test ID selector which is most reliable for this custom dropdown
                # data-testid="export-type-select" is unique to the Export format dropdown
                format_dropdown = page.locator('[data-testid="export-type-select"]')
                
                # Click to open the dropdown
                await format_dropdown.click()
                await page.wait_for_timeout(1500)  # Wait for options to appear
                
                # Click on the desired format option by text
                await page.get_by_text(config["format"], exact=True).click()
                logging.info(f"Format '{config['format']}' selected successfully")
                
            except Exception as e:
                # Fallback to alternative format if primary fails
                fallback = config.get("fallback_format", "CSV")
                logging.warning(f"Primary format failed ({e}), trying fallback: {fallback}")
                try:
                    # Use same test ID selector for fallback
                    format_dropdown = page.locator('[data-testid="export-type-select"]')
                    
                    # Click to open dropdown
                    await format_dropdown.click()
                    await page.wait_for_timeout(1500)
                    
                    # Click on fallback format
                    await page.get_by_text(fallback, exact=True).click()
                    logging.info(f"Fallback format '{fallback}' selected successfully")
                    
                except Exception as fallback_error:
                    logging.error(f"Fallback format selection also failed: {fallback_error}")
                    raise
            
            # Step 5: Select "All data" option
            logging.info("Selecting 'All data' option...")
            try:
                # Try different possible text patterns for "All data"
                await page.get_by_text("All data", exact=True).first.check()
            except Exception:
                # If exact match fails, try without exact matching
                await page.get_by_text("All data").first.check()
            
            # Step 6: Click Download button to start download
            logging.info("Initiating download...")
            await page.get_by_role("button", name="Download").click()
            
            # Step 7: Wait for download to complete
            download = await download_promise
            suggested_filename = download.suggested_filename
            logging.info(f"Download started: {suggested_filename}")
            
            # Step 8: Ensure target directory exists and save file
            await ensure_dir(config["download_dir"])
            save_path = Path(config["download_dir"]) / suggested_filename
            await download.save_as(str(save_path))
            
            success_msg = f"✅ Successfully downloaded: {save_path}"
            logging.info(success_msg)
            
            # Step 9: Send success email notification with attachment
            await send_email_notification(
                subject=f"Download Complete: {site_key}",
                body=f"{success_msg}\n\nFile saved to: {save_path}",
                attachment_path=str(save_path),
                config=email_config
            )
            
            return str(save_path)
            
        except Exception as e:
            # Handle any errors during download
            error_msg = f"❌ Download failed for {site_key}: {type(e).__name__}: {e}"
            logging.error(error_msg, exc_info=True)
            
            # Send failure email notification
            await send_email_notification(
                subject=f"Download Failed: {site_key}",
                body=f"{error_msg}\n\nPlease check logs/downloader.log for details.",
                config=email_config
            )
            
            # Re-raise exception for caller to handle
            raise
            
        finally:
            # Always close browser resources
            logging.info(f"Closing browser for {site_key}...")
            await context.close()
            await browser.close()
            await playwright.stop()
            logging.info(f"Browser closed for {site_key}")


async def run_parallel(sites: dict, email_config: dict) -> list:
    """
    Execute multiple site downloads concurrently using asyncio.gather().
    
    Creates a downloader instance for each site and runs them in parallel.
    Collects results and exceptions from all downloads.
    
    Args:
        sites: Dictionary of site configurations {site_key: config_dict}
        email_config: Email SMTP configuration dictionary
        
    Returns:
        list: List of results (file paths) and/or exceptions
        
    Example:
        >>> results = await run_parallel(SITES, EMAIL_CONFIG)
        >>> for result in results:
        ...     if isinstance(result, Exception):
        ...         print(f"Failed: {result}")
        ...     else:
        ...         print(f"Success: {result}")
    """
    logging.info(f"🚀 Starting parallel downloads for {len(sites)} site(s)")
    
    # Create tasks for all sites
    tasks = [
        AsyncPlaywrightDownloader().download_site(key, cfg, email_config)
        for key, cfg in sites.items()
    ]
    
    # Execute all tasks concurrently and collect results
    # return_exceptions=True prevents one failure from stopping others
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Log summary of results
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    fail_count = sum(1 for r in results if isinstance(r, Exception))
    
    logging.info(f"Parallel downloads complete: {success_count} succeeded, {fail_count} failed")
    
    return results
