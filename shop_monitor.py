#!/usr/bin/env python3
import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TARGET_URL = "https://official-goods-store.jp/55mth/"
SNAPSHOT_FILE = "shop_snapshot.json"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")


def get_page_hash():
    """Fetch the website and return its hash."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text
        return hashlib.sha256(content.encode()).hexdigest(), content
    except requests.RequestException as e:
        print(f"Error fetching {TARGET_URL}: {e}")
        return None, None


def load_last_snapshot():
    """Load the last saved snapshot."""
    if Path(SNAPSHOT_FILE).exists():
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return None


def save_snapshot(content_hash):
    """Save the current snapshot."""
    snapshot = {
        "hash": content_hash,
        "timestamp": datetime.now().isoformat(),
    }
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)


def send_discord_notification(message, changed_details=None):
    """Send a notification to Discord."""
    if not DISCORD_WEBHOOK:
        print("Discord webhook URL not configured. Skipping notification.")
        return

    embed = {
        "title": "?? Shop Change Detected",
        "description": message,
        "color": 15105570,
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {"name": "Target", "value": TARGET_URL, "inline": False},
            {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True},
        ],
    }

    if changed_details:
        embed["fields"].append({
            "name": "Details",
            "value": changed_details,
            "inline": False,
        })

    payload = {
        "username": "Shop Monitor",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3143/3143615.png",
        "embeds": [embed],
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Discord notification sent at {datetime.now().strftime('%H:%M:%S')}")
    except requests.RequestException as e:
        print(f"Failed to send Discord notification: {e}")


def check_shop():
    """Main monitoring function."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking shop...")

    current_hash, content = get_page_hash()
    if current_hash is None:
        print("Could not fetch the page. Skipping check.")
        return

    last_snapshot = load_last_snapshot()

    if last_snapshot is None:
        print("First run - saving snapshot.")
        save_snapshot(current_hash)
        send_discord_notification("? Shop monitor started - baseline snapshot saved.")
        return

    if current_hash == last_snapshot["hash"]:
        print("? No changes detected.")
    else:
        print("? Changes detected!")
        save_snapshot(current_hash)

        last_time = last_snapshot["timestamp"]
        details = f"Last check: {last_time}\nCurrent time: {datetime.now().isoformat()}"

        send_discord_notification(
            f"The shop at {TARGET_URL} has been updated!",
            details
        )


if __name__ == "__main__":
    check_shop()
