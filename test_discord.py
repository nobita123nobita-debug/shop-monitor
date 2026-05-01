#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

def test_discord():
    """Send test notification to Discord."""
    if not DISCORD_WEBHOOK:
        print("❌ Discord webhook URL not set!")
        return False

    embed = {
        "title": "✅ テスト通知",
        "description": "ショップ監視ツールが正常に動作しています！",
        "color": 3066993,
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {"name": "テスト時刻", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True},
            {"name": "ステータス", "value": "✅ 接続成功", "inline": True},
            {"name": "対象URL", "value": "https://onlineshop.55mth.com/", "inline": False},
        ],
    }

    payload = {
        "username": "Shop Monitor",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3143/3143615.png",
        "embeds": [embed],
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Discord通知送信成功！")
        return True
    except requests.RequestException as e:
        print(f"❌ Discord通知送信失敗: {e}")
        return False

if __name__ == "__main__":
    test_discord()
