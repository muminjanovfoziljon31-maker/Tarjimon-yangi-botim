import telebot
from deep_translator import GoogleTranslator
from docx import Document
from gtts import gTTS
import os

TOKEN = "8759004216:AAErGjowHh3eO_RgSzAl-plm_RBscs4JxKE"

bot = telebot.TeleBot(TOKEN)
user_languages = {}
all_users = set()
user_favorites = {}

dasturchi_ismi = "@Foziljon20l0"
ADMIN_ID = 123456789  # O'z Telegram ID raqamingizni yozing

TEXTS = {
    "uz": {
        "change_lang": "🌐 Tilni o'zgartirish",
        "favorites": "⭐ Sevimlilar",
        "help": "💡 Yordam",
        "about": "ℹ️ Bot haqida",
        "select_new": "Yangi tilni tanlang:",
        "help_text": (
            "💡 **Botdan qanday foydalaniladi?**\n\n"
            "1️⃣ **Tilni tanlash:** Botga kirgach, o'zingizga qulay tilni tanlang (keyinchalik 🌐 tugmasi orqali istalgan vaqtda o'zgartirishingiz mumkin).\n"
            "2️⃣ **Matn tarjimasi:** Menga istalgan aralash tildagi matnni yuboring, darhol tanlangan tilga tezkor tarjima qilib beraman.\n"
            "3️⃣ **Fayl tarjimasi:** `.txt` yoki `.docx` formatdagi hujjatlarni yuborsangiz, ularni ham to'liq tarjima qilib, qaytadan fayl ko'rinishida yuboraman.\n"
            "4️⃣ **Ovozli eshitish:** Har bir tarjima qilingan matn ostida ovozli talaffuz (`voice`) xabari ham birga keladi.\n"
            "5️⃣ **Sevimlilarga saqlash:**\n"
            "   • Biror matnni tarjima qilganimdan so'ng, xabar ostida **\"⭐ Sevimlilarga qo'shish\"** degan tugma paydo bo'ladi.\n"
            "   • Shu tugmani bir marta bossangiz, ushbu tarjima avtomatik ravishda saqlanadi.\n"
            "   • Kerakli vaqtda menyudagi **\"⭐ Sevimlilar\"** tugmasini bosib, barcha saqlangan tarjimalaringizni ko'rishingiz mumkin.\n"
            "6️⃣ **Inline rejim:** Istalgan chatda `@bot_username` deb yozib, botga kirmasdan turib ham tezkor tarjima qilishingiz mumkin."
        ),
        "about_text": (
            "🤖 **Super Tarjimon Botga xush kelibsiz!**\n\n"
            "Bu bot sizga quyidagi professional imkoniyatlarni taqdim etadi:\n"
            "• 🌐 **Matnlarni tarjima qilish:** Istalgan aralash yoki bitta tildagi matnlarni tanlangan tilga tezkor o'girish.\n"
            "• 📄 **Hujjatlar tarjimasi:** `.txt` va `.docx` formatdagi matnli fayllarni to'liq tarjima qilib yuborish.\n"
            "• 🎙 **Ovozli talaffuz:** Tarjima qilingan matnni ovozli xabar (`voice`) shaklida eshitish.\n"
            "• ⭐ **Sevimlilar:** Muhim tarjimalaringizni saqlab qo'yish va qayta ko'rish.\n"
            "• ⚡ **Inline rejim:** Boshqa chatlarda ham to'g'ridan-to'g'ri foydalanish.\n\n"
            f"👨‍💻 **Dasturchi:** {dasturchi_ismi} 🚀"
        ),
        "saved": "✅ Til saqlandi! Menga matn, fayl yuboring yoki so'z yozing.",
        "translation": "<b>Tarjima:</b>",
        "file_caption": "📄 Tarjima qilingan hujjat:",
        "added_fav": "⭐ Tarjima sevimlilarga qo'shildi!"
    },
    "ru": {
        "change_lang": "🌐 Изменить язык",
        "favorites": "⭐ Избранное",
        "help": "💡 Помощь",
        "about": "ℹ️ О боте",
        "select_new": "Выберите новый язык:",
        "help_text": "💡 Отправьте текст или файл для перевода.",
        "about_text": f"🤖 Супер бот-переводчик.\nРазработчик: {dasturchi_ismi} 🚀",
        "saved": "✅ Язык сохранен!",
        "translation": "<b>Перевод:</b>",
        "file_caption": "📄 Переведенный документ:",
        "added_fav": "⭐ Добавлено в избранное!"
    },
    "en": {
        "change_lang": "🌐 Change Language",
        "favorites": "⭐ Favorites",
        "help": "💡 Help",
        "about": "ℹ️ About Bot",
        "select_new": "Choose a new language:",
        "help_text": "💡 Send text or a file to translate.",
        "about_text": f"🤖 Super Translator Bot.\nDeveloper: {dasturchi_ismi} 🚀",
        "saved": "✅ Language saved!",
        "translation": "<b>Translation:</b>",
        "file_caption": "📄 Translated document:",
        "added_fav": "⭐ Added to favorites!"
    },
    "tr": {
        "change_lang": "🌐 Dili Değiştir",
        "favorites": "⭐ Favoriler",
        "help": "💡 Yardım",
        "about": "ℹ️ Bot Hakkında",
        "select_new": "Yeni bir dil seçin:",
        "help_text": "💡 Çeviri için metin veya dosya gönderin.",
        "about_text": f"🤖 Süper Çeviri Botu.\nGeliştirici: {dasturchi_ismi} 🚀",
        "saved": "✅ Dil kaydedildi!",
        "translation": "<b>Çeviri:</b>",
        "file_caption": "📄 Çevrilen belge:",
        "added_fav": "⭐ Favorilere eklendi!"
    },
    "ko": {
        "change_lang": "🌐 언어 변경",
        "favorites": "⭐ 즐겨찾기",
        "help": "💡 도움말",
        "about": "ℹ️ 봇 정보",
        "select_new": "새 언어를 선택하세요:",
        "help_text": "💡 번역할 텍스트나 파일을 보내주세요.",
        "about_text": f"🤖 슈퍼 번역 봇.\n개발자: {dasturchi_ismi} 🚀",
        "saved": "✅ 언어가 저장되었습니다!",
        "translation": "<b>번역:</b>",
        "file_caption": "📄 번역된 문서:",
        "added_fav": "⭐ 즐겨찾기에 추가되었습니다!"
    },
    "zh-CN": {
        "change_lang": "🌐 更改语言",
        "favorites": "⭐ 收藏夹",
        "help": "💡 帮助",
        "about": "ℹ️ 关于机器",
        "select_new": "请选择新语言：",
        "help_text": "💡 发送文本或文件进行翻译。",
        "about_text": f"🤖 超级翻译机器人。\n开发者：{dasturchi_ismi} 🚀",
        "saved": "✅ 语言保存成功！",
        "translation": "<b>翻译：</b>",
        "file_caption": "📄 翻译后的文档：",
        "added_fav": "⭐ 已添加到收藏夹！"
    },
    "es": {
        "change_lang": "🌐 Cambiar idioma",
        "favorites": "⭐ Favoritos",
        "help": "💡 Ayuda",
        "about": "ℹ️ Acerca del bot",
        "select_new": "Elija un nuevo idioma:",
        "help_text": "💡 Envía texto o archivo para traducir.",
        "about_text": f"🤖 Súper bot de traducción.\nDesarrollador: {dasturchi_ismi} 🚀",
        "saved": "✅ ¡Idioma guardado!",
        "translation": "<b>Traducción:</b>",
        "file_caption": "📄 Documento traducido:",
        "added_fav": "⭐ ¡Añadido a favoritos!"
    },
    "de": {
        "change_lang": "🌐 Sprache ändern",
        "favorites": "⭐ Favoriten",
        "help": "💡 Hilfe",
        "about": "ℹ️ Über den Bot",
        "select_new": "Wählen Sie eine neue Sprache:",
        "help_text": "💡 Senden Sie Text oder Datei zur Übersetzung.",
        "about_text": f"🤖 Super Übersetzer-Bot.\nEntwickler: {dasturchi_ismi} 🚀",
        "saved": "✅ Sprache gespeichert!",
        "translation": "<b>Übersetzung:</b>",
        "file_caption": "📄 Übersetztes Dokument:",
        "added_fav": "⭐ Zu Favoriten hinzugefügt!"
    },
    "ar": {
        "change_lang": "🌐 تغيير اللغة",
        "favorites": "⭐ المفضلة",
        "help": "💡 المساعدة",
        "about": "ℹ️ حول البوت",
        "select_new": "اختر لغة جديدة:",
        "help_text": "💡 أرسل نصا أو ملفا للترجمة.",
        "about_text": f"🤖 بوت الترجمة الخارق.\nالمطور: {dasturchi_ismi} 🚀",
        "saved": "✅ تم حفظ اللغة!",
        "translation": "<b>الترجمة:</b>",
        "file_caption": "📄 المستند المترجم:",
        "added_fav": "⭐ تمت الإضافة إلى المفضلة!"
    },
    "fr": {
        "change_lang": "🌐 Changer de langue",
        "favorites": "⭐ Favoris",
        "help": "💡 Aide",
        "about": "ℹ️ À propos",
        "select_new": "Choisissez une nouvelle langue :",
        "help_text": "💡 Envoyez un texte ou un fichier à traduire.",
        "about_text": f"🤖 Super bot de traduction.\nDéveloppeur : {dasturchi_ismi} 🚀",
        "saved": "✅ Langue enregistrée !",
        "translation": "<b>Traduction :</b>",
        "file_caption": "📄 Document traduit :",
        "added_fav": "⭐ Ajouté aux favoris !"
    }
}

def get_language_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="uz"),
        telebot.types.InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
        telebot.types.InlineKeyboardButton("🇬🇧 English", callback_data="en"),
        telebot.types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="tr"),
        telebot.types.InlineKeyboardButton("🇰🇷 한국어", callback_data="ko"),
        telebot.types.InlineKeyboardButton("🇨🇳 中文", callback_data="zh-CN"),
        telebot.types.InlineKeyboardButton("🇪🇸 Español", callback_data="es"),
        telebot.types.InlineKeyboardButton("🇩🇪 Deutsch", callback_data="de"),
        telebot.types.InlineKeyboardButton("🇸🇦 العربية", callback_data="ar"),
        telebot.types.InlineKeyboardButton("🇫🇷 Français", callback_data="fr")
    )
    return markup

def get_main_menu(lang):
    t = TEXTS.get(lang, TEXTS["uz"])
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(t["change_lang"], t["favorites"])
    markup.row(t["help"], t["about"])
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    all_users.add(message.chat.id)
    text = "Salom! Tilni tanlang / Выберите язык / Choose language / اختر اللغة:"
    bot.send_message(message.chat.id, text, reply_markup=get_language_keyboard())

@bot.message_handler(commands=['stats'])
def show_stats(message):
    bot.reply_to(message, f"📊 Jami foydalanuvchilar: {len(all_users)} ta")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id != ADMIN_ID:
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "Yuborish uchun matn kiriting!")
        return
    count = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 <b>E'lon:</b>\n\n{text}", parse_mode="HTML")
            count += 1
        except:
            pass
    bot.reply_to(message, f"✅ Xabar {count} ta foydalanuvchiga yuborildi.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if data.startswith("fav_"):
        text_to_fav = data.replace("fav_", "")
        if chat_id not in user_favorites:
            user_favorites[chat_id] = []
        if text_to_fav not in user_favorites[chat_id]:
            user_favorites[chat_id].append(text_to_fav)
        lang = user_languages.get(chat_id, "uz")
        t = TEXTS.get(lang, TEXTS["uz"])
        bot.answer_callback_query(call.id, t["added_fav"])
        return

    lang_code = data
    user_languages[chat_id] = lang_code
    t = TEXTS.get(lang_code, TEXTS["uz"])
    
    bot.answer_callback_query(call.id, "OK")
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=t["saved"])
    bot.send_message(chat_id, "👇", reply_markup=get_main_menu(lang_code))

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    all_users.add(chat_id)
    lang = user_languages.get(chat_id, "uz")
    t = TEXTS.get(lang, TEXTS["uz"])
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name
        
        text_content = ""
        if file_name.endswith('.txt'):
            text_content = downloaded_file.decode('utf-8')
        elif file_name.endswith('.docx'):
            with open("temp.docx", "wb") as f:
                f.write(downloaded_file)
            doc = Document("temp.docx")
            text_content = "\n".join([p.text for p in doc.paragraphs])
            os.remove("temp.docx")
        
        if not text_content.strip():
            bot.reply_to(message, "❌ Fayl bo'sh yoki o'qib bo'lmadi.")
            return

        translated_text = GoogleTranslator(source='auto', target=lang).translate(text_content)
        
        output_name = f"translated_{file_name}"
        if file_name.endswith('.docx'):
            out_doc = Document()
            out_doc.add_paragraph(translated_text)
            out_doc.save(output_name)
        else:
            with open(output_name, "w", encoding="utf-8") as f:
                f.write(translated_text)
                
        with open(output_name, "rb") as f:
            bot.send_document(chat_id, f, caption=t["file_caption"])
        os.remove(output_name)
        
    except Exception as e:
        bot.reply_to(message, "❌ Faylni tarjima qilishda xatolik yuz berdi.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    all_users.add(chat_id)
    lang = user_languages.get(chat_id, "uz")
    t = TEXTS.get(lang, TEXTS["uz"])
    
    if message.text in [TEXTS[l]["about"] for l in TEXTS]:
        bot.send_message(chat_id, t["about_text"], parse_mode="HTML")
    elif message.text in [TEXTS[l]["help"] for l in TEXTS]:
        bot.send_message(chat_id, t["help_text"], parse_mode="HTML")
    elif message.text in [TEXTS[l]["change_lang"] for l in TEXTS]:
        bot.send_message(chat_id, t["select_new"], reply_markup=get_language_keyboard())
    elif message.text in [TEXTS[l]["favorites"] for l in TEXTS]:
        favs = user_favorites.get(chat_id, [])
        if not favs:
            bot.send_message(chat_id, "⭐ Sizda hali saqlangan sevimlilar yo'q.")
        else:
            fav_text = "⭐ <b>Sizning saqlangan tarjimalaringiz:</b>\n\n" + "\n".join([f"- {f}" for f in favs[-10:]])
            bot.send_message(chat_id, fav_text, parse_mode="HTML")
    else:
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(message.text)
            
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("⭐ Sevimlilarga qo'shish", callback_data=f"fav_{translated[:30]}"))
            
            tts = gTTS(text=translated, lang=lang if lang in ['en', 'ru', 'fr', 'de', 'es'] else 'en')
            tts.save("trans.mp3")
            with open("trans.mp3", "rb") as audio:
                bot.send_voice(chat_id, audio, reply_to_message_id=message.message_id)
            os.remove("trans.mp3")

            bot.reply_to(message, f"{t['translation']}\n{translated}", parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            bot.reply_to(message, "Xatolik yuz berdi / Error occurred")

@bot.inline_handler(func=lambda query: True)
def inline_query(query):
    text = query.query
    if not text:
        return
    try:
        translated = GoogleTranslator(source='auto', target='uz').translate(text)
        results = [
            telebot.types.InlineQueryResultArticle(
                id='1',
                title="O'zbek tiliga tarjima",
                description=translated,
                input_message_content=telebot.types.InputTextMessageContent(f"<b>Tarjima:</b>\n{translated}", parse_mode="HTML")
            )
        ]
        bot.answer_inline_query(query.id, results, cache_time=1)
    except:
        pass

print("Super Bot to'liq imkoniyatlar bilan ishga tushdi...")
bot.infinity_polling(none_stop=True, interval=0)
