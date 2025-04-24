import requests
import re
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Function to extract the direct link (simple scraping)
def extract_direct_link(shared_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(shared_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find a direct video or download link pattern
        script_tags = soup.find_all('script')
        for script in script_tags:
            if 'downloadLink' in script.text:
                match = re.search(r'"downloadLink":"(https:[^"]+)"', script.text)
                if match:
                    direct_link = match.group(1).replace('\\u002F', '/')
                    return direct_link
    except Exception as e:
        return f"Error: {str(e)}"

    return None

# Telegram message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    match = re.search(r'https?://(?:www\.)?terabox\.com/s/[A-Za-z0-9]+', text)

    if match:
        link = match.group(0)
        await update.message.reply_text(f"Processing link: {link}")

        direct_link = extract_direct_link(link)

        if direct_link:
            await update.message.reply_text(f"Here is your direct link:\n{direct_link}")
        else:
            await update.message.reply_text("Couldn't extract the direct link. TeraBox might have changed the structure.")
    else:
        await update.message.reply_text("Please send a valid TeraBox share link.")

# Build bot app
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()