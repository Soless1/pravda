import asyncio
import random

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile

from downloader import run
from pdf_to_image import pdf_to_image
import pytesseract
from PIL import Image
from utils import *

TOKEN = "8802887183:AAGrlG3OFcRcVs0bsyZm8hSDOpGMOiAE_8U"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# хранение текущей игры
game_state = {
    "year": None,
    "image": None,
    "pdf": None
}


def build_keyboard(years):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[[InlineKeyboardButton(text=str(y), callback_data=f"year_{y}")] for y in years],
        ]
    )


def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎴 Новая газета", callback_data="daily_new")]
        ]
    )




async def start_daily_game(message: Message):
    await message.answer("🔎 Загружаю выпуск...")

    pdf_path, year = run()

    if not pdf_path:
        await message.answer("❌ Не удалось найти выпуск")
        return

    image_path = pdf_to_image(pdf_path)

    options = generate_year_options(int(year))

    game_state["year"] = int(year)
    game_state["image"] = image_path

    keyboard = build_keyboard(options)
    photo = FSInputFile(image_path)

    await message.answer_photo(
        photo,
        caption="🗞 Угадай год этой газеты",
        reply_markup=keyboard
    )

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "📰 Игра 'Угадай год по газете'\n\n"
        "/daily — новая газета\n"
        "/hint — подсказка\n"
        "/answer — показать ответ",
        reply_markup=start_keyboard()
    )


@dp.message(Command("daily"))
async def daily(message: Message):
    await start_daily_game(message)




@dp.message(Command("answer"))
async def answer(message: Message):
    if not game_state["year"]:
        await message.answer("Сначала /daily")
        return

    await message.answer(f"📅 Ответ: {game_state['year']}")


@dp.callback_query(F.data.startswith("year_"))
async def check_year(call: CallbackQuery):
    chosen = int(call.data.split("_")[1])
    correct = game_state.get("year")

    if correct is None:
        await call.message.answer("Сначала /daily")
        return

    if chosen == correct:
        await call.message.answer("✅ Правильно!")
    else:
        await call.message.answer(f"❌ Неверно. Правильный год: {correct}")

    await call.answer()


@dp.callback_query(F.data == "daily_new")
async def daily_from_button(call: CallbackQuery):
    await start_daily_game(call.message)
    await call.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
