import os
import telebot
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_CHAT_ID')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت ذكاء اصطناعي أعمل على مدار الساعة على منصة Koyeb.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [{"role": "user", "content": message.text}]
            }
        )
        response.raise_for_status()
        ai_message = response.json()['choices'][0]['message']['content']
        bot.reply_to(message, ai_message)
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(message, "عذراً، حدث خطأ في معالجة طلبك. تأكد من إعداد المفاتيح بشكل صحيح.")

if __name__ == "__main__":
    logger.info("Bot is starting...")
    bot.infinity_polling()
