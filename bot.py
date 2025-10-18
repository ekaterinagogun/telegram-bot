import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os

# ====== НАСТРОЙКИ ======
TOKEN = "8413313287:AAF1KLyKH7hl7W9gkokqWeE5RpCQQw0eZy8"
CHANNEL_USERNAME = "@nutritionpro"  # например: @mychannel
CONSULT_LINK = "https://t.me/nutri_wayne"  # например: https://t.me/yourusername

# ====== ЛОГИРОВАНИЕ ======
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ====== КЛАВИАТУРЫ ======

# Главное меню (после проверки)
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(
    KeyboardButton("📘5 простых шагов к стройности"),
    KeyboardButton("📗Белковая шпаргалка - продукты, нормы, симптомы дефицита"),
    KeyboardButton("📕Питание для здоровой, чистой и сияющей кожи")
)
main_keyboard.add(KeyboardButton("💬 Записаться на консультацию"))

# ====== СТАРТ ======
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Чтобы получить материалы, подпишитесь на мой канал и нажмите кнопку <b>Проверить подписку</b> 👇"
    )

    check_sub_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"),
        InlineKeyboardButton("📢 Перейти к каналу", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")
    )

    await message.answer(text, reply_markup=check_sub_button)

# ====== ПРОВЕРКА ПОДПИСКИ ======
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await callback_query.message.answer(
                "🎉 Отлично! Вы подписаны.\nТеперь выберите, какой материал хотите получить 👇",
                reply_markup=main_keyboard
            )
        else:
            await callback_query.answer("Вы ещё не подписались 😔", show_alert=True)
    except Exception:
        await callback_query.answer("Не удалось проверить подписку. Убедитесь, что канал публичный.", show_alert=True)

# ====== ОБРАБОТЧИКИ КНОПОК С ФАЙЛАМИ ======
@dp.message_handler(lambda message: message.text == "📘5 простых шагов к стройности")
async def send_5 простых шагов к стройности(message: types.Message):
    with open("files/5 простых шагов к стройности.pdf", "rb") as f:
        await message.answer_document(f, caption="📘Вот ваш файл!")

@dp.message_handler(lambda message: message.text == "📗Белковая шпаргалка")
async def send_Белковая шпаргалка(message: types.Message):
    with open("files/Белковая шпаргалка.pdf", "rb") as f:
        await message.answer_document(f, caption="📗Вот ваш файл!")

@dp.message_handler(lambda message: message.text == "📕Питание для здоровой, чистой и сияющей кожи")
async def send_Питание для здоровой, чистой и сияющей кожи(message: types.Message):
    with open("files/Питание для здоровой, чистой и сияющей кожи.pdf", "rb") as f:
        await message.answer_document(f, caption="📕Вот ваш файл!")

# ====== КНОПКА ЗАПИСИ ======
@dp.message_handler(lambda message: message.text == "💬 Записаться на консультацию")
async def consultation_handler(message: types.Message):
    await message.answer(
        f"🗓 Чтобы записаться на консультацию — напишите мне лично:\n👉 <a href='{CONSULT_LINK}'>Перейти в чат</a>",
        disable_web_page_preview=True
    )

# ====== ЗАПУСК ======
if __name__ == "__main__":
    print("Бот запущен...")
from aiohttp import web
import asyncio

async def run_fake_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

asyncio.get_event_loop().create_task(run_fake_server())
    executor.start_polling(dp, skip_updates=True)
