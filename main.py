import os
import tempfile
import threading
import requests

import telebot
from telebot import types
from deep_translator import GoogleTranslator
from PIL import Image
import pytesseract
from moviepy import VideoFileClip
from flask import Flask


# =========================================================
# BOT SOZLAMALARI
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN kiritilmagan!")

bot = telebot.TeleBot(
    TOKEN,
    parse_mode="HTML"
)


# =========================================================
# FOYDALANUVCHI MA'LUMOTLARI
# =========================================================

user_languages = {}
user_favorites = {}


# =========================================================
# 6 TA TIL
# =========================================================

LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "ko": "🇰🇷 한국어",
    "zh-CN": "🇨🇳 中文"
}


# =========================================================
# BOT MATNLARI
# =========================================================

TEXTS = {

    # =====================================================
    # O'ZBEKCHA
    # =====================================================

    "uz": {

        "about": "🤖 Bot haqida",
        "help": "❓ Yordam",
        "change_lang": "🌐 Tilni o'zgartirish",
        "favorites": "⭐ Sevimlilar",

        "choose_lang":
            "🌐 Kerakli tilni tanlang:",

        "language_changed":
            "✅ Til muvaffaqiyatli o'zgartirildi!",

        "start": (
            "👋 Assalomu alaykum!\n\n"
            "🤖 <b>Fast Translator</b> botiga xush kelibsiz!\n\n"
            "📝 So'z yoki matn yuboring.\n"
            "🎬 Video yuborsangiz, videodagi "
            "ko'rinadigan yozuvlarni tarjima qilaman."
        ),

        "about_text": (
            "🤖 <b>FAST TRANSLATOR</b>\n\n"
            "📝 Matn va so'z tarjimasi\n"
            "📚 Ko'p ma'noli so'zlar\n"
            "🎬 Videodagi yozuvlarni tarjima qilish\n"
            "🌐 6 ta til\n"
            "⭐ Sevimlilar\n"
            "❓ Yordam\n"
            "📱 Qulay menyu\n\n"
            "🔇 Video ovozi tarjima qilinmaydi.\n\n"
            "👨‍💻 <b>Bot yaratuvchisi:</b> @Foziljon20l0"
        ),

        "help_text": (
            "❓ <b>YORDAM</b>\n\n"

            "📝 <b>Matn tarjimasi</b>\n"
            "Istalgan so'z yoki gapni yuboring. "
            "Bot uni tanlangan tilga tarjima qiladi.\n\n"

            "📚 <b>Ko'p ma'noli so'zlar</b>\n"
            "Masalan, <b>book</b> kabi so'zlarda "
            "mavjud asosiy ma'nolar ham ko'rsatiladi.\n\n"

                       "🎬 <b>Video tarjimasi</b>\n"
            "Video yuboring. Bot videodagi ko'rinadigan "
            "yozuvlarni aniqlaydi va tanlangan tilga tarjima qiladi.\n\n"

            "🔇 <b>Muhim:</b> Videodagi ovoz tarjima qilinmaydi. "
            "Faqat videodagi yozuvlar tarjima qilinadi.\n\n"

            "⭐ <b>Sevimlilar</b>\n"
            "Tarjima ostidagi ⭐ tugmasini bosib, "
            "tarjimani saqlab qo'yishingiz mumkin.\n\n"

            "🌐 <b>Tilni o'zgartirish</b>\n"
            "🌐 tugmasini bosib 6 ta tildan birini tanlang."
        ),

        "favorites_empty":
            "⭐ Sizda saqlangan tarjimalar yo'q.",

        "favorites_title":
            "⭐ <b>Sevimlilar</b>\n\n",

        "add_favorite":
            "⭐ Sevimlilarga qo'shish",

        "favorite_added":
            "⭐ Tarjima sevimlilarga qo'shildi!",

        "favorite_exists":
            "⭐ Bu tarjima allaqachon saqlangan!",

        "video_processing":
            "🎬 Videodagi yozuvlar aniqlanmoqda...",

        "video_no_text":
            "❌ Videoda yozuv topilmadi.",

        "video_error":
            "❌ Videoni qayta ishlashda xatolik yuz berdi.",

        "translation_error":
            "❌ Tarjima qilishda xatolik yuz berdi.",

        "empty_text":
            "❌ Tarjima qilish uchun matn yuboring."
    },


    # =====================================================
    # ENGLISH
    # =====================================================

    "en": {

        "about": "🤖 About bot",
        "help": "❓ Help",
        "change_lang": "🌐 Change language",
        "favorites": "⭐ Favorites",

        "choose_lang":
            "🌐 Choose your language:",

        "language_changed":
            "✅ Language changed successfully!",

        "start": (
            "👋 Hello!\n\n"
            "🤖 Welcome to <b>Fast Translator</b>!\n\n"
            "📝 Send a word or text.\n"
            "🎬 Send a video to translate visible text."
        ),

        "about_text": (
            "🤖 <b>FAST TRANSLATOR</b>\n\n"
            "📝 Word and text translation\n"
            "📚 Multiple word meanings\n"
            "🎬 Translate visible text in videos\n"
            "🌐 6 languages\n"
            "⭐ Favorites\n"
            "❓ Help\n"
            "📱 Easy menu\n\n"
            "🔇 Video audio is not translated.\n\n"
            "👨‍💻 <b>Bot creator:</b> @Foziljon20l0"
        ),

        "help_text": (
            "❓ <b>HELP</b>\n\n"

            "📝 <b>Text translation</b>\n"
            "Send any word or sentence. "
            "The bot translates it into the selected language.\n\n"

            "📚 <b>Multiple meanings</b>\n"
            "For words such as <b>book</b>, "
            "the bot also shows the main available meanings.\n\n"

            "🎬 <b>Video translation</b>\n"
            "Send a video. The bot detects visible text "
            "and translates it into the selected language.\n\n"

            "🔇 <b>Important:</b> Video audio is not translated. "
            "Only visible text is translated.\n\n"

            "⭐ <b>Favorites</b>\n"
            "Press ⭐ under a translation to save it.\n\n"

            "🌐 <b>Change language</b>\n"
            "Press 🌐 and choose one of the 6 languages."
        ),

        "favorites_empty":
            "⭐ You have no saved translations.",

        "favorites_title":
            "⭐ <b>Favorites</b>\n\n",

        "add_favorite":
            "⭐ Add to favorites",

        "favorite_added":
            "⭐ Translation added to favorites!",

        "favorite_exists":
            "⭐ This translation is already saved!",

        "video_processing":
            "🎬 Detecting text in the video...",

        "video_no_text":
            "❌ No text was found in the video.",

        "video_error":
            "❌ Error while processing the video.",

        "translation_error":
            "❌ Translation error.",

        "empty_text":
            "❌ Send some text to translate."
    },


    # =====================================================
    # RUSSIAN
    # =====================================================

    "ru": {

        "about": "🤖 О боте",
        "help": "❓ Помощь",
        "change_lang": "🌐 Изменить язык",
        "favorites": "⭐ Избранное",

        "choose_lang":
            "🌐 Выберите язык:",

        "language_changed":
            "✅ Язык успешно изменён!",

        "start": (
            "👋 Здравствуйте!\n\n"
            "🤖 Добро пожаловать в <b>Fast Translator</b>!\n\n"
            "📝 Отправьте слово или текст.\n"
            "🎬 Отправьте видео для перевода текста."
        ),

        "about_text": (
            "🤖 <b>FAST TRANSLATOR</b>\n\n"
            "📝 Перевод слов и текста\n"
            "📚 Несколько значений слов\n"
            "🎬 Перевод текста в видео\n"
            "🌐 6 языков\n"
            "⭐ Избранное\n"
            "❓ Помощь\n"
            "📱 Удобное меню\n\n"
            "🔇 Голос видео не переводится.\n\n"
            "👨‍💻 <b>Создатель бота:</b> @Foziljon20l0"
        ),

        "help_text": (
            "❓ <b>ПОМОЩЬ</b>\n\n"

            "📝 <b>Перевод текста</b>\n"
            "Отправьте слово или предложение. "
            "Бот переведёт его на выбранный язык.\n\n"

            "📚 <b>Несколько значений</b>\n"
            "Для многозначных слов, например <b>book</b>, "
            "бот показывает основные значения.\n\n"

            "🎬 <b>Перевод видео</b>\n"
            "Отправьте видео. Бот распознает видимый текст "
            "и переведёт его.\n\n"

            "🔇 <b>Важно:</b> Голос видео не переводится. "
            "Переводится только видимый текст.\n\n"

            "⭐ <b>Избранное</b>\n"
            "Нажмите ⭐ под переводом, чтобы сохранить его.\n\n"

            "🌐 <b>Изменение языка</b>\n"
            "Нажмите 🌐 и выберите один из 6 языков."
        ),

        "favorites_empty":
            "⭐ У вас нет сохранённых переводов.",

        "favorites_title":
            "⭐ <b>Избранное</b>\n\n",

        "add_favorite":
            "⭐ Добавить в избранное",

        "favorite_added":
            "⭐ Перевод добавлен в избранное!",

        "favorite_exists":
            "⭐ Этот перевод уже сохранён!",

        "video_processing":
            "🎬 Определяем текст в видео...",

        "video_no_text":
            "❌ Текст в видео не найден.",

        "video_error":
            "❌ Ошибка обработки видео.",

        "translation_error":
            "❌ Ошибка перевода.",

        "empty_text":
            "❌ Отправьте текст."
    },


    # =====================================================
    # ARABIC
    # =====================================================

    "ar": {

        "about": "🤖 حول البوت",
        "help": "❓ المساعدة",
        "change_lang": "🌐 تغيير اللغة",
        "favorites": "⭐ المفضلة",

        "choose_lang":
            "🌐 اختر اللغة:",

        "language_changed":
            "✅ تم تغيير اللغة بنجاح!",

        "start": (
            "👋 مرحباً!\n\n"
            "🤖 أهلاً بك في <b>Fast Translator</b>!\n\n"
            "📝 أرسل كلمة أو نصاً.\n"
            "🎬 أرسل فيديو لترجمة النص الظاهر."
        ),

        "about_text": (
            "🤖 <b>FAST TRANSLATOR</b>\n\n"
            "📝 ترجمة الكلمات والنصوص\n"
            "📚 معاني الكلمات المتعددة\n"
            "🎬 ترجمة النص الظاهر في الفيديو\n"
            "🌐 6 لغات\n"
            "⭐ المفضلة\n"
            "❓ المساعدة\n"
            "📱 قائمة سهلة\n\n"
            "🔇 لا تتم ترجمة صوت الفيديو.\n\n"
            "👨‍💻 <b>منشئ البوت:</b> @Foziljon20l0"
        ),

        "help_text": (
            "❓ <b>المساعدة</b>\n\n"

            "📝 <b>ترجمة النص</b>\n"
            "أرسل أي كلمة أو جملة وسيتم ترجمتها "
            "إلى اللغة المختارة.\n\n"

            "📚 <b>معاني متعددة</b>\n"
            "للكلمات متعددة المعاني مثل <b>book</b>، "
            "يعرض البوت المعاني الرئيسية.\n\n"

            "🎬 <b>ترجمة الفيديو</b>\n"
            "أرسل فيديو وسيكتشف البوت النص الظاهر "
            "ويترجمه.\n\n"

            "🔇 <b>مهم:</b> لا تتم ترجمة صوت الفيديو. "
            "تتم ترجمة النص الظاهر فقط.\n\n"

            "⭐ <b>المفضلة</b>\n"
            "اضغط ⭐ أسفل الترجمة لحفظها.\n\n"

            "🌐 <b>تغيير اللغة</b>\n"
            "اضغط 🌐 واختر إحدى اللغات الست."
        ),

        "favorites_empty":
            "⭐ لا توجد ترجمات محفوظة.",

        "favorites_title":
            "⭐ <b>المفضلة</b>\n\n",

        "add_favorite":
            "⭐ إضافة إلى المفضلة",

        "favorite_added":
            "⭐ تمت إضافة الترجمة إلى المفضلة!",

        "favorite_exists":
            "⭐ هذه الترجمة محفوظة بالفعل!",

        "video_processing":
            "🎬 يتم اكتشاف النص في الفيديو...",

        "video_no_text":
            "❌ لم يتم العثور على نص في الفيديو.",

        "video_error":
            "❌ حدث خطأ أثناء معالجة الفيديو.",

        "translation_error":
            "❌ حدث خطأ في الترجمة.",

        "empty_text":
            "❌ أرسل نصاً للترجمة."
    },


    # =====================================================
    # KOREAN
    # =====================================================

    "ko": {

        "about": "🤖 봇 정보",
        "help": "❓ 도움말",
        "change_lang": "🌐 언어 변경",
        "favorites": "⭐ 즐겨찾기",

        "choose_lang":
            "🌐 언어를 선택하세요:",

        "language_changed":
            "✅ 언어가 성공적으로 변경되었습니다!",

        "start": (
            "👋 안녕하세요!\n\n"
            "🤖 <b>Fast Translator</b>에 오신 것을 환영합니다!\n\n"
            "📝 단어나 문장을 보내세요.\n"
            "🎬 동영상을 보내면 보이는 텍스트를 번역합니다."
        ),

        "about_text": (
            "🤖 <b>FAST TRANSLATOR</b>\n\n"
            "📝 단어 및 텍스트 번역\n"
            "📚 여러 단어 의미\n"
            "🎬 동영상의 보이는 텍스트 번역\n"
            "🌐 6개 언어\n"
            "⭐ 즐겨찾기\n"
            "❓ 도움말\n"
            "📱 편리한 메뉴\n\n"
            "🔇 동영상 음성은 번역되지 않습니다.\n\n"
            "👨‍💻 <b>봇 제작자:</b> @Foziljon20l0"
        ),

        "help_text": (
            "❓ <b>도움말</b>\n\n"

            "📝 <b>텍스트 번역</b>\n"
            "단어나 문장을 보내면 선택한 언어로 번역합니다.\n\n"

            "📚 <b>여러 의미</b>\n"
            "<b>book</b>과 같이 여러 의미가 있는 단어는 "
            "주요 의미도 보여줍니다.\n\n"

            "🎬 <b>동영상 번역</b>\n"
            "동영상을 보내면 보이는 텍스트를 찾아 번역합니다.\n\n"

            "🔇 <b>중요:</b> 동영상의 음성은 번역하지 않습니다. "
            "보이는 텍스트만 번역합니다.\n\n"

            "⭐ <b>즐겨찾기</b>\n"
            "번역 아래의 ⭐ 버튼을 눌러 저장할 수 있습니다.\n\n"

            "🌐 <b>언어 변경</b>\n"
            "🌐 버튼을 누르고 6개 언어 중 하나를 선택하세요."
        ),

        "favorites_empty":
            "⭐ 저장된 번역이 없습니다.",

        "favorites_title":
            "⭐ <b>즐겨찾기</b>\n\n",

        "add_favorite":
            "⭐ 즐겨찾기에 추가",

        "favorite_added":
            "⭐ 번역이 즐겨찾기에 추가되었습니다!",

        "favorite_exists":
            "⭐ 이미 저장된 번역입니다!",

        "video_processing":
            "🎬 동영상의 텍스트를 찾는 중입니다...",

        "video_no_text":
            "❌ 동영상에서 텍스트를 찾지 못했습니다.",

        "video_error":
            "❌ 동영상 처리 중 오류가 발생했습니다.",

        "translation_error":
            "❌ 번역 중 오류가 발생했습니다.",

        "empty_text":
            "❌ 번역할 텍스트를 보내주세요."
    },


    # =====================================================
    # CHINESE
    # =====================================================

    "zh-CN": {

        "about": "🤖 关于机器人",
        "help": "❓ 帮助",
        "change_lang": "🌐 更改语言",
        "favorites": "⭐ 收藏",

        "choose_lang":
            "🌐 请选择语言:",

        "language_changed":
            "✅ 语言已成功更改!",

        "start": (
            "👋 你好!\n\n"
            "🤖 欢迎使用 <b>Fast Translator</b>!\n\n"
            "📝 发送单词或文本。\n"
            "🎬 发送视频即可翻译可见文字。"
        ),

        "about_text": (
            "🤖 <b>FAST TRANSLATOR</b>\n\n"
            "📝 单词和文本翻译\n"
            "📚 单词的多个含义\n"
            "🎬 翻译视频中的可见文字\n"
            "🌐 6种语言\n"
            "⭐ 收藏\n"
            "❓ 帮助\n"
            "📱 方便的菜单\n\n"
            "🔇 不翻译视频声音。\n\n"
            "👨‍💻 <b>机器人创建者:</b> @Foziljon20l0"
        ),

        "help_text": (
            "❓ <b>帮助</b>\n\n"

            "📝 <b>文本翻译</b>\n"
            "发送单词或句子，机器人会翻译成所选语言。\n\n"

            "📚 <b>多个含义</b>\n"
            "对于像 <b>book</b> 这样的多义词，"
            "机器人也会显示主要含义。\n\n"

            "🎬 <b>视频翻译</b>\n"
            "发送视频，机器人会识别可见文字并进行翻译。\n\n"

            "🔇 <b>重要:</b> 不翻译视频声音，"
            "只翻译可见文字。\n\n"

            "⭐ <b>收藏</b>\n"
            "点击翻译下面的 ⭐ 按钮即可保存。\n\n"

            "🌐 <b>更改语言</b>\n"
            "点击 🌐 并选择六种语言之一。"
        ),

        "favorites_empty":
            "⭐ 没有保存的翻译。",

        "favorites_title":
            "⭐ <b>收藏</b>\n\n",

        "add_favorite":
            "⭐ 添加到收藏",

        "favorite_added":
            "⭐ 翻译已添加到收藏!",

        "favorite_exists":
            "⭐ 此翻译已经保存!",

        "video_processing":
            "🎬 正在识别视频中的文字...",

        "video_no_text":
            "❌ 视频中没有找到文字。",

        "video_error":
            "❌ 处理视频时发生错误。",

        "translation_error":
            "❌ 翻译时发生错误。",

        "empty_text":
            "❌ 请发送要翻译的文本。"
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

    return TEXTS.get(
        lang,
        TEXTS["uz"]
    ).get(
        key,
        TEXTS["uz"].get(key, "")
    )


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_keyboard(user_id):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add(
        types.KeyboardButton(
            txt(user_id, "about")
        ),
        types.KeyboardButton(
            txt(user_id, "help")
        )
    )

    keyboard.add(
        types.KeyboardButton(
            txt(user_id, "change_lang")
        ),
        types.KeyboardButton(
            txt(user_id, "favorites")
        )
    )

    return keyboard


# =========================================================
# TIL TANLASH
# =========================================================

def language_keyboard():

    keyboard = types.InlineKeyboardMarkup(
        row_width=2
    )

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
        return None

    try:

        translator = GoogleTranslator(
            source="auto",
            target=target
        )

        return translator.translate(text)

    except Exception as e:

        print("Translation error:", e)

        return None


# =========================================================
# KO'P MA'NOLI SO'ZLAR
# =========================================================

def get_word_meanings(word, target):

    word = word.strip()

    if not word or len(word.split()) != 1:
        return []

    try:

        api_url = (
            "https://api.dictionaryapi.dev/api/v2/"
            "entries/en/"
            + word
        )

        response = requests.get(
            api_url,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        meanings = []

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

                    if not definition_text:
                        continue

                    translated = translate_text(
                        definition_text,
                        target
                    )

                    if not translated:
                        continue

                    item = (
                        f"• <b>{part}</b> — "
                        f"{translated}"
                    )

                    if item not in meanings:
                        meanings.append(item)

        return meanings[:8]

    except Exception as e:

        print("Meaning error:", e)

        return []


# =========================================================
# FAVORITES
# =========================================================

def favorite_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "⭐",
            callback_data="favorite:add"
        )
    )

    return keyboard


def save_favorite(user_id, text):

    if user_id not in user_favorites:
        user_favorites[user_id] = []

    if text in user_favorites[user_id]:
        return False

    user_favorites[user_id].append(text)

    return True


# =========================================================
# START
# =========================================================

@bot.message_handler(
    commands=["start"]
)
def start_handler(message):

    user_id = message.from_user.id

    get_lang(user_id)

    bot.send_message(
        message.chat.id,
        txt(user_id, "start"),
        reply_markup=main_keyboard(user_id)
    )

    bot.send_message(
        message.chat.id,
        txt(user_id, "choose_lang"),
        reply_markup=language_keyboard()
    )


# =========================================================
# ABOUT
# =========================================================

@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["about"]
        for lang in TEXTS
    ]
)
def about_handler(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        txt(user_id, "about_text"),
        reply_markup=main_keyboard(user_id)
    )


# =========================================================
# HELP
# =========================================================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        txt(user_id, "help_text"),
        reply_markup=main_keyboard(user_id)
    )


@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["help"]
        for lang in TEXTS
    ]
)
def help_button_handler(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        txt(user_id, "help_text"),
        reply_markup=main_keyboard(user_id)
    )


# =========================================================
# CHANGE LANGUAGE
# =========================================================

@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["change_lang"]
        for lang in TEXTS
    ]
)
def change_language_handler(message):

    user_id = message.from_user.id

    bot.send_message(
        message.chat.id,
        txt(user_id, "choose_lang"),
        reply_markup=language_keyboard()
    )


# =========================================================
# FAVORITES
# =========================================================

@bot.message_handler(
    func=lambda message:
    message.text in [
        TEXTS[lang]["favorites"]
        for lang in TEXTS
    ]
)
def favorites_handler(message):

    user_id = message.f
