import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# API anahtarlarını güvenlik için .env veya GitHub Secrets gibi yerde saklamanı öneririm!
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Gemini yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Kullanıcı hafızası ve geçmiş mesaj sayısı
USER_MEMORY = {}
MAX_HISTORY = 5

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
Programmany saýdymyzdan ýükläp bilersiňiz!
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

BLACKLIST = [
    "seks", "ölüm", "jeset", "syýasy", "porn", "adam öldür",
    "seni kim döretdi", "ýaradyjy"
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ['group', 'supergroup']:
        # Bot kullanıcı adı yoksa mesajı dikkate alma
        if not context.bot.username.lower() in update.message.text.lower():
            return

    user_id = update.effective_user.id
    user_message = update.message.text.replace(f"@{context.bot.username}", "").strip()

    if any(term in user_message.lower() for term in BLACKLIST):
        await update.message.reply_text("Bagyşla dos, bu tema boýunça kömek edip bilmerin.")
        return

    # Kullanıcı geçmişini al, yeni mesajı ekle
    previous = USER_MEMORY.get(user_id, [])
    previous.append(f"Kullanýjy: {user_message}")
    USER_MEMORY[user_id] = previous[-MAX_HISTORY:]

    # Geçmişi prompta ekle
    history_text = "\n".join(USER_MEMORY[user_id])

    prompt = (
        f"{ISLETME_BILGI}\n\n"
        f"Dost bilen öňki gepleşik:\n{history_text}\n\n"
        f"Dostdan täze sorag:\n{user_message}\n\n"
        f"⚠️ Edebe laýyk we umumy maglumatlara jogap ber, dini/syýasy/ahlakdan daş temalardan gaç. Jogap bereniňde köplenç 'Dost' diýip gürleş, bilmedik sorag berilende 'Bagyşlaň, soragyňyza düşünmedim. Başga bir soragyňyz barmy ?' diý. Emojiler ulanyp jogap berjek bol."
    )

    try:
        response = model.generate_content(prompt)
        bot_reply = response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Hata: {e}")
        bot_reply = "Bagyşlaň, näsazlyk ýüze çykdy."

    # Bot cevabını geçmişe ekle
    USER_MEMORY[user_id].append(f"Redzone AI: {bot_reply}")
    USER_MEMORY[user_id] = USER_MEMORY[user_id][-MAX_HISTORY:]

    await update.message.reply_text(bot_reply)

if __name__ == "__main__":
    print("Bot işleýär... Synap görüň!")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
