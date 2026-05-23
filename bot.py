import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from downloader import run
from parser import  extract_headlines


TOKEN = "8802887183:AAGrlG3OFcRcVs0bsyZm8hSDOpGMOiAE_8U"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("📰 Бот запущен!\n\nКоманда:\n/daily — получить выпуск")

@dp.message(Command("daily"))
async def daily(message: Message):
    await message.answer("🔎 Загружаю выпуск...")

    pdf_path = run()

    if not pdf_path:
        await message.answer("❌ Не удалось найти подходящий выпуск")
        return

    headlines = extract_headlines(pdf_path)

    if not headlines:
        await message.answer("⚠️ Заголовки не найдены")
        return

    result = "\n".join(headlines[:20])

    await message.answer("🗞 Заголовки:\n\n" + result + "\n\n🤔 Попробуй угадать год!")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())