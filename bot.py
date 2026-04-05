import asyncio
import json
import os
from telethon import TelegramClient, events

# load config
with open("config.json") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
bot_token = config["bot_token"]

client = TelegramClient("bot_session", api_id, api_hash)


# پاسخ به سلام
@client.on(events.NewMessage(pattern="سلام"))
async def hello_handler(event):
    await event.reply("علیک سلام")


# دریافت فایل با progress
@client.on(events.NewMessage)
async def file_handler(event):
    message = event.message

    if not message.file:
        return

    try:
        os.makedirs("downloads", exist_ok=True)

        progress_msg = await event.reply("⬇️ شروع دانلود...")

        last_percent = 0

        async def progress(current, total):
            nonlocal last_percent

            percent = int((current / total) * 100)

            # جلوگیری از اسپم (هر 5٪ آپدیت)
            if percent - last_percent >= 5:
                last_percent = percent
                try:
                    await progress_msg.edit(f"⬇️ در حال دانلود... {percent}%")
                except:
                    pass

        # دانلود با progress
        path = await client.download_media(
            message,
            file="downloads/",
            progress_callback=progress
        )

        await progress_msg.edit(f"✅ دانلود کامل شد:\n{path}")

    except Exception as e:
        print("Error:", str(e))
        await event.reply(f"❌ خطا: {str(e)}")


async def main():
    await client.start(bot_token=bot_token)
    print("🤖 Bot started")
    await client.run_until_disconnected()


try:
    with client:
        client.loop.run_until_complete(main())
except KeyboardInterrupt:
    print("\n⛔ Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())