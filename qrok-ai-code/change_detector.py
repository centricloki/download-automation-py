import json
import aiohttp
from pathlib import Path
import logging

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
        except Exception:
            pass

    current_meta = {}
    url = config["url"]
    
    # PRO-TIP: For Socrata data portals (like data.delaware.gov), query the metadata API
    # to get the exact timestamp when the dataset rows were last updated.
    if "data.delaware.gov" in url:
        try:
            # Extract dataset ID (e.g., 5zy2-grhr) from the URL
            dataset_id = url.rstrip('/').split('/')[-2]
            api_url = f"https://data.delaware.gov/api/views/{dataset_id}.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        current_meta["rows_updated_at"] = data.get("rowsUpdatedAt")
        except Exception as e:
            logging.warning(f"Failed to fetch Socrata metadata API: {e}")

    # Fallback to standard HTTP headers if Socrata API wasn't used or failed
    if not current_meta:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(url, timeout=15) as resp:
                    headers = dict(resp.headers)
                    current_meta = {
                        "last_modified": headers.get("Last-Modified"),
                        "content_length": headers.get("Content-Length"),
                        "etag": headers.get("ETag")
                    }
            except Exception:
                current_meta = {}

    # If no metadata available, download anyway
    if not current_meta or not previous:
        save_metadata(current_meta, metadata_path)
        return True

    # Compare based on what we collected
    is_updated = False
    if "rows_updated_at" in current_meta and "rows_updated_at" in previous:
        is_updated = current_meta["rows_updated_at"] != previous["rows_updated_at"]
    else:
        # Fallback comparison for standard HTTP headers
        is_updated = not (
            current_meta.get("last_modified") == previous.get("last_modified") and
            current_meta.get("content_length") == previous.get("content_length")
        )

    if not is_updated:
        logging.info(f"✅ No updates detected for {site_key}")
        return False

    logging.info(f"🔄 Updates detected for {site_key}")
    save_metadata(current_meta, metadata_path)
    return True

def save_metadata(meta: dict, path: Path):
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)