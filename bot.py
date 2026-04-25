import os
import telebot
import requests

# Get environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_CHAT_ID')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت ذكاء اصطناعي أعمل على مدار الساعة.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # Simple AI response via OpenRouter (example)
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
        ai_message = response.json()['choices'][0]['message']['content']
        bot.reply_to(message, ai_message)
    except Exception as e:
        bot.reply_to(message, "عذراً، حدث خطأ في معالجة طلبك.")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
