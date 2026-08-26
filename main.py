import os
import tempfile
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


# =========================================================
# BOT SOZLAMALARI
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN kiritilmagan!")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# =========================================================
# KANALLAR
# =========================================================

CHANNELS = [
    "@Matematikamilliysertifikat_F",
    "@afkari_dan"
]


# =========================================================
# FOYDALANUVCHI MA'LUMOTLARI
# =========================================================

user_languages = {}
all_users = set()
user_favorites = {}


# =========================================================
# 10 TA TIL
# =========================================================

LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "ko": "🇰🇷 한국어",
    "tr": "🇹🇷 Türkçe",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "zh-CN": "🇨🇳 中文"
}

TTS_LANGUAGES = {
    "uz": "uz",
    "en": "en",
    "ru": "ru",
    "ar": "ar",
    "ko": "ko",
    "tr": "tr",
    "de": "de",
    "fr": "fr",
    "es": "es",
    "zh-CN": "zh-CN"
}


# =========================================================
# MATNLAR
# =========================================================

TEXTS = {
    "uz": {
        "about": "🤖 Bot haqida",
        "help": "💡 Yordam",
        "change_lang": "🌐 Tilni o'zgartirish",
        "favorites": "⭐ Sevimlilar",
        "select_new": "🌐 Kerakli tilni tanlang:",
        "language_changed": "✅ Til muvaffaqiyatli o'zgartirildi!",
        "favorite_add": "⭐ Sevimlilarga qo'shish",
        "favorite_added": "⭐ Tarjima sevimlilarga qo'shildi!",
        "favorite_exists": "⭐ Bu tarjima allaqachon sevimlilarda!",
        "fav_empty": "⭐ Sizda saqlangan tarjimalar yo'q.",
        "favorites_title": "⭐ <b>Sevimlilar:</b>",
        "sub_required": (
            "⚠️ Botdan foydalanish uchun avval quyidagi kanallarga "
            "obuna bo'ling:\n\n"
            "👉 @Matematikamilliysertifikat_F\n"
            "👉 @afkari_dan\n\n"
            "Obuna bo'lgach, xabaringizni qayta yuboring."
        ),
        "start": (
            "🇺🇿 Assalomu alaykum! 👋\n\n"
            "🌐 Super Tarjimon Botga xush kelibsiz!\n\n"
            "Tilni tanlang yoki tarjima qilish uchun xabar yuboring."
        ),
        "about_text": (
            "🤖 <b>Super Translator Bot</b>\n\n"
            "🌐 Matn tarjimasi\n"
            "📄 TXT va DOCX tarjimasi\n"
            "🎙 Ovozli xabar tarjimasi\n"
            "🔊 Tarjimani ovozli eshitish\n"
            "🖼 Rasmdagi matnni tarjima qilish\n"
            "⭐ Sevimlilarga saqlash\n\n"
            "👨‍💻 Dasturchi: @Foziljon20l0"
        ),
        "help_text": (
            "💡 <b>Botdan foydalanish</b>\n\n"
            "1️⃣ Tilni tanlang.\n"
            "2️⃣ Matn yuboring.\n"
            "3️⃣ TXT yoki DOCX fayl yuboring.\n"
            "4️⃣ Ovozli xabar yuboring.\n"
            "5️⃣ Matnli rasm yuboring.\n"
            "6️⃣ ⭐ tugmasi orqali tarjimani saqlang.\n"
            "7️⃣ 🌐 orqali tilni almashtiring."
        )
    },

    "en": {
        "about": "🤖 About bot",
        "help": "💡 Help",
        "change_lang": "🌐 Change language",
        "favorites": "⭐ Favorites",
        "select_new": "🌐 Choose your language:",
        "language_changed": "✅ Language changed!",
        "favorite_add": "⭐ Add to favorites",
        "favorite_added": "⭐ Added to favorites!",
        "favorite_exists": "⭐ Already in favorites!",
        "fav_empty": "⭐ No saved translations.",
        "favorites_title": "⭐ <b>Favorites:</b>",
        "sub_required": "⚠️ Please subscribe to:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nThen send your message again.",
        "start": "🇬🇧 Hello! 👋\n\n🌐 Welcome to Super Translator Bot!\n\nChoose a language or send a message.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 Text translation\n📄 TXT and DOCX translation\n🎙 Voice translation\n🔊 Text-to-speech\n🖼 Image translation\n⭐ Favorites\n\n👨‍💻 Developer: @Foziljon20l0",
        "help_text": "💡 <b>How to use</b>\n\n1️⃣ Choose a language.\n2️⃣ Send text.\n3️⃣ Send TXT or DOCX.\n4️⃣ Send voice.\n5️⃣ Send an image with text.\n6️⃣ Save translations with ⭐.\n7️⃣ Change language with 🌐."
    },

    "ru": {
        "about": "🤖 О боте",
        "help": "💡 Помощь",
        "change_lang": "🌐 Изменить язык",
        "favorites": "⭐ Избранное",
        "select_new": "🌐 Выберите язык:",
        "language_changed": "✅ Язык изменён!",
        "favorite_add": "⭐ Добавить в избранное",
        "favorite_added": "⭐ Добавлено в избранное!",
        "favorite_exists": "⭐ Уже в избранном!",
        "fav_empty": "⭐ Нет сохранённых переводов.",
        "favorites_title": "⭐ <b>Избранное:</b>",
        "sub_required": "⚠️ Сначала подпишитесь:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nПосле этого отправьте сообщение снова.",
        "start": "🇷🇺 Здравствуйте! 👋\n\n🌐 Добро пожаловать в переводчик!\n\nВыберите язык или отправьте сообщение.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 Перевод текста\n📄 Перевод TXT и DOCX\n🎙 Перевод голоса\n🔊 Озвучивание\n🖼 Перевод изображений\n⭐ Избранное\n\n👨‍💻 Разработчик: @Foziljon20l0",
        "help_text": "💡 <b>Как пользоваться</b>\n\n1️⃣ Выберите язык.\n2️⃣ Отправьте текст.\n3️⃣ Отправьте TXT или DOCX.\n4️⃣ Отправьте голос.\n5️⃣ Отправьте изображение с текстом.\n6️⃣ Сохраняйте перевод через ⭐.\n7️⃣ Меняйте язык через 🌐."
    },

    "ar": {
        "about": "🤖 حول البوت",
        "help": "💡 المساعدة",
        "change_lang": "🌐 تغيير اللغة",
        "favorites": "⭐ المفضلة",
        "select_new": "🌐 اختر اللغة:",
        "language_changed": "✅ تم تغيير اللغة!",
        "favorite_add": "⭐ إضافة إلى المفضلة",
        "favorite_added": "⭐ تمت الإضافة!",
        "favorite_exists": "⭐ موجود بالفعل!",
        "fav_empty": "⭐ لا توجد ترجمات محفوظة.",
        "favorites_title": "⭐ <b>المفضلة:</b>",
        "sub_required": "⚠️ يرجى الاشتراك أولاً:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nثم أرسل رسالتك مرة أخرى.",
        "start": "🇸🇦 مرحباً! 👋\n\n🌐 أهلاً بك في بوت الترجمة!\n\nاختر لغة أو أرسل رسالة.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 ترجمة النصوص\n📄 ترجمة TXT و DOCX\n🎙 ترجمة الصوت\n🔊 النطق الصوتي\n🖼 ترجمة الصور\n⭐ المفضلة\n\n👨‍💻 المطور: @Foziljon20l0",
        "help_text": "💡 <b>طريقة الاستخدام</b>\n\n1️⃣ اختر اللغة.\n2️⃣ أرسل النص.\n3️⃣ أرسل TXT أو DOCX.\n4️⃣ أرسل رسالة صوتية.\n5️⃣ أرسل صورة تحتوي على نص.\n6️⃣ احفظ الترجمة عبر ⭐.\n7️⃣ غيّر اللغة عبر 🌐."
    },

    "ko": {
        "about": "🤖 봇 정보",
        "help": "💡 도움말",
        "change_lang": "🌐 언어 변경",
        "favorites": "⭐ 즐겨찾기",
        "select_new": "🌐 언어를 선택하세요:",
        "language_changed": "✅ 언어가 변경되었습니다!",
        "favorite_add": "⭐ 즐겨찾기에 추가",
        "favorite_added": "⭐ 즐겨찾기에 추가되었습니다!",
        "favorite_exists": "⭐ 이미 저장되어 있습니다!",
        "fav_empty": "⭐ 저장된 번역이 없습니다.",
        "favorites_title": "⭐ <b>즐겨찾기:</b>",
        "sub_required": "⚠️ 먼저 다음 채널을 구독하세요:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\n그 후 메시지를 다시 보내세요.",
        "start": "🇰🇷 안녕하세요! 👋\n\n🌐 번역 봇에 오신 것을 환영합니다!\n\n언어를 선택하거나 메시지를 보내세요.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 텍스트 번역\n📄 TXT 및 DOCX 번역\n🎙 음성 번역\n🔊 음성 출력\n🖼 이미지 번역\n⭐ 즐겨찾기\n\n👨‍💻 개발자: @Foziljon20l0",
        "help_text": "💡 <b>사용 방법</b>\n\n1️⃣ 언어 선택\n2️⃣ 텍스트 전송\n3️⃣ TXT 또는 DOCX 전송\n4️⃣ 음성 전송\n5️⃣ 텍스트가 있는 이미지 전송\n6️⃣ ⭐ 저장\n7️⃣ 🌐 언어 변경"
    },

    "tr": {
        "about": "🤖 Bot hakkında",
        "help": "💡 Yardım",
        "change_lang": "🌐 Dili değiştir",
        "favorites": "⭐ Favoriler",
        "select_new": "🌐 Dil seçin:",
        "language_changed": "✅ Dil değiştirildi!",
        "favorite_add": "⭐ Favorilere ekle",
        "favorite_added": "⭐ Favorilere eklendi!",
        "favorite_exists": "⭐ Zaten favorilerde!",
        "fav_empty": "⭐ Kayıtlı çeviri yok.",
        "favorites_title": "⭐ <b>Favoriler:</b>",
        "sub_required": "⚠️ Önce kanallara abone olun:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nSonra mesajınızı tekrar gönderin.",
        "start": "🇹🇷 Merhaba! 👋\n\n🌐 Çeviri Botuna hoş geldiniz!\n\nDil seçin veya mesaj gönderin.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 Metin çevirisi\n📄 TXT ve DOCX\n🎙 Ses çevirisi\n🔊 Sesli okuma\n🖼 Görsel çevirisi\n⭐ Favoriler\n\n👨‍💻 Geliştirici: @Foziljon20l0",
        "help_text": "💡 <b>Kullanım</b>\n\n1️⃣ Dil seçin.\n2️⃣ Metin gönderin.\n3️⃣ TXT veya DOCX gönderin.\n4️⃣ Ses gönderin.\n5️⃣ Metinli resim gönderin.\n6️⃣ ⭐ ile kaydedin.\n7️⃣ 🌐 ile dili değiştirin."
    },

    "de": {
        "about": "🤖 Über den Bot",
        "help": "💡 Hilfe",
        "change_lang": "🌐 Sprache ändern",
        "favorites": "⭐ Favoriten",
        "select_new": "🌐 Sprache auswählen:",
        "language_changed": "✅ Sprache geändert!",
        "favorite_add": "⭐ Zu Favoriten hinzufügen",
        "favorite_added": "⭐ Zu Favoriten hinzugefügt!",
        "favorite_exists": "⭐ Bereits gespeichert!",
        "fav_empty": "⭐ Keine gespeicherten Übersetzungen.",
        "favorites_title": "⭐ <b>Favoriten:</b>",
        "sub_required": "⚠️ Bitte abonnieren Sie zuerst:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nSenden Sie danach die Nachricht erneut.",
        "start": "🇩🇪 Hallo! 👋\n\n🌐 Willkommen beim Übersetzungsbot!\n\nWählen Sie eine Sprache oder senden Sie eine Nachricht.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 Textübersetzung\n📄 TXT und DOCX\n🎙 Sprachübersetzung\n🔊 Sprachausgabe\n🖼 Bildübersetzung\n⭐ Favoriten\n\n👨‍💻 Entwickler: @Foziljon20l0",
        "help_text": "💡 <b>Verwendung</b>\n\n1️⃣ Sprache auswählen.\n2️⃣ Text senden.\n3️⃣ TXT oder DOCX senden.\n4️⃣ Sprachnachricht senden.\n5️⃣ Bild mit Text senden.\n6️⃣ Mit ⭐ speichern.\n7️⃣ Sprache mit 🌐 ändern."
    },

    "fr": {
        "about": "🤖 À propos",
        "help": "💡 Aide",
        "change_lang": "🌐 Changer de langue",
        "favorites": "⭐ Favoris",
        "select_new": "🌐 Choisissez une langue:",
        "language_changed": "✅ Langue changée!",
        "favorite_add": "⭐ Ajouter aux favoris",
        "favorite_added": "⭐ Ajouté aux favoris!",
        "favorite_exists": "⭐ Déjà dans les favoris!",
        "fav_empty": "⭐ Aucun favori.",
        "favorites_title": "⭐ <b>Favoris:</b>",
        "sub_required": "⚠️ Veuillez d'abord vous abonner:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nPuis envoyez votre message.",
        "start": "🇫🇷 Bonjour! 👋\n\n🌐 Bienvenue dans le bot de traduction!\n\nChoisissez une langue ou envoyez un message.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 Traduction de texte\n📄 TXT et DOCX\n🎙 Traduction vocale\n🔊 Lecture audio\n🖼 Traduction d'images\n⭐ Favoris\n\n👨‍💻 Développeur: @Foziljon20l0",
        "help_text": "💡 <b>Utilisation</b>\n\n1️⃣ Choisissez une langue.\n2️⃣ Envoyez un texte.\n3️⃣ Envoyez TXT ou DOCX.\n4️⃣ Envoyez un message vocal.\n5️⃣ Envoyez une image avec du texte.\n6️⃣ Enregistrez avec ⭐.\n7️⃣ Changez de langue avec 🌐."
    },

    "es": {
        "about": "🤖 Sobre el bot",
        "help": "💡 Ayuda",
        "change_lang": "🌐 Cambiar idioma",
        "favorites": "⭐ Favoritos",
        "select_new": "🌐 Elige un idioma:",
        "language_changed": "✅ ¡Idioma cambiado!",
        "favorite_add": "⭐ Añadir a favoritos",
        "favorite_added": "⭐ ¡Añadido a favoritos!",
        "favorite_exists": "⭐ ¡Ya está en favoritos!",
        "fav_empty": "⭐ No hay traducciones guardadas.",
        "favorites_title": "⭐ <b>Favoritos:</b>",
        "sub_required": "⚠️ Primero suscríbete a:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\nDespués envía el mensaje otra vez.",
        "start": "🇪🇸 ¡Hola! 👋\n\n🌐 ¡Bienvenido al bot traductor!\n\nElige un idioma o envía un mensaje.",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 Traducción de texto\n📄 TXT y DOCX\n🎙 Traducción de voz\n🔊 Texto a voz\n🖼 Traducción de imágenes\n⭐ Favoritos\n\n👨‍💻 Desarrollador: @Foziljon20l0",
        "help_text": "💡 <b>Cómo usarlo</b>\n\n1️⃣ Elige idioma.\n2️⃣ Envía texto.\n3️⃣ Envía TXT o DOCX.\n4️⃣ Envía voz.\n5️⃣ Envía una imagen con texto.\n6️⃣ Guarda con ⭐.\n7️⃣ Cambia idioma con 🌐."
    },

    "zh-CN": {
        "about": "🤖 关于机器人",
        "help": "💡 帮助",
        "change_lang": "🌐 更改语言",
        "favorites": "⭐ 收藏",
        "select_new": "🌐 请选择语言:",
        "language_changed": "✅ 语言已更改!",
        "favorite_add": "⭐ 添加到收藏",
        "favorite_added": "⭐ 已添加到收藏!",
        "favorite_exists": "⭐ 已经收藏!",
        "fav_empty": "⭐ 没有保存的翻译。",
        "favorites_title": "⭐ <b>收藏:</b>",
        "sub_required": "⚠️ 请先订阅以下频道:\n\n👉 @Matematikamilliysertifikat_F\n👉 @afkari_dan\n\n订阅后再次发送消息。",
        "start": "🇨🇳 你好! 👋\n\n🌐 欢迎使用翻译机器人!\n\n请选择语言或发送消息。",
        "about_text": "🤖 <b>Super Translator Bot</b>\n\n🌐 文本翻译\n📄 TXT 和 DOCX 翻译\n🎙 语音翻译\n🔊 语音朗读\n🖼 图片翻译\n⭐ 收藏\n\n👨‍💻 开发者: @Foziljon20l0",
        "help_text": "💡 <b>使用方法</b>\n\n1️⃣ 选择语言。\n2️⃣ 发送文本。\n3️⃣ 发送 TXT 或 DOCX。\n4️⃣ 发送语音。\n5️⃣ 发送带文字的图片。\n6️⃣ 使用 ⭐ 收藏。\n7️⃣ 使用 🌐 更改语言。"
    }
}


# =========================================================
# YORDAMCHI FUNKSIYALAR
# =========================================================

def get_lang(user_id):
    if user_id not in user_languages:
        user_languages[user_id] = "uz"
    return user_languages[user_id]


def txt(user_id, key):
    lang = get_lang(user_id)
    return TEXTS.get(lang, TEXTS["uz"]).get(key, TEXTS["uz"].get(key, ""))


def add_user(user_id):
    all_users.add(user_id)
    get_lang(user_id)


# =========================================================
# OBUNA TEKSHIRISH
# =========================================================

def check_subscription(user_id):
    """
    Foydalanuvchi ikkala kanalga ham obuna bo'lganini tekshiradi.
    Bot kanallarda admin bo'lishi kerak.
    """

    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:
            print("Obuna tekshirish xatosi:", channel, e)

            # Kanalni tekshirib bo'lmasa, foydalanuvchini o'tkazmaymiz.
            return False

    return True


def subscription_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 Matematikamilliysertifikat_F",
            url="https://t.me/Matematikamilliysertifikat_F"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 afkari_dan",
            url="https://t.me/afkari_dan"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_sub"
        )
    )

    return keyboard


def require_subscription(message):
    add_user(message.from_user.id)

    if check_subscription(message.from_user.id):
        return True

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "sub_required"),
        reply_markup=subscription_keyboard()
    )

    return False


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_keyboard(user_id):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add(
        types.KeyboardButton(txt(user_id, "about")),
        types.KeyboardButton(txt(user_id, "help"))
    )

    keyboard.add(
        types.KeyboardButton(txt(user_id, "change_lang")),
        types.KeyboardButton(txt(user_id, "favorites"))
    )

    return keyboard


# =========================================================
# TIL TANLASH
# =========================================================

def language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = []

    for code, name in LANGUAGES.items():
        buttons.append(
            types.InlineKeyboardButton(
                name,
                callback_data=f"lang:{code}"
            )
        )

    keyboard.add(*buttons)

    return keyboard


# =========================================================
# TARJIMA
# =========================================================

def translate_text(text, target):
    if not text or not text.strip():
        return ""

    try:
        translator = GoogleTranslator(
            source="auto",
            target=target
        )

        return translator.translate(text)

    except Exception as e:
        print("Translation error:", e)
        return "❌ Tarjima qilishda xatolik yuz berdi."


# =========================================================
# FAVORITES
# =========================================================

def favorite_keyboard(user_id, translation):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            txt(user_id, "favorite_add"),
            callback_data="fav:add"
        )
    )

    return keyboard


def save_favorite(user_id, text):
    if user_id not in user_favorites:
        user_favorites[user_id] = []

    if text not in user_favorites[user_id]:
        user_favorites[user_id].append(text)
        return True

    return False


# =========================================================
# TTS
# =========================================================

def create_voice(text, lang):
    filename = tempfile.mktemp(suffix=".mp3")

    try:
        tts = gTTS(
            text=text,
            lang=TTS_LANGUAGES.get(lang, "en")
        )

        tts.save(filename)
        return filename

    except Exception as e:
        print("TTS error:", e)

        if os.path.exists(filename):
            os.remove(filename)

        return None


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start_handler(message):
    add_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "start"),
        reply_markup=main_keyboard(message.from_user.id)
    )

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "select_new"),
        reply_markup=language_keyboard()
    )


# =========================================================
# HELP
# =========================================================

@bot.message_handler(commands=["help"])
def help_command(message):
    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "help_text"),
        reply_markup=main_keyboard(message.from_user.id)
    )


# =========================================================
# ABOUT / HELP / LANGUAGE / FAVORITES
# =========================================================

@bot.message_handler(
    func=lambda message: message.text in [
        TEXTS[lang]["about"] for lang in TEXTS
    ]
)
def about_handler(message):
    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "about_text"),
        reply_markup=main_keyboard(message.from_user.id)
    )


@bot.message_handler(
    func=lambda message: message.text in [
        TEXTS[lang]["help"] for lang in TEXTS
    ]
)
def help_button_handler(message):
    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "help_text"),
        reply_markup=main_keyboard(message.from_user.id)
    )


@bot.message_handler(
    func=lambda message: message.text in [
        TEXTS[lang]["change_lang"] for lang in TEXTS
    ]
)
def change_language_handler(message):
    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        txt(message.from_user.id, "select_new"),
        reply_markup=language_keyboard()
    )


@bot.message_handler(
    func=lambda message: message.text in [
        TEXTS[lang]["favorites"] for lang in TEXTS
    ]
)
def favorites_handler(message):
    if not require_subscription(message):
        return

    user_id = message.from_user.id
    favorites = user_favorites.get(user_id, [])

    if not favorites:
        bot.send_message(
            message.chat.id,
            txt(user_id, "fav_empty"),
            reply_markup=main_keyboard(user_id)
        )
        return

    result = txt(user_id, "favorites_title") + "\n\n"

    for i, favorite in enumerate(favorites, 1):
        result += f"{i}. {favorite}\n\n"

    bot.send_message(
        message.chat.id,
        result,
        reply_markup=main_keyboard(user_id)
    )


# =========================================================
# LANGUAGE SELECTION
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lang:")
)
def language_callback(call):

    lang = call.data.split(":", 1)[1]

    if lang not in LANGUAGES:
        return

    user_languages[call.from_user.id] = lang
    all_users.add(call.from_user.id)

    bot.answer_callback_query(
        call.id,
        txt(call.from_user.id, "language_changed")
    )

    try:
        bot.edit_message_text(
            txt(call.from_user.id, "language_changed"),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_keyboard(call.from_user.id)
        )
    except Exception:
        bot.send_message(
            call.message.chat.id,
            txt(call.from_user.id, "language_changed"),
            reply_markup=main_keyboard(call.from_user.id)
        )


# =========================================================
# FAVORITES CALLBACK
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("fav:")
)
def favorite_callback(call):

    try:
        data = call.data.split(":", 1)
        action = data[1]

        user_id = call.from_user.id

        if action == "add":

            text = call.message.text or ""

            if "🌐 <b>Tarjima:</b>\n\n" in text:
                translation = text.split(
                    "🌐 <b>Tarjima:</b>\n\n",
                    1
                )[1]
            else:
                translation = text

            if user_id not in user_favorites:
                user_favorites[user_id] = []

            if translation in user_favorites[user_id]:

                bot.answer_callback_query(
                    call.id,
                    txt(user_id, "favorite_exists")
                )

            else:

                user_favorites[user_id].append(
                    translation
                )

                bot.answer_callback_query(
                    call.id,
                    txt(user_id, "favorite_added")
                )

        elif action == "remove":

            bot.answer_callback_query(
                call.id,
                txt(user_id, "favorite_removed")
            )

    except Exception as e:
        print("Favorite error:", e)


# =========================================================
# PHOTO / IMAGE
# =========================================================

@bot.message_handler(content_types=["photo"])
def photo_handler(message):

    if not require_subscription(message):
        return

    try:

        file_info = bot.get_file(
            message.photo[-1].file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        image_path = tempfile.mktemp(
            suffix=".jpg"
        )

        with open(image_path, "wb") as f:
            f.write(downloaded)

        image = Image.open(image_path)

        extracted_text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        os.remove(image_path)

        if not extracted_text.strip():

            bot.send_message(
                message.chat.id,
                "❌ Rasmda matn topilmadi."
            )

            return

        target = get_lang(
            message.from_user.id
        )

        result = translate_text(
            extracted_text,
            target
        )

        bot.send_message(
            message.chat.id,
            f"🖼 <b>Rasmdagi matn:</b>\n\n"
            f"{extracted_text}\n\n"
            f"🌐 <b>Tarjima:</b>\n\n"
            f"{result}",
            reply_markup=favorite_keyboard(
                message.from_user.id,
                result
            )
        )

        send_tts(
            message.chat.id,
            result,
            target
        )

    except Exception as e:

        print("Photo error:", e)

        bot.send_message(
            message.chat.id,
            "❌ Rasmni qayta ishlashda xatolik yuz berdi."
        )


# =========================================================
# VOICE
# =========================================================

@bot.message_handler(content_types=["voice"])
def voice_handler(message):

    if not require_subscription(message):
        return

    input_file = None
    wav_file = None

    try:

        file_info = bot.get_file(
            message.voice.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        input_file = tempfile.mktemp(
            suffix=".ogg"
        )

        wav_file = tempfile.mktemp(
            suffix=".wav"
        )

        with open(input_file, "wb") as f:
            f.write(downloaded)

        audio = AudioSegment.from_file(
            input_file,
            format="ogg"
        )

        audio.export(
            wav_file,
            format="wav"
        )

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_file) as source:

            audio_data = recognizer.record(
                source
            )

        recognized = recognizer.recognize_google(
            audio_data
        )

        target = get_lang(
            message.from_user.id
        )

        result = translate_text(
            recognized,
            target
        )

        bot.send_message(
            message.chat.id,
            f"🎙 <b>Matn:</b>\n\n"
            f"{recognized}\n\n"
            f"🌐 <b>Tarjima:</b>\n\n"
            f"{result}",
            reply_markup=favorite_keyboard(
                message.from_user.id,
                result
            )
        )

        send_tts(
            message.chat.id,
            result,
            target
        )

    except sr.UnknownValueError:

        bot.send_message(
            message.chat.id,
            "❌ Ovozdagi gapni tushunib bo'lmadi."
        )

    except Exception as e:

        print("Voice error:", e)

        bot.send_message(
            message.chat.id,
            "❌ Ovozli xabarni qayta ishlashda xatolik."
        )

    finally:

        for file_path in [
            input_file,
            wav_file
        ]:

            if file_path and os.path.exists(
                file_path
            ):

                try:
                    os.remove(file_path)
                except:
                    pass


# =========================================================
# AUDIO FILE
# =========================================================

@bot.message_handler(content_types=["audio"])
def audio_handler(message):

    if not require_subscription(message):
        return

    bot.send_message(
        message.chat.id,
        "🎵 Audio fayl qabul qilindi. Qayta ishlanmoqda..."
    )

    input_file = None
    wav_file = None

    try:

        file_info = bot.get_file(
            message.audio.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        input_file = tempfile.mktemp(
            suffix=".mp3"
        )

        wav_file = tempfile.mktemp(
            suffix=".wav"
        )

        with open(input_file, "wb") as f:
            f.write(downloaded)

        audio = AudioSegment.from_file(
            input_file
        )

        audio.export(
            wav_file,
            format="wav"
        )

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_file) as source:

            audio_data = recognizer.record(
                source
            )

        recognized = recognizer.recognize_google(
            audio_data
        )

        target = get_lang(
            message.from_user.id
        )

        result = translate_text(
            recognized,
            target
        )

        bot.send_message(
            message.chat.id,
            f"🎵 <b>Matn:</b>\n\n"
            f"{recognized}\n\n"
            f"🌐 <b>Tarjima:</b>\n\n"
            f"{result}",
            reply_markup=favorite_keyboard(
                message.from_user.id,
                result
            )
        )

        send_tts(
            message.chat.id,
            result,
            target
        )

    except Exception as e:

        print("Audio error:", e)

        bot.send_message(
            message.chat.id,
            "❌ Audio faylni qayta ishlashda xatolik."
        )

    finally:

        for file_path in [
            input_file,
            wav_file
        ]:

            if file_path and os.path.exists(
                file_path
            ):

                try:
                    os.remove(file_path)
                except:
                    pass


# =========================================================
# DOCUMENT / FILE
# =========================================================

@bot.message_handler(content_types=["document"])
def document_handler(message):

    if not require_subscription(message):
        return

    filename = (
        message.document.file_name or ""
    ).lower()

    if not (
        filename.endswith(".txt")
        or filename.endswith(".docx")
    ):

        bot.send_message(
            message.chat.id,
            "❌ Faqat .txt va .docx fayllar "
            "qo'llab-quvvatlanadi."
        )

        return

    local_file = None

    try:

        file_info = bot.get_file(
            message.document.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        extension = os.path.splitext(
            filename
        )[1]

        local_file = tempfile.mktemp(
            suffix=extension
        )

        with open(local_file, "wb") as f:
            f.write(downloaded)

        if filename.endswith(".txt"):

            with open(
                local_file,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                text = f.read()

        else:

            document = Document(
                local_file
            )

            paragraphs = []

            for paragraph in document.paragraphs:

                if paragraph.text.strip():
                    paragraphs.append(
                        paragraph.text
                    )

            text = "\n".join(
                paragraphs
            )

        if not text.strip():

            bot.send_message(
                message.chat.id,
                "❌ Faylda matn topilmadi."
            )

            return

        target = get_lang(
            message.from_user.id
        )

        result = translate_text(
            text,
            target
        )

        for i in range(
            0,
            len(result),
            3500
        ):

            bot.send_message(
                message.chat.id,
                result[i:i + 3500]
            )

    except Exception as e:

        print("Document error:", e)

        bot.send_message(
            message.chat.id,
            "❌ Faylni tarjima qilishda xatolik."
        )

    finally:

        if local_file and os.path.exists(
            local_file
        ):

            try:
                os.remove(local_file)
            except:
                pass


# =========================================================
# TEXT
# =========================================================

@bot.message_handler(
    content_types=["text"]
)
def text_handler(message):

    if not require_subscription(message):
        return

    text = message.text.strip()

    if text.startswith("/"):
        return

    target = get_lang(
        message.from_user.id
    )

    result = translate_text(
        text,
        target
    )

    bot.send_message(
        message.chat.id,
        f"🌐 <b>Tarjima:</b>\n\n{result}",
        reply_markup=favorite_keyboard(
            message.from_user.id,
            result
        )
    )

    send_tts(
        message.chat.id,
        result,
        target
    )


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)


@app.route("/")
def home():
    return "Super Translator Bot is running!"


# =========================================================
# RUN
# =========================================================

def run_bot():

    print("Bot ishga tushdi...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
    )

# =========================================================
# RUN
# =========================================================

def run_bot():
    print("Bot ishga tushdi...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
    )


if __name__ == "__main__":

    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    port = int(
        os.environ.get(
            "PORT",
            8080
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
