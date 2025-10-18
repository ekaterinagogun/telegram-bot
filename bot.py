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

# ====== ЛОГИРОВАНИЕ ======
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
            await callback_query.message.answer(
                "🎉 Отлично! Вы подписаны.\nТеперь выберите, какой материал хотите получить 👇"
            )
            await send_file_buttons(callback_query.message.chat.id)
        else:
            await callback_query.answer("Вы ещё не подписались 😔", show_alert=True)
    except Exception:
        await callback_query.answer("Не удалось проверить подписку. Убедитесь, что канал публичный.", show_alert=True)

# ====== КНОПКИ С ФАЙЛАМИ ======
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
    mapping = {
        "file_steps": "files/5 простых шагов к стройности.pdf",
        "file_protein": "files/Белковая шпаргалка.pdf",
        "file_skin": "files/Питание для здоровой, чистой и сияющей кожи.pdf"
    }

    path = mapping.get(callback_query.data)
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

# ====== FAKE SERVER (для Render) ======
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
