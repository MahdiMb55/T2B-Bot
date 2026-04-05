import asyncio
import json
from balethon import Client


class BaleFileSender:
    def __init__(self,  chat_id: str):
        self.chat_id = chat_id
        self.bots = []
        self.index = 0

        self._load_bots("config.json")

    def _load_bots(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for bot in data.get("bale_bots", []):
            token = bot.get("token")
            if token:
                self.bots.append(Client(token))

        if not self.bots:
            raise Exception("No bots found in config!")

    def _get_next_bot(self):
        bot = self.bots[self.index]
        self.index = (self.index + 1) % len(self.bots)
        return bot

    async def _send_file(self, bot: Client, file_path: str):
        await bot.send_document(
            chat_id=self.chat_id,
            document=file_path
        )

    async def send_files(self, files: list):
        tasks = []

        for file_path in files:
            bot = self._get_next_bot()
            tasks.append(self._send_file(bot, file_path))

        await asyncio.gather(*tasks)