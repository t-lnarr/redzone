from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import threading

app = Flask(__name__)

logs = []

# Telegram bot token
TOKEN = "BOT_TOKENIN_BURAYA"

# Telegram bot handler fonksiyonu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selam! Bot çalışıyor.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = {
        'id': update.effective_user.id,
        'username': update.effective_user.username,
        'first_name': update.effective_user.first_name
    }
    question = update.message.text
    # Burada bot cevabını üret (örnek cevap veriyorum)
    answer = f"Sen dedin ki: {question}"

    # Log kaydı
    logs.append({
        'user': user_info,
        'question': question,
        'answer': answer
    })

    await update.message.reply_text(answer)

# Telegram botu başlatma fonksiyonu (async)
async def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot işleýär... http://127.0.0.1:5000 paneli aç.")
    await application.run_polling()

# Flask ana sayfa - admin paneli için basit örnek
@app.route('/')
def admin_panel():
    html = "<h1>Admin Paneli</h1><ul>"
    for log in logs[-20:]:  # Son 20 log
        user = log['user']
        html += f"<li><b>{user.get('username') or user.get('first_name')}</b>: {log['question']} => {log['answer']}</li>"
    html += "</ul>"
    return html

# Flask ve botu aynı anda çalıştırmak için
def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Flask thread olarak başlat
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Async botu çalıştır
    asyncio.run(start_bot())
