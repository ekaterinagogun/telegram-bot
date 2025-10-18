import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# ====== НАСТРОЙКИ ======
TOKEN = "8413313287:AAF1KLyKH7hl7W9gkokqWeE5RpCQQw0eZy8"
CHANNEL_USERNAME = "@nutritionpro"
CONSULT_LINK = "https://t.me/nutri_wayne"

# ====== ЛОГИ ======
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ====== СТАРТ ======
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"),
        InlineKeyboardButton("📢 Перейти к каналу", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")
    )
    await message.answer(
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Чтобы получить материалы, подпишись на мой канал и нажми <b>Проверить подписку</b> 👇",
        reply_markup=kb
    )

# ====== ПРОВЕРКА ПОДПИСКИ ======
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        status = member.status
        if status in ["member", "administrator", "creator"]:
            await callback_query.message.answer("🎉 Отлично! Вы подписаны. Вот мои материалы 👇")
            await send_materials(user_id)
        else:
            await callback_query.answer("❌ Вы ещё не подписаны на канал!", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        # Даже если Telegram даёт сбой — продолжаем
        await callback_query.message.answer("⚠️ Не удалось проверить подписку. Показываю материалы всё равно 👇")
        await send_materials(user_id)

# ====== МАТЕРИАЛЫ ======
async def send_materials(user_id):
    materials = [
        {
            "photo": "https://i.ibb.co/vYbJtLQ/steps.jpg",
            "caption": "📘 <b>5 простых шагов к стройности</b>\n✨ Пошаговый план для комфортного снижения веса.",
            "callback": "file_steps",
        },
        {
            "photo": "https://i.ibb.co/yVbtpF5/protein.jpg",
            "caption": "📗 <b>Белковая шпаргалка</b>\n🥦 Продукты, нормы и симптомы дефицита.",
            "callback": "file_protein",
        },
        {
            "photo": "https://i.ibb.co/tZnH6GH/skin.jpg",
            "caption": "📕 <b>Питание для здоровой, чистой и сияющей кожи</b>\n💧 Как питание влияет на чистоту и сияние кожи.",
            "callback": "file_skin",
        }
    ]

    for m in materials:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📥 Скачать PDF", callback_data=m["callback"])
        )
        await bot.send_photo(
            user_id,
            photo=m["photo"],
            caption=m["caption"],
            reply_markup=kb
        )

    consult_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("💬 Записаться на консультацию", url=CONSULT_LINK)
    )
    await bot.send_message(user_id, "🗓 Готова помочь лично!", reply_markup=consult_kb)

# ====== ОТПРАВКА ФАЙЛОВ ======
@dp.callback_query_handler(lambda c: c.data.startswith("file_"))
async def send_file(callback_query: types.CallbackQuery):
    files = {
        "file_steps": "files/5 простых шагов к стройности.pdf",
        "file_protein": "files/Белковая шпаргалка.pdf",
        "file_skin": "files/Питание для здоровой, чистой и сияющей кожи.pdf",
    }

    file_path = files.get(callback_query.data)
    if not file_path or not os.path.exists(file_path):
        await callback_query.answer("⚠️ Файл не найден на сервере 😔", show_alert=True)
        return

    try:
        with open(file_path, "rb") as f:
            await bot.send_document(callback_query.from_user.id, f)
        await callback_query.answer("📤 Файл отправлен!", show_alert=False)
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")
        await callback_query.answer("Ошибка при отправке файла 😢", show_alert=True)

# ====== FAKE SERVER ДЛЯ RENDER ======
async def run_fake_server():
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

if __name__ == "__main__":
    asyncio.get_event_loop().create_task(run_fake_server())
    executor.start_polling(dp, skip_updates=True)
