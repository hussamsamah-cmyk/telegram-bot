
import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الحصول على المتغيرات البيئية
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OWNER_CHAT_ID = os.getenv('OWNER_CHAT_ID')

# التحقق من وجود التوكن
if not TOKEN:
    logger.error("لم يتم العثور على TELEGRAM_BOT_TOKEN في المتغيرات البيئية!")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة ترحيب عند تشغيل الأمر /start"""
    welcome_text = (
        "أهلاً بك! أنا بوت Hussam Designer المساعد الذكي.\n\n"
        "يمكنني مساعدتك في:\n"
        "1. تصميم باترونات الملابس.\n"
        "2. خدمات Gerber AccuMark التقنية.\n"
        "3. بيع البرامج والأدوات المخصصة.\n\n"
        "كيف يمكنني مساعدتك اليوم؟"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة مساعدة عند تشغيل الأمر /help"""
    await update.message.reply_text("أرسل لي أي استفسار وسأقوم بالرد عليك فوراً.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعامل مع الرسائل الواردة باستخدام OpenRouter AI"""
    user_text = update.message.text
    
    # إذا لم يتوفر مفتاح AI، نرد برسالة بسيطة
    if not OPENROUTER_API_KEY:
        await update.message.reply_text("عذراً، نظام الذكاء الاصطناعي غير مفعل حالياً. يرجى التواصل مع الإدارة.")
        return

    try:
        # إرسال طلب إلى OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {"role": "system", "content": "أنت مساعد ذكي لبوت Hussam Designer. تخصصك هو تصميم باترونات الملابس وخدمات Gerber AccuMark. رد دائماً باللغة العربية بأسلوب مهني وودود."},
                    {"role": "user", "content": user_text}
                ]
            }
        )
        response.raise_for_status()
        ai_response = response.json()['choices'][0]['message']['content']
        await update.message.reply_text(ai_response)
        
        # إخطار صاحب البوت بالرسالة (اختياري)
        if OWNER_CHAT_ID:
            try:
                await context.bot.send_message(
                    chat_id=OWNER_CHAT_ID,
                    text=f"رسالة جديدة من {update.effective_user.first_name}:\n{user_text}"
                )
            except Exception as e:
                logger.error(f"فشل إرسال الإشعار للمالك: {e}")

    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")
        await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة لاحقاً.")

def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()

    # إضافة المعالجات (Handlers)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء التشغيل
    logger.info("بدأ تشغيل البوت...")
    application.run_polling()

if __name__ == '__main__':
    main()
