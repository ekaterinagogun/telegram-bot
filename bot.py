import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# ====== НАСТРОЙКИ ======
TOKEN = "8413313287:AAF1KLyKH7hl7W9gkokqWeE5RpCQQw0eZy8"
CHANNEL_USERNAME = "@nutritionpro"
CONSULT_LINK = "https://t.me/nutri_wayne"
WEBHOOK_HOST = "https://telegram-bot-9mod.onrender.com"  # 👈 твой Render URL
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# ====== ЛОГИ ======
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# ====== /start ======
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Чтобы получить материалы, подпишитесь на мой канал и нажмите кнопку <b>Проверить подписку</b> 👇"
    )

    buttons = InlineKeyboardMarkup(row_width=1)
    buttons.add(
        InlineKeyboardButton("📢 Перейти к каналу", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"),
        InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")
    )

    await message.answer(text, reply_markup=buttons)


# ====== ПРОВЕРКА ПОДПИСКИ ======
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await callback_query.message.answer(
                "🎉 Отлично! Вы подписаны.\nТеперь выберите, какой материал хотите получить 👇"
            )
            await send_file_buttons(callback_query.message.chat.id)
        else:
            await callback_query.answer("Вы ещё не подписались 😔", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        await callback_query.answer("Не удалось проверить подписку. Убедитесь, что канал публичный.", show_alert=True)


# ====== КНОПКИ С ФАЙЛАМИ (в чате!) ======
async def send_file_buttons(chat_id):
    files_markup = InlineKeyboardMarkup(row_width=1)
    files_markup.add(
        InlineKeyboardButton("📘 5 простых шагов к стройности", callback_data="file_steps"),
        InlineKeyboardButton("📗 Белковая шпаргалка", callback_data="file_protein"),
        InlineKeyboardButton("📕 Питание для здоровой кожи", callback_data="file_skin"),
        InlineKeyboardButton("💬 Записаться на консультацию", url=CONSULT_LINK)
    )
    await bot.send_message(chat_id, "👇 Выберите материал:", reply_markup=files_markup)


# ====== ОТПРАВКА ФАЙЛОВ ======
@dp.callback_query_handler(lambda c: c.data.startswith("file_"))
async def send_file(callback_query: types.CallbackQuery):
    files = {
        "file_steps": "files/5 простых шагов к стройности.pdf",
        "file_protein": "files/Белковая шпаргалка.pdf",
        "file_skin": "files/Питание для здоровой, чистой и сияющей кожи.pdf"
    }

    path = files.get(callback_query.data)
    if not path or not os.path.exists(path):
        await callback_query.answer("⚠️ Файл не найден. Проверьте название или путь.", show_alert=True)
        return

    try:
        with open(path, "rb") as f:
            await bot.send_document(callback_query.from_user.id, f)
        await callback_query.answer("📤 Файл отправлен!", show_alert=False)
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")
        await callback_query.answer("Ошибка при отправке файла 😢", show_alert=True)


# ====== WEBHOOK ======
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    logging.warning("Выключаем вебхук...")
    await bot.delete_webhook()
    logging.info("Вебхук удалён. Бот остановлен.")

async def handle_webhook(request):
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.process_update(telegram_update)
    return web.Response(text="OK")


# ====== СЕРВЕР ======
app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.router.add_get("/", lambda request: web.Response(text="Bot is running ✅"))
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=10000)
