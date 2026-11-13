import asyncio
import logging
import os
import requests
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- НАСТРОЙКИ ---
# На Render токен и ID будут браться из переменных окружения (Environment Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8625421904:AAH14yjEvbyzS7O4emoUCm86ZRNsmQmctVc")
ADMIN_ID = int(os.getenv("ADMIN_ID", 6269035045))
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:5001")

CARD_NUMBER = "9860101224639944"
CARD_HOLDER = "SUXROB MUXITDINOV"
PRICE_JARVIS = "50 000 сум"
PRICE_VIDEO = "150 000 сум"

# ССЫЛКИ НА СКАЧИВАНИЕ
DOWNLOAD_LINK_MAC = "https://cloud.mail.ru/public/roXA/h3fW4CHim"
DOWNLOAD_LINK_AF = "https://cloud.mail.ru/public/uFfh/F7AGTyqCx"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class OrderForm(StatesGroup):
    waiting_username_jarvis = State()
    waiting_screenshot_jarvis = State()
    waiting_username_video = State()
    waiting_screenshot_video = State()
    waiting_support = State()


# --- СТАРТ И МЕНЮ ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💡 Что умеет Jarvis", callback_data="about")],
        [types.InlineKeyboardButton(text=f"💳 Купить Jarvis — {PRICE_JARVIS}", callback_data="buy_jarvis")],
        [types.InlineKeyboardButton(text=f"🎬 AFTER EFECTS PRO — {PRICE_VIDEO}", callback_data="buy_video")],
        [types.InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ])
    await message.answer(
        "👋 Привет! Я — бот для покупки цифровых продуктов.\n\n"
        "Доступно:\n"
        f"🤖 **Jarvis** — твой AI-ассистент ({PRICE_JARVIS})\n"
        f"🎬 **AFTER EFECTS PRO** — мощная программа для монтажа и эффектов ({PRICE_VIDEO})\n\n"
        "Выбери, что хочешь купить:",
        reply_markup=kb
    )


@dp.callback_query(lambda c: c.data == "about")
async def about_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "🤖 **JARVIS для Mac — что он умеет:**\n\n"
        "🗣 **Голосовое управление** — просто скажи «Jarvis», и он ответит.\n"
        "💬 **Чат** — задавай любые вопросы, как ChatGPT.\n"
        "🖥 **Управление Mac** — открывает приложения, показывает загрузку CPU, память.\n"
        "📁 **Работа с файлами** — читает, ищет, удаляет файлы по команде.\n"
        "⚙️ **Терминал** — выполняет shell-команды.\n"
        "🧠 **Память** — запоминает твои предпочтения.\n"
        "🔒 **Безопасность** — все действия с риском требуют подтверждения."
    )
    await callback.answer()


# --- ПОДДЕРЖКА ---
@dp.callback_query(lambda c: c.data == "support")
async def support_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🆘 **Поддержка**\n\n"
        "Опиши проблему одним сообщением. Что именно не работает? Что ты уже пробовал?\n\n"
        "Можешь прикрепить скриншот ошибки."
    )
    await state.set_state(OrderForm.waiting_support)
    await callback.answer()


@dp.message(OrderForm.waiting_support)
async def handle_support(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"🆘 **Новая проблема!**\n\n👤 Имя: {user.full_name}\n🔗 Юзернейм: @{user.username}\n🆔 ID: {user.id}\n\n📝 Сообщение: {message.text}"
    await bot.send_message(chat_id=ADMIN_ID, text=text)
    if message.photo:
        await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption="Скриншот от пользователя")
    await message.answer("✅ Твоё сообщение отправлено в поддержку. Мы ответим в ближайшее время.")
    await state.clear()


# --- ПОКУПКА JARVIS ---
@dp.callback_query(lambda c: c.data == "buy_jarvis")
async def process_buy_jarvis(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Я понял", callback_data="understood_jarvis")]
    ])
    await callback.message.answer(
        "📝 **Важно перед оплатой:**\n\n"
        "Чтобы мы знали, кто именно оплатил, тебе нужно указать свой "
        "**юзернейм** или **Telegram ID**.\n\n"
        "Нажми «Я понял», чтобы продолжить.",
        reply_markup=kb
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data == "understood_jarvis")
async def process_understood_jarvis(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "✍️ Напиши свой **юзернейм** или **Telegram ID**.\n\nПример: `@username` или `123456789`")
    await state.set_state(OrderForm.waiting_username_jarvis)
    await callback.answer()


@dp.message(OrderForm.waiting_username_jarvis)
async def handle_username_jarvis(message: types.Message, state: FSMContext):
    username = message.text.strip()
    await state.update_data(username=username)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid_jarvis")]
    ])
    await message.answer(
        f"💰 Оплата {PRICE_JARVIS}\n\n"
        f"📱 Через Click переведи на карту:\n`{CARD_NUMBER}`\nВладелец: {CARD_HOLDER}\n\n"
        f"⚠️ В комментарии к переводу укажи: **{username}**\n\n"
        f"После оплаты нажми кнопку «Я оплатил».",
        reply_markup=kb, parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "paid_jarvis")
async def process_paid_jarvis(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📸 Теперь отправь **скриншот чека** об оплате.")
    await state.set_state(OrderForm.waiting_screenshot_jarvis)
    await callback.answer()


@dp.message(OrderForm.waiting_screenshot_jarvis, lambda m: m.photo is not None)
async def handle_screenshot_jarvis(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username", "не указан")
    user = message.from_user
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"🔔 **Новый покупатель (Jarvis)!**\n\n👤 Имя: {user.full_name}\n🔗 Юзернейм: @{user.username}\n🆔 Telegram ID: {user.id}\n\n📝 Указал при оплате: **{username}**\n\nПроверь чек и напиши:\n/confirm_jarvis {user.id}"
    )
    await message.answer("⏳ Спасибо! Скриншот отправлен на проверку.")
    await state.clear()


# --- ПОКУПКА ВИДЕОРЕДАКТОРА ---
@dp.callback_query(lambda c: c.data == "buy_video")
async def process_buy_video(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Я понял", callback_data="understood_video")]
    ])
    await callback.message.answer(
        "📝 **Важно перед оплатой:**\n\n"
        "Чтобы мы знали, кто именно оплатил, тебе нужно указать свой "
        "**юзернейм** или **Telegram ID**.\n\n"
        "Нажми «Я понял», чтобы продолжить.",
        reply_markup=kb
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data == "understood_video")
async def process_understood_video(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "✍️ Напиши свой **юзернейм** или **Telegram ID**.\n\nПример: `@username` или `123456789`")
    await state.set_state(OrderForm.waiting_username_video)
    await callback.answer()


@dp.message(OrderForm.waiting_username_video)
async def handle_username_video(message: types.Message, state: FSMContext):
    username = message.text.strip()
    await state.update_data(username=username)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid_video")]
    ])
    await message.answer(
        f"💰 Оплата {PRICE_VIDEO}\n\n"
        f"📱 Через Click переведи на карту:\n`{CARD_NUMBER}`\nВладелец: {CARD_HOLDER}\n\n"
        f"⚠️ В комментарии к переводу укажи: **{username}**\n\n"
        f"После оплаты нажми кнопку «Я оплатил».",
        reply_markup=kb, parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "paid_video")
async def process_paid_video(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📸 Теперь отправь **скриншот чека** об оплате.")
    await state.set_state(OrderForm.waiting_screenshot_video)
    await callback.answer()


@dp.message(OrderForm.waiting_screenshot_video, lambda m: m.photo is not None)
async def handle_screenshot_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username", "не указан")
    user = message.from_user
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"🔔 **Новый покупатель (Видеоредактор)!**\n\n👤 Имя: {user.full_name}\n🔗 Юзернейм: @{user.username}\n🆔 Telegram ID: {user.id}\n\n📝 Указал при оплате: **{username}**\n\nПроверь чек и напиши:\n/confirm_video {user.id}"
    )
    await message.answer("⏳ Спасибо! Скриншот отправлен на проверку.")
    await state.clear()


# --- ВЫДАЧА ТОВАРА (АДМИН) ---
@dp.message(Command("confirm_jarvis"))
async def confirm_jarvis(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        buyer_id = int(message.text.split()[1])
        await bot.send_message(
            chat_id=buyer_id,
            text=(
                "✅ **Оплата Jarvis подтверждена!**\n\n"
                f"📥 **Скачай по ссылке:**\n{DOWNLOAD_LINK_MAC}\n\n"
                "**📖 ИНСТРУКЦИЯ:**\n"
                "1. Скачай и распакуй архив.\n"
                "2. Запусти `JarvisLoader.app`.\n"
                "3. Скопируй свой **HWID** и отправь сюда в чат.\n"
                "4. После привязки запусти `JarvisLoader.app` снова.\n\n"
                "**🔑 API-КЛЮЧ:** Используй бесплатный Groq (console.groq.com) или Gemini."
            )
        )
        await message.answer(f"✅ Инструкция Jarvis отправлена пользователю {buyer_id}.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@dp.message(Command("confirm_video"))
async def confirm_video(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    try:
        buyer_id = int(message.text.split()[1])
        await bot.send_message(
            chat_id=buyer_id,
            text=(
                "✅ **Оплата видеоредактора подтверждена!**\n\n"
                f"📥 **Скачай программу по ссылке:**\n{DOWNLOAD_LINK_AF}\n\n"
                "**📖 ИНСТРУКЦИЯ:**\n"
                "1. Перейди по ссылке и скачай файл.\n"
                "2. Распакуй архив.\n"
                "3. Следуй инструкции установки внутри архива.\n\n"
                "Если возникнут вопросы — пиши в поддержку."
            )
        )
        await message.answer(f"✅ Инструкция видеоредактора отправлена пользователю {buyer_id}.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


# --- ПРИВЯЗКА HWID ---
@dp.message()
async def handle_hwid(message: types.Message):
    text = message.text.strip()
    if text.isdigit() and len(text) > 10:
        hwid = text
        try:
            response = requests.post(f"{SERVER_URL}/add", json={"hwid": hwid}, timeout=10)
            if response.status_code == 200:
                await message.answer("✅ Твой компьютер привязан!\n\nТеперь запусти `JarvisLoader.app` снова.")
                await bot.send_message(chat_id=ADMIN_ID,
                                       text=f"🔔 Пользователь {message.from_user.id} добавил HWID: {hwid}")
            else:
                await message.answer("❌ Ошибка сервера. Попробуй позже.")
        except Exception as e:
            await message.answer(f"❌ Ошибка соединения с сервером: {e}")


# --- ЗАПУСК ДЛЯ RENDER (WEBHOOK) ---
async def on_startup(bot: Bot):
    webhook_url = f"{os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:10000')}/webhook"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook установлен: {webhook_url}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logging.info("Webhook удален")


def main():
    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Эндпоинт для UptimeRobot (чтобы Render не засыпал)
    async def health(request):
        return web.Response(text="OK")

    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()