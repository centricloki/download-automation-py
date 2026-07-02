import json
import hashlib
import aiohttp
from pathlib import Path
import logging
import pandas as pd

async def has_updates(site_key: str, config: dict) -> bool:
    if not config.get("check_updates"):
        return True

    metadata_path = Path(config.get("metadata_file", f"downloads/{site_key}/metadata.json"))
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    # Load previous metadata
    previous = {}
    if metadata_path.exists():
        try:
            with open(metadata_path) as f:
                previous = json.load(f)
        except:
            pass

    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(config["url"], timeout=15) as resp:
                headers = dict(resp.headers)
                current_meta = {
                    "last_modified": headers.get("Last-Modified"),
                    "content_length": headers.get("Content-Length"),
                    "etag": headers.get("ETag")
                }
        except:
            current_meta = {}

    # If no metadata available, download anyway
    if not current_meta or not previous:
        save_metadata(current_meta, metadata_path)
        return True

    # Compare
    if (current_meta.get("last_modified") == previous.get("last_modified") and
        current_meta.get("content_length") == previous.get("content_length")):
        logging.info(f"✅ No updates detected for {site_key}")
        return False

    logging.info(f"🔄 Updates detected for {site_key}")
    save_metadata(current_meta, metadata_path)
    return True

def save_metadata(meta: dict, path: Path):
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)