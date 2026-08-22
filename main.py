import telebot
from deep_translator import GoogleTranslator
from gTTS import gTTS
from docx import Document
import os
import speech_recognition as sr
from pydub import AudioSegment
import pytesseract
from PIL import Image
from flask import Flask
import threading

# --- BOT TOKENI (O'zingizning tokeningizni yozing) ---
TOKEN = "8759004216:AAEjvnt-PKLlbtgy8jZCpTyIfeyngCZ2-IU"
bot = telebot.TeleBot(TOKEN)

# Majburiy obuna qilinadigan kanallar ro'yxati
CHANNELS = ["@Matematikamilliysertifikat_F", "@afkari_dan"]

# Foydalanuvchilar tillari va xotira lug'atlari
user_languages = {}
all_users = set()
user_favorites = {}

# Har xil tillardagi menyu va bot matnlari
TEXTS = {
    "uz": {
        "about": "ℹ️ Bot haqida",
        "help": "❓ Yordam",
        "change_lang": "⚙️ Tilni o'zgartirish",
        "favorites": "⭐ Sevimlilar",
        "about_text": "🌐 <b>Tarjimon Bot</b> — Matnlar, hujjatlar (.docx/.txt), ovozli xabarlar, musiqalar va rasmlarni barcha ma'nolari bilan tarjima qiluvchi aqlli yordamchi bot.",
        "help_text": "Buyruqlar:\n/start - Botni ishga tushirish\n\nMenga matn, hujjat, ovozli xabar, musiqa yoki rasm yuboring, men uni tarjima qilib beraman!",
        "select_new": "Marhamat, kerakli tilni tanlang:",
        "sub_required": "⚠️ Xizmatdan foydalanish uchun avval quyidagi kanallarimizga obuna bo'ling:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nObuna bo'lgach, xabaringizni qayta yuboring!",
        "fav_empty": "⭐ Sizda hozircha saqlangan sevimlilar yo'q.",
        "added_fav": "⭐ So'z sevimlilarga qo'shildi!"
    },
    "ru": {
        "about": "ℹ️ О боте",
        "help": "❓ Помощь",
        "change_lang": "⚙️ Изменить язык",
        "favorites": "⭐ Избранное",
        "about_text": "🌐 <b>Переводчик Бот</b> — умный помощник для быстрого перевода текстов, документов (.docx/.txt), голосовых сообщений, музыки и картинок.",
        "help_text": "Команды:\n/start - Запустить бот\n\nПросто отправьте мне текст, документ, голосовое, музыку или картинку!",
        "select_new": "Пожалуйста, выберите язык:",
        "sub_required": "⚠️ Чтобы пользоваться ботом, подпишитесь на наши каналы:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nПосле подписки отправьте сообщение снова!",
        "fav_empty": "⭐ У вас пока нет сохраненных слов.",
        "added_fav": "⭐ Слово добавлено в избранное!"
    }
}

def get_texts(chat_id):
    lang = user_languages.get(chat_id, "uz")
    return TEXTS.get(lang, TEXTS["uz"])

# Kanallarning barchasiga obuna bo'lganligini tekshiruvchi funksiya
def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            pass # Agar bot kanalga qo'shilmagan bo'lsa xatolik bermasligi uchun
    return True

def get_language_keyboard(chat_id):
    t = get_texts(chat_id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton(t["about"]),
        telebot.types.KeyboardButton(t["help"]),
        telebot.types.KeyboardButton(t["change_lang"]),
        telebot.types.KeyboardButton(t["favorites"])
    )
    return markup

def get_lang_select_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        telebot.types.KeyboardButton("🇺🇿 O'zbekcha"),
        telebot.types.KeyboardButton("🇷🇺 Русский"),
        telebot.types.KeyboardButton("🇬🇧 English")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    all_users.add(chat_id)
    user_languages.setdefault(chat_id, "uz")
    
    markup = get_language_keyboard(chat_id)
    bot.send_message(chat_id, "Assalomu alaykum! Tarjimon botga xush kelibsiz. Tilni tanlang yoki tarjima uchun xabar yuboring:", reply_markup=markup)

# Tilni o'zgartirish tugmalari
@bot.message_handler(func=lambda message: message.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"])
def set_language(message):
    chat_id = message.chat.id
    if message.text == "🇺🇿 O'zbekcha":
        user_languages[chat_id] = "uz"
    elif message.text == "🇷🇺 Русский":
        user_languages[chat_id] = "ru"
    elif message.text == "🇬🇧 English":
        user_languages[chat_id] = "en"
    
    t = get_texts(chat_id)
    bot.reply_to(message, f"✅ Til o'zgartirildi: {message.text}", reply_markup=get_language_keyboard(chat_id))

# --- OVOZLI XABAR VA MUSIQANI QABUL QILISH ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice_and_audio(message):
    chat_id = message.chat.id
    if not check_subscription(chat_id):
        t = get_texts(chat_id)
        bot.reply_to(message, t["sub_required"])
        return

    try:
        bot.reply_to(message, "🎙 Ovozli xabar yoki musiqa qabul qilindi, matnga o'girilmoqda...")
        
        if message.content_type == 'voice':
            file_info = bot.get_file(message.voice.file_id)
        else:
            file_info = bot.get_file(message.audio.file_id)
            
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "temp_audio.ogg"
        with open(input_file, 'wb') as f:
            f.write(downloaded_file)
            
        wav_file = "temp_audio.wav"
        sound = AudioSegment.from_file(input_file)
        sound.export(wav_file, format="wav")
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="uz-UZ")
            
        os.remove(input_file)
        os.remove(wav_file)
        
        if not text.strip():
            bot.reply_to(message, "❌ Ovozdan matn topilmadi.")
            return

        lang = user_languages.get(chat_id, "uz")
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        
        response_text = f"🗣 <b>Eshitilgan matn:</b>\n{text}\n\n🌐 <b>Tarjima:</b>\n{translated}"
        bot.reply_to(message, response_text, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ovozli xabar yoki musiqani qayta ishlashda xatolik yuz berdi.")

# --- RASMNI QABUL QILISH VA TARJIMA QILISH ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if not check_subscription(chat_id):
        t = get_texts(chat_id)
        bot.reply_to(message, t["sub_required"])
        return

    try:
        bot.reply_to(message, "🖼 Rasm qabul qilindi, ichidagi matn o'qilmoqda...")
        
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = "temp_image.jpg"
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)
            
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img, lang='uz+rus+eng')
        
        os.remove(image_path)
        
        if not extracted_text.strip():
            bot.reply_to(message, "❌ Rasmdan matn topilmadi.")
            return
            
        lang = user_languages.get(chat_id, "uz")
        translated = GoogleTranslator(source='auto', target=lang).translate(extracted_text)
        
        response_text = f"📄 <b>Rasmdan topilgan matn:</b>\n{extracted_text}\n\n🌐 <b>Tarjima:</b>\n{translated}"
        bot.reply_to(message, response_text, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, "❌ Rasmni qayta ishlashda xatolik yuz berdi.")

# --- HUJJATLARNI QABUL QILISH (.docx, .txt) ---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    if not check_subscription(chat_id):
        t = get_texts(chat_id)
        bot.reply_to(message, t["sub_required"])
        return

    try:
        lang = user_languages.get(chat_id, "uz")
        
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
        
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(translated_text)
            
        with open(output_name, "rb") as f:
            bot.send_document(chat_id, f, caption="Mana sizning tarjima qilingan hujjatingiz 📄")
        os.remove(output_name)
        
    except Exception as e:
        bot.reply_to(message, "❌ Hujjatni tarjima qilishda xatolik yuz berdi.")

# --- MATNNI VA MENYULARNI QABUL QILISH ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    all_users.add(chat_id)
    lang = user_languages.get(chat_id, "uz")
    t = TEXTS.get(lang, TEXTS["uz"])

    if message.text in [TEXTS["uz"]["about"], TEXTS["ru"]["about"]]:
        bot.send_message(chat_id, t["about_text"], parse_mode="HTML")
    elif message.text in [TEXTS["uz"]["help"], TEXTS["ru"]["help"]]:
        bot.send_message(chat_id, t["help_text"], parse_mode="HTML")
    elif message.text in [TEXTS["uz"]["change_lang"], TEXTS["ru"]["change_lang"]]:
        bot.send_message(chat_id, t["select_new"], reply_markup=get_lang_select_keyboard())
    elif message.text in [TEXTS["uz"]["favorites"], TEXTS["ru"]["favorites"]]:
        favs = user_favorites.get(chat_id, [])
        if not favs:
            bot.send_message(chat_id, t["fav_empty"])
        else:
            bot.send_message(chat_id, "⭐ <b>Sizning sevimlilar ro'yxatingiz:</b>\n\n" + "\n".join(favs), parse_mode="HTML")
    else:
        try:
            word = message.text.strip()
            translated = GoogleTranslator(source='auto', target=lang).translate(word)
            
            if len(word.split()) == 1:
                response_text = f"📖 <b>So'z:</b> {word}\n\n🌐 <b>Asosiy tarjima:</b> {translated}\n\n💡 <i>(Eslatma: So'z kontekstga qarab boshqa ma'nolarga ham ega bo'lishi mumkin).</i>"
            else:
                response_text = f"🌐 <b>Tarjima:</b>\n{translated}"

            user_favorites.setdefault(chat_id, [])
            fav_item = f"{word} — {translated}"
            if fav_item not in user_favorites[chat_id]:
                user_favorites[chat_id].append(fav_item)

            tts = gTTS(text=translated, lang=lang if lang in ['en', 'ru', 'fr', 'de', 'es'] else 'en')
            tts.save("trans.mp3")
            with open("trans.mp3", "rb") as audio:
                bot.send_voice(chat_id, audio, reply_to_message_id=message.message_id)
            os.remove("trans.mp3")
            
            bot.reply_to(message, response_text, parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message, "❌ Xatolik yuz berdi / Error occurred")

# --- RENDER WEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()

print("Super Bot to'liq imkoniyatlar bilan ishga tushdi...")
bot.infinity_polling()
    
