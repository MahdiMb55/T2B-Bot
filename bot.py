import json
import os
import asyncio
from telethon import TelegramClient, events
from splitter import split_file
from zipper import do_file_split
from bale_sender import BaleFileSender


# load config
with open("config.json") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
bot_token = config["bot_token"]

client = TelegramClient("bot_session", api_id, api_hash)

# محدود کردن تعداد دانلود همزمان
semaphore = asyncio.Semaphore(2)  # مثلا 2 تا همزمان


@client.on(events.NewMessage(pattern="سلام"))
async def hello_handler(event):
    await event.reply("علیک سلام")


@client.on(events.NewMessage)
async def file_handler(event):
    if not event.message.file:
        return

    # هر فایل در یک task جدا
    asyncio.create_task(handle_download(event))


async def handle_download(event):
    async with semaphore:  # کنترل همزمانی
        message = event.message

        try:
            os.makedirs("downloads", exist_ok=True)

            progress_msg = await event.reply("⬇️ شروع دانلود...")

            last_percent = 0

            async def progress(current, total):
                nonlocal last_percent

                percent = int((current / total) * 100)

                if percent - last_percent >= 5:
                    last_percent = percent
                    try:
                        await progress_msg.edit(f"⬇️ در حال دانلود... {percent}%")
                    except:
                        pass

            path = await client.download_media(
                message,
                file="downloads/",
                progress_callback=progress
            )

            await progress_msg.edit(f"✅ دانلود کامل شد:\n{path}")
            
            result = do_file_split(path)

            sender = BaleFileSender(
                config_path="config.json",
                chat_id="4360823791"
            )

            await sender.send_files(result["files"])


        except Exception as e:
            print("Error:", str(e))
            await event.reply(f"❌ خطا: {str(e)}")


async def main():
    await client.start(bot_token=bot_token)
    print("🤖 Bot started")
    await client.run_until_disconnected()


# ✅ اجرای درست Telethon
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())