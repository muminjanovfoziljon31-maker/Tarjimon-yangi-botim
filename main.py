# ============================================================
# SUPER TARJIMON BOT
# 6 TIL + RASM TARJIMASI + SO'Z MA'NOLARI
# ============================================================

import os
import re
import io
import json
import logging
import tempfile
import urllib.request
import urllib.parse
from typing import Optional

import telebot
from telebot import types

from deep_translator import GoogleTranslator

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract


# ============================================================
# SOZLAMALAR
# ============================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN topilmadi. Hostingdagi Environment Variables "
        "bo'limiga BOT_TOKEN ni qo'shing."
    )


# ============================================================
# BOT
# ============================================================

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# TILLAR
# ============================================================

LANGUAGES = {
    "uz": {
        "name": "🇺🇿 O‘zbek",
        "google": "uz",
        "ocr": "eng+rus"
    },

    "en": {
        "name": "🇬🇧 English",
        "google": "en",
        "ocr": "eng"
    },

    "ru": {
        "name": "🇷🇺 Русский",
        "google": "ru",
        "ocr": "rus+eng"
    },

    "ar": {
        "name": "🇸🇦 العربية",
        "google": "ar",
        "ocr": "ara+eng"
    },

    "ko": {
        "name": "🇰🇷 한국어",
        "google": "ko",
        "ocr": "kor+eng"
    },

    "zh": {
        "name": "🇨🇳 中文",
        "google": "zh-CN",
        "ocr": "chi_sim+eng"
    }
}


# ============================================================
# FOYDALANUVCHI TILLARI
# ============================================================

user_languages = {}


def get_user_language(user_id: int) -> str:
    return user_languages.get(user_id, "uz")


def set_user_language(user_id: int, lang: str):
    if lang in LANGUAGES:
        user_languages[user_id] = lang


# ============================================================
# MATNLAR
# ============================================================

TEXTS = {

    "uz": {
        "welcome":
            "👋 <b>Super Tarjimon Bot</b>ga xush kelibsiz!\n\n"
            "📝 Istalgan matnni yuboring — men uni tarjima qilaman.\n"
            "🖼️ Rasm yuborsangiz, rasmdagi matnni o‘qib tarjima qilib, "
            "tarjima qilingan yangi rasmni yuboraman.\n\n"
            "🔤 Agar bitta so‘z yuborsangiz, imkon qadar uning "
            "bir nechta asosiy ma’nolarini ko‘rsataman.\n\n"
            "🌍 Tilni tanlash uchun <b>🌐 Tilni o‘zgartirish</b> tugmasini bosing.",

        "help":
            "📚 <b>Yordam</b>\n\n"
            "📝 Matn yuboring — tarjima qilaman.\n"
            "🖼️ Rasm yuboring — rasmdagi yozuvni tarjima qilib, "
            "rasm holida qaytaraman.\n"
            "🔤 Bitta so‘z yuboring — asosiy ma’nolarini ko‘rsatishga harakat qilaman.\n\n"
            "🌐 <b>Tilni o‘zgartirish</b> — bot interfeysi va tarjima tilini o‘zgartiradi.\n"
            "ℹ️ <b>Haqida</b> — bot haqida ma’lumot.",

        "language":
            "🌐 <b>Tarjima qilinadigan tilni tanlang:</b>",

        "selected":
            "✅ Til o‘zgartirildi: <b>{}</b>",

        "about":
            "ℹ️ <b>Super Tarjimon Bot haqida</b>\n\n"
            "🤖 Bot vazifasi:\n"
            "• Matnlarni tarjima qilish\n"
            "• Rasmdagi matnni aniqlash va tarjima qilish\n"
            "• Bitta so‘zning asosiy ma’nolarini ko‘rsatish\n\n"
            "🌍 Qo‘llab-quvvatlanadigan tillar:\n"
            "🇺🇿 O‘zbek\n"
            "🇬🇧 English\n"
            "🇷🇺 Русский\n"
            "🇸🇦 العربية\n"
            "🇰🇷 한국어\n"
            "🇨🇳 中文\n\n"
            "👨‍💻 <b>Bot yaratuvchisi:</b> @Foziljon20l0",

        "error":
            "❌ Tarjima vaqtida xatolik yuz berdi. Keyinroq yana urinib ko‘ring.",

        "empty":
            "⚠️ Matn topilmadi.",

        "processing":
            "⏳ Tarjima qilinmoqda...",

        "image_processing":
            "🖼️ Rasm tahlil qilinmoqda va tarjima qilinmoqda...",

        "ocr_error":
            "❌ Rasm ichidagi matnni aniqlab bo‘lmadi.",

        "no_text":
            "⚠️ Rasm ichida tarjima qilinadigan matn topilmadi.",

        "word_meanings":
            "🔤 <b>So‘z:</b> {word}\n\n"
            "📖 <b>Asosiy ma’nolari:</b>\n{meanings}\n\n"
            "🌐 <b>Tarjima:</b> {translation}",

        "buttons": {
            "language": "🌐 Tilni o‘zgartirish",
            "about": "ℹ️ Haqida",
            "help": "❓ Yordam"
        }
    },


    "en": {
        "welcome":
            "👋 Welcome to <b>Super Translator Bot</b>!\n\n"
            "📝 Send any text and I will translate it.\n"
            "🖼️ Send an image and I will read the text, translate it, "
            "and return a translated image.\n\n"
            "🔤 If you send one word, I will try to show several main meanings.\n\n"
            "🌍 Use <b>🌐 Change Language</b> to select a language.",

        "help":
            "📚 <b>Help</b>\n\n"
            "📝 Send text — I will translate it.\n"
            "🖼️ Send an image — I will translate the text inside it.\n"
            "🔤 Send one word — I will try to show its main meanings.\n\n"
            "🌐 <b>Change Language</b> — changes the translation language.\n"
            "ℹ️ <b>About</b> — information about the bot.",

        "language":
            "🌐 <b>Select the translation language:</b>",

        "selected":
            "✅ Language changed to: <b>{}</b>",

        "about":
            "ℹ️ <b>About Super Translator Bot</b>\n\n"
            "🤖 Bot functions:\n"
            "• Translate text\n"
            "• Detect and translate text from images\n"
            "• Show main meanings of a single word\n\n"
            "🌍 Supported languages:\n"
            "🇺🇿 Uzbek\n"
            "🇬🇧 English\n"
            "🇷🇺 Russian\n"
            "🇸🇦 Arabic\n"
            "🇰🇷 Korean\n"
            "🇨🇳 Chinese\n\n"
            "👨‍💻 <b>Bot creator:</b> @Foziljon20l0",

        "error":
            "❌ An error occurred during translation. Please try again later.",

        "empty":
            "⚠️ No text was found.",

        "processing":
            "⏳ Translating...",

        "image_processing":
            "🖼️ Processing and translating the image...",

        "ocr_error":
            "❌ Could not detect text in the image.",

        "no_text":
            "⚠️ No translatable text was found in the image.",

        "word_meanings":
            "🔤 <b>Word:</b> {word}\n\n"
            "📖 <b>Main meanings:</b>\n{meanings}\n\n"
            "🌐 <b>Translation:</b> {translation}",

        "buttons": {
            "language": "🌐 Change Language",
            "about": "ℹ️ About",
            "help": "❓ Help"
        }
    },


    "ru": {
        "welcome":
            "👋 Добро пожаловать в <b>Super Translator Bot</b>!\n\n"
            "📝 Отправьте текст — я переведу его.\n"
            "🖼️ Отправьте изображение — я распознаю текст, переведу его "
            "и отправлю новое изображение.\n\n"
            "🔤 Если отправить одно слово, я постараюсь показать несколько "
            "основных значений.\n\n"
            "🌍 Для выбора языка нажмите <b>🌐 Изменить язык</b>.",

        "help":
            "📚 <b>Помощь</b>\n\n"
            "📝 Отправьте текст — я переведу его.\n"
            "🖼️ Отправьте изображение — я переведу текст внутри него.\n"
            "🔤 Отправьте одно слово — покажу основные значения.\n\n"
            "🌐 <b>Изменить язык</b> — изменить язык перевода.\n"
            "ℹ️ <b>О боте</b> — информация о боте.",

        "language":
            "🌐 <b>Выберите язык перевода:</b>",

        "selected":
            "✅ Язык изменён: <b>{}</b>",

        "about":
            "ℹ️ <b>О Super Translator Bot</b>\n\n"
            "🤖 Возможности бота:\n"
            "• Перевод текста\n"
            "• Распознавание и перевод текста на изображениях\n"
            "• Основные значения отдельных слов\n\n"
            "🌍 Поддерживаемые языки:\n"
            "🇺🇿 Узбекский\n"
            "🇬🇧 Английский\n"
            "🇷🇺 Русский\n"
            "🇸🇦 Арабский\n"
            "🇰🇷 Корейский\n"
            "🇨🇳 Китайский\n\n"
            "👨‍💻 <b>Создатель бота:</b> @Foziljon20l0",

        "error":
            "❌ Во время перевода произошла ошибка. Попробуйте позже.",

        "empty":
            "⚠️ Текст не найден.",

        "processing":
            "⏳ Перевод выполняется...",

        "image_processing":
            "🖼️ Изображение анализируется и переводится...",

        "ocr_error":
            "❌ Не удалось распознать текст на изображении.",

        "no_text":
            "⚠️ На изображении не найден текст для перевода.",

        "word_meanings":
            "🔤 <b>Слово:</b> {word}\n\n"
            "📖 <b>Основные значения:</b>\n{meanings}\n\n"
            "🌐 <b>Перевод:</b> {translation}",

        "buttons": {
            "language": "🌐 Изменить язык",
            "about": "ℹ️ О боте",
            "help": "❓ Помощь"
        }
    },


    "ar": {
        "welcome":
            "👋 مرحباً بك في <b>Super Translator Bot</b>!\n\n"
            "📝 أرسل أي نص وسأقوم بترجمته.\n"
            "🖼️ أرسل صورة وسأتعرف على النص الموجود فيها وأترجمه "
            "وأرسل لك صورة مترجمة.\n\n"
            "🔤 إذا أرسلت كلمة واحدة، سأحاول عرض عدة معانٍ رئيسية لها.\n\n"
            "🌍 لاختيار اللغة اضغط على <b>🌐 تغيير اللغة</b>.",

        "help":
            "📚 <b>المساعدة</b>\n\n"
            "📝 أرسل نصاً — سأقوم بترجمته.\n"
            "🖼️ أرسل صورة — سأترجم النص الموجود فيها.\n"
            "🔤 أرسل كلمة واحدة — سأحاول عرض معانيها الرئيسية.\n\n"
            "🌐 <b>تغيير اللغة</b> — تغيير لغة الترجمة.\n"
            "ℹ️ <b>حول البوت</b> — معلومات عن البوت.",

        "language":
            "🌐 <b>اختر لغة الترجمة:</b>",

        "selected":
            "✅ تم تغيير اللغة إلى: <b>{}</b>",

        "about":
            "ℹ️ <b>حول Super Translator Bot</b>\n\n"
            "🤖 وظائف البوت:\n"
            "• ترجمة النصوص\n"
            "• التعرف على النصوص في الصور وترجمتها\n"
            "• عرض المعاني الرئيسية للكلمة الواحدة\n\n"
            "🌍 اللغات المدعومة:\n"
            "🇺🇿 الأوزبكية\n"
            "🇬🇧 الإنجليزية\n"
            "🇷🇺 الروسية\n"
            "🇸🇦 العربية\n"
            "🇰🇷 الكورية\n"
            "🇨🇳 الصينية\n\n"
            "👨‍💻 <b>منشئ البوت:</b> @Foziljon20l0",

        "error":
            "❌ حدث خطأ أثناء الترجمة. حاول مرة أخرى لاحقاً.",

        "empty":
            "⚠️ لم يتم العثور على نص.",

        "processing":
            "⏳ جارٍ الترجمة...",

        "image_processing":
            "🖼️ جارٍ تحليل الصورة وترجمتها...",

        "ocr_error":
            "❌ تعذر التعرف على النص في الصورة.",

        "no_text":
            "⚠️ لم يتم العثور على نص قابل للترجمة في الصورة.",

        "word_meanings":
            "🔤 <b>الكلمة:</b> {word}\n\n"
            "📖 <b>المعاني الرئيسية:</b>\n{meanings}\n\n"
            "🌐 <b>الترجمة:</b> {translation}",

        "buttons": {
            "language": "🌐 تغيير اللغة",
            "about": "ℹ️ حول البوت",
            "help": "❓ المساعدة"
        }
    },


    "ko": {
        "welcome":
            "👋 <b>Super Translator Bot</b>에 오신 것을 환영합니다!\n\n"
            "📝 텍스트를 보내주시면 번역해 드립니다.\n"
            "🖼️ 이미지를 보내주시면 이미지의 글자를 인식하고 번역한 후 "
            "번역된 이미지로 보내드립니다.\n\n"
            "🔤 한 단어를 보내면 가능한 경우 여러 주요 의미를 보여드립니다.\n\n"
            "🌍 언어를 선택하려면 <b>🌐 언어 변경</b>을 눌러주세요.",

        "help":
            "📚 <b>도움말</b>\n\n"
            "📝 텍스트를 보내면 번역합니다.\n"
            "🖼️ 이미지를 보내면 이미지 속 글자를 번역합니다.\n"
            "🔤 한 단어를 보내면 주요 의미를 보여드리려고 합니다.\n\n"
            "🌐 <b>언어 변경</b> — 번역 언어를 변경합니다.\n"
            "ℹ️ <b>봇 정보</b> — 봇에 대한 정보입니다.",

        "language":
            "🌐 <b>번역 언어를 선택하세요:</b>",

        "selected":
            "✅ 언어가 변경되었습니다: <b>{}</b>",

        "about":
            "ℹ️ <b>Super Translator Bot 정보</b>\n\n"
            "🤖 봇 기능:\n"
            "• 텍스트 번역\n"
            "• 이미지 속 텍스트 인식 및 번역\n"
            "• 한 단어의 주요 의미 표시\n\n"
            "🌍 지원 언어:\n"
            "🇺🇿 우즈베크어\n"
            "🇬🇧 영어\n"
            "🇷🇺 러시아어\n"
            "🇸🇦 아랍어\n"
            "🇰🇷 한국어\n"
            "🇨🇳 중국어\n\n"
            "👨‍💻 <b>봇 제작자:</b> @Foziljon20l0",

        "error":
            "❌ 번역 중 오류가 발생했습니다. 나중에 다시 시도해주세요.",

        "empty":
            "⚠️ 텍스트를 찾을 수 없습니다.",

        "processing":
            "⏳ 번역 중...",

        "image_processing":
            "🖼️ 이미지를 분석하고 번역하는 중입니다...",

        "ocr_error":
            "❌ 이미지에서 텍스트를 인식하지 못했습니다.",

        "no_text":
            "⚠️ 이미지에서 번역할 텍스트를 찾지 못했습니다.",

        "word_meanings":
            "🔤 <b>단어:</b> {word}\n\n"
            "📖 <b>주요 의미:</b>\n{meanings}\n\n"
            "🌐 <b>번역:</b> {translation}",

        "buttons": {
            "language": "🌐 언어 변경",
            "about": "ℹ️ 봇 정보",
            "help": "❓ 도움말"
        }
    },


    "zh": {
        "welcome":
            "👋 欢迎使用 <b>Super Translator Bot</b>！\n\n"
            "📝 发送文本，我会为你翻译。\n"
            "🖼️ 发送图片，我会识别图片中的文字并翻译，然后发送翻译后的图片。\n\n"
            "🔤 如果发送一个单词，我会尽可能显示它的多个主要含义。\n\n"
            "🌍 点击 <b>🌐 更改语言</b> 选择语言。",

        "help":
            "📚 <b>帮助</b>\n\n"
            "📝 发送文本 — 我会翻译它。\n"
            "🖼️ 发送图片 — 我会翻译图片中的文字。\n"
            "🔤 发送一个单词 — 我会尝试显示主要含义。\n\n"
            "🌐 <b>更改语言</b> — 更改翻译语言。\n"
            "ℹ️ <b>关于机器人</b> — 查看机器人信息。",

        "language":
            "🌐 <b>请选择翻译语言：</b>",

        "selected":
            "✅ 语言已更改为：<b>{}</b>",

        "about":
            "ℹ️ <b>关于 Super Translator Bot</b>\n\n"
            "🤖 机器人功能：\n"
            "• 翻译文本\n"
            "• 识别并翻译图片中的文字\n"
            "• 显示单词的主要含义\n\n"
            "🌍 支持的语言：\n"
            "🇺🇿 乌兹别克语\n"
            "🇬🇧 英语\n"
            "🇷🇺 俄语\n"
            "🇸🇦 阿拉伯语\n"
            "🇰🇷 韩语\n"
            "🇨🇳 中文\n\n"
            "👨‍💻 <b>机器人创建者：</b> @Foziljon20l0",

        "error":
            "❌ 翻译过程中出现错误，请稍后再试。",

        "empty":
            "⚠️ 没有找到文本。",

        "processing":
            "⏳ 正在翻译...",

        "image_processing":
            "🖼️ 正在分析并翻译图片...",

        "ocr_error":
            "❌ 无法识别图片中的文字。",

        "no_text":
            "⚠️ 图片中没有找到可翻译的文字。",

        "word_meanings":
            "🔤 <b>单词：</b> {word}\n\n"
            "📖 <b>主要含义：</b>\n{meanings}\n\n"
            "🌐 <b>翻译：</b> {translation}",

        "buttons": {
            "language": "🌐 更改语言",
            "about": "ℹ️ 关于机器人",
            "help": "❓ 帮助"
        }
    }
}


# ============================================================
# TEXT FUNKSIYASI
# ============================================================

def t(user_id: int, key: str) -> str:
    lang = get_user_language(user_id)
    return TEXTS[lang][key]


# ============================================================
# ASOSIY KLAVIATURA
# ============================================================

def main_keyboard(user_id: int):
    lang = get_user_language(user_id)

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add(
        types.KeyboardButton(TEXTS[lang]["buttons"]["language"]),
        types.KeyboardButton(TEXTS[lang]["buttons"]["about"])
    )

    keyboard.add(
        types.KeyboardButton(TEXTS[lang]["buttons"]["help"])
    )

    return keyboard


# ============================================================
# TIL TANLASH INLINE KEYBOARD
# ============================================================

def language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = []

    for code, data in LANGUAGES.items():
        buttons.append(
            types.InlineKeyboardButton(
                data["name"],
                callback_data=f"lang:{code}"
            )
        )

    for i in range(0, len(buttons), 2):
        keyboard.row(*buttons[i:i + 2])

    return keyboard


# ============================================================
# GOOGLE TRANSLATOR
# ============================================================

def translate_text(text: str, target_lang: str) -> str:

    if not text or not text.strip():
        return ""

    try:

        result = GoogleTranslator(
            source="auto",
            target=target_lang
        ).translate(text)

        return result if result else ""

    except Exception as e:

        logger.error(
            "Translation error: %s",
            e
        )

        return ""


# ============================================================
# MATN TILINI TAXMIN QILISH
# ============================================================

def detect_language(text: str) -> str:

    text = text.strip()

    # Arabic
    if re.search(r"[\u0600-\u06FF]", text):
        return "ar"

    # Korean
    if re.search(r"[\uAC00-\uD7AF]", text):
        return "ko"

    # Chinese
    if re.search(r"[\u4E00-\u9FFF]", text):
        return "zh"

    # Cyrillic
    if re.search(r"[А-Яа-яЁё]", text):
        return "ru"

    # Uzbek special letters
    if re.search(r"[ʻ’‘ʼ]", text):
        return "uz"

    # Uzbek common words
    uz_words = {
        "men",
        "sen",
        "u",
        "biz",
        "siz",
        "ular",
        "salom",
        "qanday",
        "nima",
        "uchun",
        "bilan",
        "emas",
        "ha",
        "yo‘q",
        "yoq",
        "maktab",
        "kitob",
        "yaxshi",
        "kerak",
        "bo‘ladi",
        "boladi"
    }

    words = re.findall(
        r"[A-Za-zÀ-ÿʻ’‘ʼ-]+",
        text.lower()
    )

    if any(word in uz_words for word in words):
        return "uz"

    # Default English
    return "en"


# ============================================================
# BITTA SO'Z EKANINI ANIQLASH
# ============================================================

def is_single_word(text: str) -> bool:

    text = text.strip()

    if not text:
        return False

    # faqat bitta so'z
    if len(text.split()) != 1:
        return False

    # juda uzun bo'lmasin
    if len(text) > 50:
        return False

    # URL yoki raqam bo'lmasin
    if "http://" in text.lower():
        return False

    if "https://" in text.lower():
        return False

    if re.fullmatch(r"[\d\W_]+", text):
        return False

    return True


# ============================================================
# ENGLISH DICTIONARY API
# ============================================================

def dictionary_meanings(word: str):

    try:

        encoded = urllib.parse.quote(word)

        url = (
            "https://api.dictionaryapi.dev/api/v2/entries/en/"
            + encoded
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SuperTranslatorBot/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=8
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        meanings = []

        if isinstance(data, list):

            for entry in data:

                for meaning in entry.get(
                    "meanings",
                    []
                ):

                    part = meaning.get(
                        "partOfSpeech",
                        ""
                    )

                    for definition in meaning.get(
                        "definitions",
                        []
                    ):

                        definition_text = definition.get(
                            "definition",
                            ""
                        )

                        if definition_text:

                            if part:
                                item = (
                                    f"• <b>{part}</b>: "
                                    f"{definition_text}"
                                )
                            else:
                                item = (
                                    f"• {definition_text}"
                                )

                            if item not in meanings:
                                meanings.append(item)

                        if len(meanings) >= 8:
                            break

                    if len(meanings) >= 8:
                        break

                if len(meanings) >= 8:
                    break

        return meanings

    except Exception as e:

        logger.warning(
            "Dictionary API error: %s",
            e
        )

        return []


# ============================================================
# SO'Z MA'NOLARINI OLISH
# ============================================================

def get_word_meanings(
    word: str,
    target_lang: str
):

    source_lang = detect_language(word)

    meanings = []

    # English word uchun dictionary
    if source_lang == "en":

        meanings = dictionary_meanings(word)

    # Tarjima
    translation = translate_text(
        word,
        LANGUAGES[target_lang]["google"]
    )

    return meanings, translation


# ============================================================
# SO'Z UCHUN JAVOB
# ============================================================

def make_word_response(
    user_id: int,
    word: str
):

    target_lang = get_user_language(
        user_id
    )

    meanings, translation = get_word_meanings(
        word,
        target_lang
    )

    if meanings:

        formatted = "\n".join(
            meanings
        )

    else:

        formatted = (
            "• "
            + translation
        )

    return TEXTS[target_lang][
        "word_meanings"
    ].format(
        word=word,
        meanings=formatted,
        translation=translation or "—"
    )


# ============================================================
# FONT TOPISH
# ============================================================

def find_font(size: int = 32):

    possible_fonts = [

        # Linux
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",

        # DejaVu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        # Windows
        "C:/Windows/Fonts/arial.ttf",

        # Local
        "arial.ttf",
        "NotoSans-Regular.ttf"
    ]

    for path in possible_fonts:

        try:

            if os.path.exists(path):

                return ImageFont.truetype(
                    path,
                    size
                )

        except Exception:
            pass

    return ImageFont.load_default()


# ============================================================
# RASMNI OCR UCHUN TAYYORLASH
# ============================================================

def prepare_image_for_ocr(
    image: Image.Image
):

    image = image.convert("RGB")

    # kattalashtirish
    width, height = image.size

    if width < 1200:

        ratio = 1200 / width

        image = image.resize(
            (
                int(width * ratio),
                int(height * ratio)
            )
        )

    # grayscale
    gray = image.convert("L")

    # kontrast
    gray = gray.filter(
        ImageFilter.SHARPEN
    )

    return gray


# ============================================================
# OCR
# ============================================================

def extract_text_from_image(
    image: Image.Image,
    target_lang: str
):

    prepared = prepare_image_for_ocr(
        image
    )

    ocr_lang = LANGUAGES[
        target_lang
    ]["ocr"]

    try:

        text = pytesseract.image_to_string(
            prepared,
            lang=ocr_lang,
            config="--psm 6"
        )

        return text.strip()

    except Exception as e:

        logger.warning(
            "OCR error with %s: %s",
            ocr_lang,
            e
        )

        # fallback English
        try:

            text = pytesseract.image_to_string(
                prepared,
                lang="eng",
                config="--psm 6"
            )

            return text.strip()

        except Exception as second_error:

            logger.error(
                "Fallback OCR error: %s",
                second_error
            )

            return ""


# ============================================================
# MATNNI QATORLARGA AJRATISH
# ============================================================

def wrap_text(
    draw,
    text,
    font,
    max_width
):

    words = text.split()

    lines = []

    current = ""

    for word in words:

        test = (
            current + " " + word
        ).strip()

        bbox = draw.textbbox(
            (0, 0),
            test,
            font=font
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:

            current = test

        else:

            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# ============================================================
# TARJIMA QILINGAN RASM YARATISH
# ============================================================

def create_translated_image(
    original_image: Image.Image,
    translated_text: str,
    original_text: str
):

    image = original_image.convert(
        "RGB"
    )

    width, height = image.size

    # juda katta rasmni kamaytirish
    max_width = 1600

    if width > max_width:

        ratio = max_width / width

        image = image.resize(
            (
                int(width * ratio),
                int(height * ratio)
            )
        )

        width, height = image.size

    # font
    font_size = max(
        24,
        min(48, width // 30)
    )

    font = find_font(
        font_size
    )

    small_font = find_font(
        max(18, font_size - 8)
    )

    # vaqtincha draw
    temp_draw = ImageDraw.Draw(
        image
    )

    # tarjimani wrap qilish
    lines = wrap_text(
        temp_draw,
        translated_text,
        font,
        width - 80
    )

    # original text ham juda uzun bo'lsa
    original_lines = wrap_text(
        temp_draw,
        original_text,
        small_font,
        width - 80
    )

    line_height = font_size + 12

    small_line_height = (
        max(18, font_size - 8) + 8
    )

    translation_height = (
        90 +
        len(lines) * line_height
    )

    original_height = (
        50 +
        len(original_lines) *
        small_line_height
    )

    extra_height = (
        translation_height +
        original_height +
        30
    )

    # yangi canvas
    new_image = Image.new(
        "RGB",
        (
            width,
            height + extra_height
        ),
        "white"
    )

    # original image
    new_image.paste(
        image,
        (0, 0)
    )

    draw = ImageDraw.Draw(
        new_image
    )

    y = height + 15

    # Original
    draw.text(
        (30, y),
        "Original:",
        font=small_font,
        fill="black"
    )

    y += small_line_height

    for line in original_lines:

        draw.text(
            (30, y),
            line,
            font=small_font,
            fill="black"
        )

        y += small_line_height

    # Translation
    y += 10

    draw.text(
        (30, y),
        "Translation:",
        font=font,
        fill="black"
    )

    y += line_height

    for line in lines:

        draw.text(
            (30, y),
            line,
            font=font,
            fill="black"
        )

        y += line_height

    return new_image


# ============================================================
# START
# ============================================================

@bot.message_handler(
    commands=["start"]
)
def start_command(message):

    user_id = message.from_user.id

    if user_id not in user_languages:
        user_languages[user_id] = "uz"

    bot.send_message(
        message.chat.id,
        t(user_id, "welcome"),
        reply_markup=main_keyboard(
            user_id
        )
    )


# ============================================================
# HELP
# ============================================================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        t(user_id, "help"),
        reply_markup=main_keyboard(
            user_id
        )
    )


# ============================================================
# LANGUAGE COMMAND
# ============================================================

@bot.message_handler(
    commands=["language"]
)
def language_command(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        t(user_id, "language"),
        reply_markup=language_keyboard()
    )


# ============================================================
# LANGUAGE BUTTON
# ============================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("lang:")
)
def language_callback(call):

    user_id = call.from_user.id

    lang = call.data.split(
        ":",
        1
    )[1]

    if lang not in LANGUAGES:
        return

    set_user_language(
        user_id,
        lang
    )

    try:

        bot.answer_callback_query(
            call.id
        )

    except Exception:
        pass

    bot.send_message(
        call.message.chat.id,
        TEXTS[lang]["selected"].format(
            LANGUAGES[lang]["name"]
        ),
        reply_markup=main_keyboard(
            user_id
        )
    )


# ============================================================
# TILNI O'ZGARTIRISH BUTTON
# ============================================================

@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["buttons"]["language"]
        for lang in TEXTS
    ]
)
def language_button(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        t(user_id, "language"),
        reply_markup=language_keyboard()
    )


# ============================================================
# ABOUT BUTTON
# ============================================================

@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["buttons"]["about"]
        for lang in TEXTS
    ]
)
def about_button(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        t(user_id, "about"),
        reply_markup=main_keyboard(
            user_id
        )
    )


# ============================================================
# HELP BUTTON
# ============================================================

@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["buttons"]["help"]
        for lang in TEXTS
    ]
)
def help_button(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        t(user_id, "help"),
        reply_markup=main_keyboard(
            user_id
        )
    )


# ============================================================
# RASM
# ============================================================

@bot.message_handler(
    content_types=["photo"]
)
def photo_handler(message):

    user_id = message.from_user.id

    lang = get_user_language(
        user_id
    )

    processing_message = bot.send_message(
        message.chat.id,
        t(user_id, "image_processing")
    )

    temp_original = None
    temp_result = None

    try:

        # eng katta photo
        photo = message.photo[-1]

        file_info = bot.get_file(
            photo.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        # original image
        original = Image.open(
            io.BytesIO(downloaded)
        ).convert("RGB")

        # OCR
        original_text = extract_text_from_image(
            original,
            lang
        )

        if not original_text:

            bot.edit_message_text(
                t(user_id, "no_text"),
                message.chat.id,
                processing_message.message_id
            )

            return

        # Tarjima
        translated_text = translate_text(
            original_text,
            LANGUAGES[lang]["google"]
        )

        if not translated_text:

            bot.edit_message_text(
                t(user_id, "error"),
                message.chat.id,
                processing_message.message_id
            )

            return

        # yangi rasm
        result_image = create_translated_image(
            original,
            translated_text,
            original_text
        )

        output = io.BytesIO()

        output.name = "translated_image.jpg"

        result_image.save(
            output,
            format="JPEG",
            quality=92
        )

        output.seek(0)

        # processing xabarini o'chirish
        try:

            bot.delete_message(
                message.chat.id,
                processing_message.message_id
            )

        except Exception:
            pass

        # rasm
        bot.send_photo(
            message.chat.id,
            output,
            caption=(
                "✅ "
                + LANGUAGES[lang]["name"]
                + " "
                + "tarjima"
            )
        )

    except Exception as e:

        logger.exception(
            "Photo processing error: %s",
            e
        )

        try:

            bot.edit_message_text(
                t(user_id, "error"),
                message.chat.id,
                processing_message.message_id
            )

        except Exception:

            bot.send_message(
                message.chat.id,
                t(user_id, "error")
            )

    finally:

        if temp_original:
            try:
                os.remove(
                    temp_original
                )
            except Exception:
                pass

        if temp_result:
            try:
                os.remove(
                    temp_result
                )
            except Exception:
                pass


# ============================================================
# TEXT
# ============================================================

@bot.message_handler(
    content_types=["text"]
)
def text_handler(message):

    user_id = message.from_user.id

    text = message.text.strip()

    if not text:
        return

    # Keyboard tugmalari handlerlardan o'tib ketgan bo'lsa
    all_buttons = []

    for lang in TEXTS:

        all_buttons.extend(
            TEXTS[lang]["buttons"].values()
        )

    if text in all_buttons:
        return

    # slash command
    if text.startswith("/"):
        return

    lang = get_user_language(
        user_id
    )

    # processing
    processing = bot.send_message(
        message.chat.id,
        t(user_id, "processing")
    )

    try:

        # Bitta so'z
        if is_single_word(text):

            response = make_word_response(
                user_id,
                text
            )

            bot.edit_message_text(
                response,
                message.chat.id,
                processing.message_id
            )

            return

        # Oddiy matn
        translated = translate_text(
            text,
            LANGUAGES[lang]["google"]
        )

        if not translated:

            bot.edit_message_text(
                t(user_id, "error"),
                message.chat.id,
                processing.message_id
            )

            return

        bot.edit_message_text(
            translated,
            message.chat.id,
            processing.message_id
        )

    except Exception as e:

        logger.exception(
            "Text handler error: %s",
            e
        )

        try:

            bot.edit_message_text(
                t(user_id, "error"),
                message.chat.id,
                processing.message_id
            )

        except Exception:
            pass


# ============================================================
# TXT FAYL
# ============================================================

@bot.message_handler(
    content_types=["document"]
)
def document_handler(message):

    user_id = message.from_user.id

    lang = get_user_language(
        user_id
    )

    document = message.document

    filename = (
        document.file_name or ""
    ).lower()

    # faqat txt
    if not filename.endswith(".txt"):

        bot.send_message(
            message.chat.id,
            "⚠️ Hozircha faqat .txt fayllar qo‘llab-quvvatlanadi."
        )

        return

    processing = bot.send_message(
        message.chat.id,
        t(user_id, "processing")
    )

    try:

        file_info = bot.get_file(
            document.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        original_text = downloaded.decode(
            "utf-8",
            errors="ignore"
        )

        if not original_text.strip():

            bot.edit_message_text(
                t(user_id, "empty"),
                message.chat.id,
                processing.message_id
            )

            return

        translated = translate_text(
            original_text,
            LANGUAGES[lang]["google"]
        )

        if not translated:

            bot.edit_message_text(
                t(user_id, "error"),
                message.chat.id,
                processing.message_id
            )

            return

        output = io.BytesIO()

        output.name = (
            "translated_" +
            filename
        )

        output.write(
            translated.encode(
                "utf-8"
            )
        )

        output.seek(0)

        try:

            bot.delete_message(
                message.chat.id,
                processing.message_id
            )

        except Exception:
            pass

        bot.send_document(
            message.chat.id,
            output,
            caption="✅ Tarjima qilingan fayl"
        )

    except Exception as e:

        logger.exception(
            "Document error: %s",
            e
        )

        try:

            bot.edit_message_text(
                t(user_id, "error"),
                message.chat.id,
                processing.message_id
            )

        except Exception:
            pass


# ============================================================
# BOT ISHLASHI
# ============================================================

if __name__ == "__main__":
    bot.infinity_polling(
        skip_pending=True,
        timeout=60,
        long_polling_timeout=60
    )


# ============================================================
# BOT ISHLASHI
# ============================================================

if __name__ == "__main__":

    logger.info(
        "Super Translator Bot ishga tushmoqda..."
    )

    logger.info(
        "Supported languages: %s",
        ", ".join(
            LANGUAGES.keys()
        )
    )

    while True:

        try:

            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )

        except Exception as e:

            logger.exception(
                "Bot polling error: %s",
                e
            )

            # bot yiqilib qolsa qayta ishga tushadi
            import time

            time.sleep(5)
