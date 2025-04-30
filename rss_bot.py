import os
import time
import feedparser
import requests
from telegram import Bot
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RSS_FEED_URL = "https://onlykdrama.online/feed/"
CHECK_INTERVAL = 300  # 5 minutes
LAST_POST_FILE = "last_post.txt"

bot = Bot(token=BOT_TOKEN)

def get_last_post_link():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as file:
            return file.read().strip()
    return None

def save_last_post_link(link):
    with open(LAST_POST_FILE, "w") as file:
        file.write(link)

def extract_image(entry):
    if 'content' in entry and entry.content:
        soup = BeautifulSoup(entry.content[0].value, "html.parser")
        img = soup.find("img")
        return img["src"] if img else None
    return None

def send_to_telegram(entry):
    title = entry.title
    link = entry.link
    image_url = extract_image(entry)
    caption = f"📰 <b>{title}</b>\n🆕 <b>Added on Website</b>\n🔗 {link}"

    if image_url:
        bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption, parse_mode="HTML")
    else:
        bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML")

def run_bot():
    while True:
        feed = feedparser.parse(RSS_FEED_URL)
        if feed.entries:
            latest = feed.entries[0]
            last_link = get_last_post_link()
            if latest.link != last_link:
                send_to_telegram(latest)
                save_last_post_link(latest.link)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
