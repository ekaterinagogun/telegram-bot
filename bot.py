import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import asyncio
import os

# ====== НАСТРОЙКИ ======
TOKEN = "8413313287:AAF1KLyKH7hl7W9gkokqWeE5RpCQQw0eZy8"
CHANNEL_USERNAME = "@nutritionpro"
CONSULT_LINK = "https://t.me/nutri_wayne"

# ====== ЛОГИ ======
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

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
            await callback_query.message.answer("🎉 Отлично! Вы подписаны. Вот мои полезные материалы 👇")

            # 1️⃣ 5 шагов к стройности
            steps_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton("📥 Скачать PDF", callback_data="file_steps")
            )
            await bot.send_photo(
                user_id,
                photo="https://i.ibb.co/vYbJtLQ/steps.jpg",  # замени на свою обложку
                caption="📘 <b>5 простых шагов к стройности</b>\n✨ Пошаговый план для комфортного снижения веса.",
                reply_markup=steps_kb
            )

            # 2️⃣ Белковая шпаргалка
            protein_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton("📥 Скачать PDF", callback_data="file_protein")
            )
            await bot.send_photo(
                user_id,
                photo="https://i.ibb.co/yVbtpF5/protein.jpg",
                caption="📗 <b>Белковая шпаргалка</b>\n🥦 Продукты, нормы и симптомы дефицита.",
                reply_markup=protein_kb
            )

            # 3️⃣ Питание для здоровой и сияющей кожи
            skin_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton("📥 Скачать PDF", callback_data="file_skin")
            )
            await bot.send_photo(
                user_id,
                photo="https://i.ibb.co/tZnH6GH/skin.jpg",
                caption="📕 <b>Питание для здоровой, чистой и сияющей кожи</b>\n💧 Как питание влияет на чистоту и сияние кожи.",
                reply_markup=skin_kb
            )

            # 💬 Консультация
            consult_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton("💬 Записаться на консультацию", url=CONSULT_LINK)
            )
            await bot.send_message(user_id, "🗓 Готова помочь лично!", reply_markup=consult_kb)

        else:
            await callback_query.answer("Вы ещё не подписались 😔", show_alert=True)
    except Exception as e:
        logging.error(e)
        await callback_query.answer("Не удалось проверить подписку. Убедитесь, что канал публичный.", show_alert=True)

# ====== INLINE-ОБРАБОТЧИКИ ДЛЯ ФАЙЛОВ ======
@dp.callback_query_handler(lambda c: c.data == "file_steps")
async def send_steps(callback_query: types.CallbackQuery):
    try:
        with open("files/5 простых шагов к стройности.pdf", "rb") as f:
            await bot.send_document(callback_query.from_user.id, f, caption="📘 5 простых шагов к стройности")
    except FileNotFoundError:
        await callback_query.answer("Файл не найден на сервере 😔", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "file_protein")
async def send_protein(callback_query: types.CallbackQuery):
    try:
        with open("files/Белковая шпаргалка.pdf", "rb") as f:
            await bot.send_document(callback_query.from_user.id, f, caption="📗 Белковая шпаргалка")
    except FileNotFoundError:
        await callback_query.answer("Файл не найден на сервере 😔", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "file_skin")
async def send_skin(callback_query: types.CallbackQuery):
    try:
        with open("files/Питание для здоровой, чистой и сияющей кожи.pdf", "rb") as f:
            await bot.send_document(callback_query.from_user.id, f, caption="📕 Питание для здоровой и сияющей кожи")
    except FileNotFoundError:
        await callback_query.answer("Файл не найден на сервере 😔", show_alert=True)

# ====== FAKE SERVER ДЛЯ RENDER ======
async def run_fake_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

if __name__ == "__main__":
    asyncio.get_event_loop().create_task(run_fake_server())
    executor.start_polling(dp, skip_updates=True)
