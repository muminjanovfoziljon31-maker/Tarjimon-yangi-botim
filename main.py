import os
import threading

import telebot
from telebot import types
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
import speech_recognition as sr
from pydub import AudioSegment
import pytesseract
from PIL import Image
from flask import Flask


# =========================
# BOT SOZLAMALARI
# =========================

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

if TOKEN == "YOUR_BOT_TOKEN":
    raise ValueError("BOT_TOKEN kiritilmagan!")

bot = telebot.TeleBot(TOKEN)

CHANNELS = [
    "@Matematikamilliysertifikat_F",
    "@afkari_dan"
]

user_languages = {}
all_users = set()
user_favorites = {}


# =========================
# MATNLAR
# =========================

TEXTS = {
    "uz": {
        "about": "ℹ️ Bot haqida",
        "help": "❓ Yordam",
        "change_lang": "⚙️ Tilni o'zgartirish",
        "favorites": "⭐ Sevimlilar",
        "about_text": (
            "🌐 <b>Tarjimon Bot</b>\n\n"
            "Matn, hujjat, ovozli xabar va rasmlardagi "
            "matnlarni tarjima qilishga yordam beradi."
        ),
        "help_text": (
            "❓ <b>Yordam</b>\n\n"
            "/start - Botni ishga tushirish\n\n"
            "Matn, hujjat, ovozli xabar yoki rasm yuboring."
        ),
        "select_new": "Marhamat, kerakli tilni tanlang:",
        "sub_required": (
            "⚠️ Xizmatdan foydalanish uchun avval "
            "quyidagi kanallarga obuna bo'ling:\n\n"
            "👉 @Matematikamilliysertifikat_F\n"
            "👉 @afkari_dan\n\n"
            "Obuna bo'lgach, xabaringizni qayta yuboring!"
        ),
        "fav_empty": "⭐ Sizda hozircha saqlangan sevimlilar yo'q.",
        "added_fav": "⭐ So'z sevimlilarga qo'shildi!"
    },

    "ru": {
        "about": "ℹ️ О боте",
        "help": "❓ Помощь",
        "change_lang": "⚙️ Изменить язык",
        "favorites": "⭐ Избранное",
        "about_text": (
            "🌐 <b>Переводчик Бот</b>\n\n"
            "Помогает переводить текст, документы, "
            "голосовые сообщения и изображения."
        ),
        "help_text": (
            "❓ <b>Помощь</b>\n\n"
            "/start - Запустить бота\n\n"
            "Отправьте текст, документ, голосовое сообщение "
            "или изображение."
        ),
        "select_new": "Пожалуйста, выберите язык:",
        "sub_required": (
            "⚠️ Чтобы пользоваться ботом, подпишитесь "
            "на наши каналы:\n\n"
            "👉 @Matematikamilliysertifikat_F\n"
            "👉 @afkari_dan\n\n"
            "После подписки отправьте сообщение снова!"
        ),
        "fav_empty": "⭐ У вас пока нет сохраненных слов.",
        "added_fav": "⭐ Слово добавлено в избранное!"
    },

    "en": {
        "about": "ℹ️ About bot",
        "help": "❓ Help",
        "change_lang": "⚙️ Change language",
        "favorites": "⭐ Favorites",
        "about_text": (
            "🌐 <b>Translator Bot</b>\n\n"
            "It helps translate text, documents, "
            "voice messages and images."
        ),
        "help_text": (
            "❓ <b>Help</b>\n\n"
            "/start - Start the bot\n\n"
            "Send me text, a document, voice message or image."
        ),
        "select_new": "Please choose a language:",
        "sub_required": (
            "⚠️ To use the service, please subscribe "
            "to our channels:\n\n"
            "👉 @Matematikamilliysertifikat_F\n"
            "👉 @afkari_dan\n\n"
            "After subscribing, send your message again!"
        ),
        "fav_empty": "⭐ You don't have any saved favorites yet.",
        "added_fav": "⭐ Word added to favorites!"
    }
}


def get_texts(chat_id):
    lang = user_languages.get(chat_id, "uz")
    return TEXTS.get(lang, TEXTS["uz"])


# =========================
# OBUNANI TEKSHIRISH
# =========================

def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status not in [
                "member",
                "administrator",
                "creator"
            ]:
                return False

        except Exception:
            # Agar kanal topilmasa yoki bot kanalga admin qilinmagan bo'lsa
            return False

    return True


# =========================
# MENYULAR
# =========================

def get_main_keyboard(chat_id):
    t = get_texts(chat_id)

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton(t["about"]),
        types.KeyboardButton(t["help"]),
        types.KeyboardButton(t["change_lang"]),
        types.KeyboardButton(t["favorites"])
    )

    return markup


def get_language_keyboard():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    markup.add(
        types.KeyboardButton("🇺🇿 O'zbekcha"),
        types.KeyboardButton("🇷🇺 Русский"),
        types.KeyboardButton("🇬🇧 English")
    )

    return markup


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id

    all_users.add(chat_id)
    user_languages.setdefault(chat_id, "uz")

    bot.send_message(
        chat_id,
        "Assalomu alaykum! 👋\n\n"
        "🌐 Tarjimon botga xush kelibsiz!\n\n"
        "Tilni tanlang yoki tarjima qilish uchun "
        "menga xabar yuboring.",
        reply_markup=get_main_keyboard(chat_id)
    )


# =========================
# TIL O'ZGARTIRISH
# =========================

@bot.message_handler(
    func=lambda message: message.text in [
        "🇺🇿 O'zbekcha",
        "🇷🇺 Русский",
        "🇬🇧 English"
    ]
)
def set_language(message):
    chat_id = message.chat.id

    if message.text == "🇺🇿 O'zbekcha":
        user_languages[chat_id] = "uz"

    elif message.text == "🇷🇺 Русский":
        user_languages[chat_id] = "ru"

    elif message.text == "🇬🇧 English":
        user_languages[chat_id] = "en"

    bot.send_message(
        chat_id,
        "✅ Til o'zgartirildi!",
        reply_markup=get_main_keyboard(chat_id)
    )


# =========================
# OVOZ VA AUDIO
# =========================

@bot.message_handler(content_types=["voice", "audio"])
def handle_voice_and_audio(message):
    chat_id = message.chat.id

    if not check_subscription(chat_id):
        bot.reply_to(
            message,
            get_texts(chat_id)["sub_required"]
        )
        return

    input_file = f"temp_{chat_id}.ogg"
    wav_file = f"temp_{chat_id}.wav"

    try:
        bot.reply_to(
            message,
            "🎙 Ovoz qabul qilindi, matnga aylantirilmoqda..."
        )

        if message.content_type == "voice":
            file_info = bot.get_file(message.voice.file_id)
        else:
            file_info = bot.get_file(message.audio.file_id)

        downloaded_file = bot.download_file(
            file_info.file_path
        )

        with open(input_file, "wb") as f:
            f.write(downloaded_file)

        sound = AudioSegment.from_file(input_file)
        sound.export(wav_file, format="wav")

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(
            audio_data,
            language="uz-UZ"
        )

        if not text.strip():
            bot.reply_to(
                message,
                "❌ Ovozdan matn topilmadi."
            )
            return

        lang = user_languages.get(chat_id, "uz")

        translated = GoogleTranslator(
            source="auto",
            target=lang
        ).translate(text)

        response = (
            f"🗣 <b>Eshitilgan matn:</b>\n{text}\n\n"
            f"🌐 <b>Tarjima:</b>\n{translated}"
        )

        bot.reply_to(
            message,
            response,
            parse_mode="HTML"
        )

    except sr.UnknownValueError:
        bot.reply_to(
            message,
            "❌ Ovozdagi gapni tushunib bo'lmadi."
        )

    except Exception as e:
        print("Audio error:", e)
        bot.reply_to(
            message,
            "❌ Ovozli xabarni qayta ishlashda xatolik yuz berdi."
        )

    finally:
        for file in [input_file, wav_file]:
            if os.path.exists(file):
                os.remove(file)


# =========================
# RASM
# =========================

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    chat_id = message.chat.id

    if not check_subscription(chat_id):
        bot.reply_to(
            message,
            get_texts(chat_id)["sub_required"]
        )
        return

    image_path = f"temp_{chat_id}.jpg"

    try:
        bot.reply_to(
            message,
            "🖼 Rasm qabul qilindi, matn o'qilmoqda..."
        )

        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)

        downloaded_file = bot.download_file(
            file_info.file_path
        )

        with open(image_path, "wb") as f:
            f.write(downloaded_file)

        img = Image.open(image_path)

        # Serverda faqat mavjud OCR tillaridan foydalanamiz
        extracted_text = pytesseract.image_to_string(
            img,
            lang="eng+rus"
        )

        if not extracted_text.strip():
            bot.reply_to(
                message,
                "❌ Rasmdan matn topilmadi."
            )
            return

        lang = user_languages.get(chat_id, "uz")

        translated = GoogleTranslator(
            source="auto",
            target=lang
        ).translate(extracted_text)

        response = (
            f"📄 <b>Topilgan matn:</b>\n"
            f"{extracted_text}\n\n"
            f"🌐 <b>Tarjima:</b>\n"
            f"{translated}"
        )

        bot.reply_to(
            message,
            response,
            parse_mode="HTML"
        )

    except Exception as e:
        print("Photo error:", e)
        bot.reply_to(
            message,
            "❌ Rasmni qayta ishlashda xatolik yuz berdi."
        )

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


# =========================
# HUJJATLAR
# =========================

@bot.message_handler(content_types=["document"])
def handle_document(message):
    chat_id = message.chat.id

    if not check_subscription(chat_id):
        bot.reply_to(
            message,
            get_texts(chat_id)["sub_required"]
        )
        return

    temp_file = f"temp_{chat_id}.docx"

    try:
        file_name = message.document.file_name.lower()

        if not (
            file_name.endswith(".txt")
            or file_name.endswith(".docx")
        ):
            bot.reply_to(
                message,
                "❌ Faqat .txt va .docx fayllar qabul qilinadi."
            )
            return

        file_info = bot.get_file(
            message.document.file_id
        )

        downloaded_file = bot.download_file(
            file_info.file_path
        )

        if file_name.endswith(".txt"):
            text_content = downloaded_file.decode(
                "utf-8",
                errors="ignore"
            )

        else:
            with open(temp_file, "wb") as f:
                f.write(downloaded_file)

            doc = Document(temp_file)

            text_content = "\n".join(
                p.text for p in doc.paragraphs
            )

        if not text_content.strip():
            bot.reply_to(
                message,
                "❌ Fayl bo'sh yoki o'qib bo'lmadi."
            )
            return

        lang = user_languages.get(chat_id, "uz")

        translated_text = GoogleTranslator(
            source="auto",
            target=lang
        ).translate(text_content)

        output_name = f"translated_{file_name}"

        if file_name.endswith(".txt"):

            with open(
                output_name,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(translated_text)

        else:
            new_doc = Document()

            for line in translated_text.split("\n"):
                new_doc.add_paragraph(line)

            new_doc.save(output_name)

        with open(output_name, "rb") as f:
            bot.send_document(
                chat_id,
                f,
                caption="📄 Mana tarjima qilingan hujjatingiz!"
            )

        if os.path.exists(output_name):
            os.remove(output_name)

    except Exception as e:
        print("Document error:", e)
        bot.reply_to(
            message,
            "❌ Hujjatni tarjima qilishda xatolik yuz berdi."
        )

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


# =========================
# MATN VA MENYU
# =========================

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if not message.text:
        return

    chat_id = message.chat.id

    all_users.add(chat_id)

    lang = user_languages.get(chat_id, "uz")
    t = TEXTS.get(lang, TEXTS["uz"])

    # ABOUT
    if message.text in [
        TEXTS["uz"]["about"],
        TEXTS["ru"]["about"],
        TEXTS["en"]["about"]
    ]:
        bot.send_message(
            chat_id,
            t["about_text"],
            parse_mode="HTML"
        )
        return

    # HELP
    if message.text in [
        TEXTS["uz"]["help"],
        TEXTS["ru"]["help"],
        TEXTS["en"]["help"]
    ]:
        bot.send_message(
            chat_id,
            t["help_text"],
            parse_mode="HTML"
        )
        return

    # CHANGE LANGUAGE
    if message.text in [
        TEXTS["uz"]["change_lang"],
        TEXTS["ru"]["change_lang"],
        TEXTS["en"]["change_lang"]
    ]:
        bot.send_message(
            chat_id,
            t["select_new"],
            reply_markup=get_language_keyboard()
        )
        return

    # FAVORITES
    if message.text in [
        TEXTS["uz"]["favorites"],
        TEXTS["ru"]["favorites"],
        TEXTS["en"]["favorites"]
    ]:
        favs = user_favorites.get(chat_id, [])

        if not favs:
            bot.send_message(
                chat_id,
                t["fav_empty"]
            )
        else:
            bot.send_message(
                chat_id,
                "⭐ <b>Sevimlilar:</b>\n\n"
                + "\n".join(favs),
                parse_mode="HTML"
            )
        return

    # OBUNA
    if not check_subscription(chat_id):
        bot.reply_to(
            message,
            t["sub_required"]
        )
        return

    # TARJIMA
    try:
        word = message.text.strip()

        if not word:
            return

        translated = GoogleTranslator(
            source="auto",
            target=lang
        ).translate(word)

        if len(word.split()) == 1:
            response_text = (
                f"📖 <b>So'z:</b> {word}\n\n"
                f"🌐 <b>Tarjima:</b> {translated}\n\n"
                "💡 So'z kontekstga qarab boshqa "
                "ma'nolarga ham ega bo'lishi mumkin."
            )
        else:
            response_text = (
                f"🌐 <b>Tarjima:</b>\n{translated}"
            )

        # Sevimliga qo'shish
        user_favorites.setdefault(chat_id, [])

        fav_item = f"{word} — {translated}"

        if fav_item not in user_favorites[chat_id]:
            user_favorites[chat_id].append(fav_item)

        # Ovoz
        tts_file = f"tts_{chat_id}.mp3"

        tts_lang = {
            "uz": "en",
            "ru": "ru",
            "en": "en"
        }.get(lang, "en")

        tts = gTTS(
            text=translated,
            lang=tts_lang
        )

        tts.save(tts_file)

        with open(tts_file, "rb") as audio:
            bot.send_voice(
                chat_id,
                audio,
                reply_to_message_id=message.message_id
            )

        if os.path.exists(tts_file):
            os.remove(tts_file)

        bot.reply_to(
            message,
            response_text,
            parse_mode="HTML"
        )

    except Exception as e:
        print("Text translation error:", e)

        bot.reply_to(
            message,
            "❌ Tarjima qilishda xatolik yuz berdi."
        )


# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Telegram bot ishlayapti!"


def run_server():
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )


def keep_alive():
    thread = threading.Thread(
        target=run_server,
        daemon=True
    )
    thread.start()


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    keep_alive()

    print("🤖 Bot ishga tushdi!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
)
