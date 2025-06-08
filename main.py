import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# API anahtarları (çevre değişkenlerinden)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Hafıza ve blacklist ayarları
USER_MEMORY = {}
MAX_HISTORY = 5

BLACKLIST = [
    "din", "allah", "jeset", "syýasy", "porn", "ýarag", "intihar", "öldür", "adam öldür", 
    "seni kim döretdi", "ýaradyjy", "Ýahudy", "Hristian", "Musulman", "Ilon Mask"
]

# İşletme Bilgisi
ISLETME_BILGI = """
Salam dost! Men Redzone AI — Pubg Mobile oýunyndaky UC (Unknown Cash) satyn almakda siziň iň gowy kömekçiňiz.

🔰 **Näme üçin siz UC satyn almaly?**
UC — Pubg Mobile’daky ähli aýratynlyklaryň, “skin”-leriň, “royal pass”-laryň we oýun içinde tapawutlanmagyň açarydyr.

🎯 **Näme üçin Redzone saýlamaly?**
✔️ Tiz hyzmat
✔️ Ynamdar hyzmat
✔️ Amatly bahalar
✔️ Müşderi goldawy
✔️ Aksiýalar we bonuslar
✔️ Onlaýn hyzmat + mobil programma

📞 **Habarlaşmak üçin:** 
+99362251883  
+99361365984

🌐 **Web saýdy:** https://redzonegg.com  
📲 **Instagram:** @redzone_official  
📢 **Telegram:** @redZone_gg  
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ['group', 'supergroup']:
        if not context.bot.username.lower() in update.message.text.lower():
            return

    user_id = update.effective_user.id
    user_message = update.message.text.replace(f"@{context.bot.username}", "").strip()

    if any(term in user_message.lower() for term in BLACKLIST):
        await update.message.reply_text("Bagyşlaň, bu tema boýunça kömek edip bilemok.")
        return

    previous = USER_MEMORY.get(user_id, [])
    previous.append(f"Kullanýjy: {user_message}")
    USER_MEMORY[user_id] = previous[-MAX_HISTORY:]
    history_text = "\n".join(USER_MEMORY[user_id])

    prompt = (
        f"{ISLETME_BILGI}\n\n"
        f"Dost bilen gepleşik:\n{history_text}\n\n"
        f"Dostdan täze sorag:\n{user_message}\n\n"
        f"⚠️ Edebe laýyk we umumy maglumatlara jogap ber, dini/syýasy/ahlakdan daş temalardan gaç. Jogap bereniňde köplenç 'Dost' diýip gürleş, bilmedik sorag berilende 'Bagyşlaň, soragyňyza düşünmedim. Başga bir soragyňyz barmy?' diý. Emojiler ulan."
    )

    try:
        response = model.generate_content(prompt)
        bot_reply = response.text or response.candidates[0].content.parts[0].text
    except Exception as e:
        print("Model hatasy:", e)
        bot_reply = "Bagyşlaň, näsazlyk ýüze çykdy."

    USER_MEMORY[user_id].append(f"Redzone AI: {bot_reply}")
    USER_MEMORY[user_id] = USER_MEMORY[user_id][-MAX_HISTORY:]

    await update.message.reply_text(bot_reply)

if __name__ == "__main__":
    print("Bot işleýär... Synap görüň!")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
