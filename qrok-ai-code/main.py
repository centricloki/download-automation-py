#!/usr/bin/env python3
"""
Main entry point for the Playwright Download Automation Framework.

This script provides a command-line interface to execute download automation
for one or multiple configured websites. It supports three execution modes:

1. Run all sites (default):
   python main.py

2. Run specific site(s):
   python main.py --site delaware_business_licenses another_site

3. Run sites from a text file (one site key per line):
   python main.py --file sites.txt

Features:
- Parallel execution of multiple downloads
- Async/await for efficient I/O operations
- Comprehensive logging to file and console
- Email notifications on success/failure
- Error retry logic with exponential backoff
- Scalable architecture for adding new sites

Usage Examples:
    # Run all configured sites in parallel
    python main.py
    
    # Run a single specific site
    python main.py --site delaware_business_licenses
    
    # Run multiple specific sites
    python main.py --site delaware_business_licenses another_site
    
    # Run sites listed in a text file
    python main.py --file sites.txt
    
    # Text file format (sites.txt):
    # One site key per line
    # Lines starting with # are comments
    delaware_business_licenses
    # another_site
"""

import asyncio
import argparse
from pathlib import Path
from config import SITES, EMAIL_CONFIG
from downloader import run_parallel
from utils import ensure_dir


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the download automation.
    
    Returns:
        argparse.Namespace: Parsed arguments containing:
            - site: Optional list of site keys to run
            - file: Optional path to text file with site keys
            
    Example:
        >>> args = parse_arguments()
        >>> if args.site:
        ...     print(f"Running sites: {args.site}")
    """
    parser = argparse.ArgumentParser(
        description="Playwright Download Automation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Run all sites
  python main.py --site site1                 # Run single site
  python main.py --site site1 site2           # Run multiple sites
  python main.py --file sites.txt             # Run sites from file
        """
    )
    
    parser.add_argument(
        "--site", 
        nargs="*",  # Accept zero or more values
        help="One or more site keys to run (e.g., --site delaware_business_licenses)"
    )
    
    parser.add_argument(
        "--file", 
        help="Text file containing site keys (one per line, # for comments)"
    )
    
    return parser.parse_args()


def load_sites_from_file(file_path: str) -> list:
    """
    Load site keys from a text file, ignoring comments and blank lines.
    
    Args:
        file_path: Path to text file with site keys
        
    Returns:
        list: List of valid site key strings
        
    Example:
        >>> sites = load_sites_from_file("sites.txt")
        >>> print(sites)
        ['delaware_business_licenses', 'another_site']
    """
    site_keys = []
    
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    site_keys.append(line)
                    
        logging.info(f"Loaded {len(site_keys)} site(s) from {file_path}")
        
    except FileNotFoundError:
        logging.error(f"Sites file not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading sites file {file_path}: {e}")
        raise
    
    return site_keys


async def main():
    """
    Main async entry point for the download automation framework.
    
    Orchestrates the execution flow:
    1. Parse command-line arguments
    2. Determine which sites to run (priority: --site > --file > all)
    3. Create necessary directories (logs, downloads)
    4. Execute downloads in parallel
    5. Report results
    
    Execution Priority:
    1. --site flag (explicit site keys)
    2. --file flag (site keys from text file)
    3. No flags (run all configured sites)
    
    Returns:
        None
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Ensure required directories exist
    await ensure_dir("logs")
    await ensure_dir("downloads")
    
    # Determine which sites to process based on arguments
    selected_sites = {}
    
    if args.site:
        # Priority 1: --site flag provided
        for key in args.site:
            if key in SITES:
                selected_sites[key] = SITES[key]
            else:
                print(f"⚠️  Warning: Site '{key}' not found in configuration.")
                
    elif args.file:
        # Priority 2: --file flag provided
        try:
            site_keys = load_sites_from_file(args.file)
            
            for key in site_keys:
                if key in SITES:
                    selected_sites[key] = SITES[key]
                else:
                    print(f"⚠️  Warning: Site '{key}' not found in configuration.")
                    
        except Exception as e:
            print(f"❌ Error reading sites file: {e}")
            return
            
    else:
        # Priority 3: No flags - run all configured sites
        selected_sites = SITES
    
    # Validate that we have sites to run
    if not selected_sites:
        print("❌ No valid sites to process. Exiting.")
        return
    
    # Display execution summary
    print(f"🚀 Starting download automation for {len(selected_sites)} site(s)")
    print(f"   Sites: {list(selected_sites.keys())}")
    print("=" * 60)
    
    # Execute downloads in parallel
    results = await run_parallel(selected_sites, EMAIL_CONFIG)
    
    # Display results summary
    print("=" * 60)
    print("📊 Results Summary:")
    
    success_count = 0
    fail_count = 0
    skipped_count = 0 
    
    for i, result in enumerate(results):
        site_key = list(selected_sites.keys())[i]

        if isinstance(result, Exception):
            fail_count += 1
            print(f" ❌ {site_key}: {type(result).__name__}: {str(result)[:100]}")
        elif isinstance(result, str) and result.startswith("SKIPPED:"):
            skipped_count += 1
            print(f" ⏭️ {site_key}: {result}")
        else:
            success_count += 1
            print(f" ✅ {site_key}: {result}")
    
    print("=" * 60)
    print(f"✅ Success: {success_count} | ⏭️ Skipped: {skipped_count} | ❌ Failed: {fail_count}")
    print("Check logs/downloader.log for detailed information.")


if __name__ == "__main__":
    # Entry point - run the async main function
    asyncio.run(main())
