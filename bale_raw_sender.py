import json
import requests
import asyncio
import os


class BaleRawSender:
    def __init__(self, chat_id: str, config_path: str = "config.json"):
        self.chat_id = chat_id
        self.index = 0
        self.bots = []
        self.lock = asyncio.Lock()

        self._load_bots(config_path)

    def _load_bots(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for bot in data.get("bale_bots", []):
            token = bot.get("token")
            if token:
                self.bots.append(token)

        if not self.bots:
            raise Exception("No bots found in config.json")

    async def _get_next_token(self):
        async with self.lock:
            token = self.bots[self.index]
            self.index = (self.index + 1) % len(self.bots)
            return token

    def _build_url(self, token):
        return f"https://tapi.bale.ai/bot{token}/sendDocument"

    def _send_sync(self, token, file):
        url = self._build_url(token)

        data = {
            "chat_id": self.chat_id,
        }

        # حالت 1: file_id یا URL
        if isinstance(file, str) and not os.path.exists(file):
            data["document"] = file
            return requests.post(url, json=data)

        # حالت 2: فایل لوکال (multipart)
        with open(file, "rb") as f:
            files = {
                "document": f
            }
            return requests.post(url, data=data, files=files)

    async def send_files(self, files: list):
        loop = asyncio.get_event_loop()
        tasks = []

        for file in files:
            token = await self._get_next_token()
            tasks.append(loop.run_in_executor(None, self._send_sync, token, file))

        results = await asyncio.gather(*tasks)

        # لاگ ساده
        for i, r in enumerate(results):
            try:
                print(f"✅ file {i} -> {r.status_code}")
            except:
                print(f"❌ file {i} failed")