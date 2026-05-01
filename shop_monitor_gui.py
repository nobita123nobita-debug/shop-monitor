#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import schedule
import time
import subprocess
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

class ShopMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("?????????")
        self.root.geometry("500x400")
        self.scheduler_thread = None
        self.running = False

        # URL??
        ttk.Label(root, text="????URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.insert(0, "https://onlineshop.55mth.com/")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # ??????1
        ttk.Label(root, text="??????1 (HH:MM):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.time1_entry = ttk.Entry(root, width=20)
        self.time1_entry.insert(0, "20:00")
        self.time1_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # ??????2
        ttk.Label(root, text="??????2 (HH:MM):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.time2_entry = ttk.Entry(root, width=20)
        self.time2_entry.insert(0, "20:01")
        self.time2_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # ???????
        ttk.Label(root, text="?????:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.status_label = ttk.Label(root, text="???", foreground="red")
        self.status_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # ???
        button_frame = ttk.Frame(root)
        button_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

        self.start_btn = ttk.Button(button_frame, text="??", command=self.start_monitor)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(button_frame, text="??", command=self.stop_monitor, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # ????
        ttk.Label(root, text="??:").grid(row=5, column=0, padx=10, pady=10, sticky="nw")
        self.log_text = tk.Text(root, height=8, width=60)
        self.log_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def log(self, message):
        self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")
        self.root.update()

    def start_monitor(self):
        url = self.url_entry.get()
        time1 = self.time1_entry.get()
        time2 = self.time2_entry.get()

        if not url or not time1 or not time2:
            messagebox.showerror("???", "???????????????")
            return

        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="???", foreground="green")

        self.scheduler_thread = threading.Thread(target=self.run_scheduler, args=(url, time1, time2), daemon=True)
        self.scheduler_thread.start()

        self.log(f"????: {url}")
        self.log(f"??????: {time1}, {time2}")

    def run_scheduler(self, url, time1, time2):
        schedule.clear()

        def check_shop():
            self.log(f"???????: {url}")
            import requests
            import hashlib
            import json
            from pathlib import Path

            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=10)
                content = response.text
                current_hash = hashlib.sha256(content.encode()).hexdigest()

                snapshot_file = "snapshot.json"
                if Path(snapshot_file).exists():
                    with open(snapshot_file, "r") as f:
                        last = json.load(f)
                    if current_hash != last["hash"]:
                        self.log("? ?????Discord?????...")
                        self.send_notification(url)
                    else:
                        self.log("? ????")
                else:
                    with open(snapshot_file, "w") as f:
                        json.dump({"hash": current_hash, "timestamp": datetime.now().isoformat()}, f)
                    self.log("???? - ??????????")

            except Exception as e:
                self.log(f"? ???: {e}")

        schedule.every().day.at(time1).do(check_shop)
        schedule.every().day.at(time2).do(check_shop)

        while self.running:
            schedule.run_pending()
            time.sleep(60)

    def send_notification(self, url):
        import requests

        embed = {
            "title": "?? ????????",
            "description": f"{url} ?????????",
            "color": 15105570,
            "timestamp": datetime.now().isoformat(),
        }

        payload = {
            "username": "Shop Monitor",
            "embeds": [embed],
        }

        try:
            response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
            self.log("? Discord??????")
        except Exception as e:
            self.log(f"? ??????: {e}")

    def stop_monitor(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="???", foreground="red")
        self.log("????")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShopMonitorApp(root)
    root.mainloop()
