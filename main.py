import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

# API anahtarları
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Hafıza ve blacklist
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
UC — Pubg Mobile’daky ähli aýratynlyklaryň, “skin”-leriň, “royal pass”-laryň we oýun içinde tapawutlanmagyň açarydyr. Öňde baryjy oýunçy bolmak, stiliňizi görkezmek we doly mümkinçiliklerden peýdalanmak üçin UC zerur!

🎯 **Näme üçin Redzone saýlamaly?**
✔️ **Tiz hyzmat:** Sargytlaryňyz gysga wagtyň içinde ýerine ýetirilýär.
✔️ **Ynamdar hyzmat:** Müşderilerimiziň ygtybarlylygyna ynamy bar.
✔️ **Amatly bahalar:** Bäsdeş bahalardan has ucuzy.
✔️ **Müşderi goldawy:** Islendik soraga hakyky işgärler we AI bilen çalt jogap.
✔️ **Yzygiderli aksiýalar:** Wagtal-wagtal arzanladyşlar we bonuslar!
✔️ **Onlaýn hyzmat + mobil programma:** Satyn almak, baha öwrenmek we akkauntlary görmek üçin diňe bize geliň.

📞 **Nädip satyn almaly?**
Satyn almak üçin bize **telefon arkaly jaň ediň**:
+99362251883
+99361365984

🌐 **Web saýdymyz:**
https://redzonegg.com

📲 **Redzone mobil programmasy:**
Programmany <a href="https://redzonegg.com/app-release.apk">📲 yüklemek üçin şu ýere bas</a>
Mobil programmamyzyň içinde:
- UC sargytlary
- Satlyk Pubg akkauntlary
- Täzelikler we indirimler bilen doly hyzmat bar!


📱 **Sosial mediada bizi tap:**
Instagram: @redzone_official
TikTok: @redzone_gg_official
Telegram: @redZone_gg

💸 **UC bahalary (telefon bilen töleg):**
▫️ 60 UC = 25 TMT
▫️ 325 UC = 120 TMT
▫️ 660 UC = 240 TMT
▫️ 1800 UC = 600 TMT
▫️ 3850 UC = 1200 TMT
▫️ 8100 UC = 2300 TMT

💵 **UC bahalary (nagt töleg):**
▫️ 60 UC = 19 TMT
▫️ 325 UC = 98 TMT
▫️ 660 UC = 193 TMT
▫️ 1800 UC = 480 TMT
▫️ 3850 UC = 960 TMT
▫️ 8100 UC = 1920 TMT

🤖 **Soraglaryňyz barmy?**
Islendik soragyňyzy sorap bilersiňiz. Men — Redzone AI — sizi ýalňyz galdyrmajak dostuňyz!
"""

# /start komutu işlendiğinde kullanıcı sanki “kendini tanit” yazmış gibi davran
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update.message.text = "sen kim ?"
    await handle_message(
    update=update,
    context=context,
    user_override_message="sen kim?"
    )

# Mesaj işleme fonksiyonu
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ['group', 'supergroup']:
        if not context.bot.username.lower() in update.message.text.lower():
            return

    user_id = update.effective_user.id
    user_message = update.message.text.replace(f"@{context.bot.username}", "").strip()

    
    if "Programmany nädip alyp bolar" in user_message or "apk" in user_message:
        download_link = "https://redzonegg.com/app-release.apk"
        reply_text = (
            "📲 <b>Redzone programmasyny şu ýerden ýükläp bilersiňiz:</b>\n"
            f'<a href="{download_link}">⬇️ Redzone.apk ýükle</a>'
        )
        await update.message.reply_text(reply_text, parse_mode="HTML")
        return
    
    # Yasaklı kelime filtresi
    if any(term in user_message.lower() for term in BLACKLIST):
        await update.message.reply_text("Bagyşlaň, bu tema boýunça kömek edip bilemok.")
        return

    # 'kendini tanit' gibi komutlara özel muamele
    if user_message.lower() in ["sen kim ?", "özüňi tanat", "who are you"]:
        user_message = "Redzone AI kim? Bize biraz özüň hakda gürrüň ber."

    # Kullanıcı geçmişi
    previous = USER_MEMORY.get(user_id, [])
    previous.append(f"Ulanyjy: {user_message}")
    USER_MEMORY[user_id] = previous[-MAX_HISTORY:]
    history_text = "\n".join(USER_MEMORY[user_id])

    prompt = (
        f"{ISLETME_BILGI}\n\n"
        f"Dost bilen gepleşik:\n{history_text}\n\n"
        f"Dostdan täze sorag:\n{user_message}\n\n"
        f"⚠️ Edebe laýyk we umumy maglumatlara jogap ber, dini/syýasy/ahlakdan daş temalardan gaç. "
        f"Jogap bereniňde köplenç 'Dost' diýip gürleş"
        f"Bilmedik, düşünmedik soragyň berilende 'Bagyşlaň, soragyňyza düşünmedim. Başga bir soragyňyz barmy?' diý. Emojiler ulan."
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

# Ana program
if __name__ == "__main__":
    print("Bot işleýär... Synap görüň!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Komut ve mesaj handler'lar
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
