import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
)

from downloader import run
from pdf_to_image import pdf_to_image
from utils import generate_year_options, cleanup_files


TOKEN = "8802887183:AAGrlG3OFcRcVs0bsyZm8hSDOpGMOiAE_8U"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# -----------------------
# PER-USER STATE
# -----------------------
game_state = {}


def set_state(user_id: int, data: dict):
    game_state[user_id] = data


def get_state(user_id: int):
    return game_state.get(user_id)


def clear_state(user_id: int):
    game_state.pop(user_id, None)


# -----------------------
# KEYBOARDS
# -----------------------
def build_keyboard(years):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(y), callback_data=f"year_{y}")]
            for y in years
        ]
    )


def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎴 Новая газета")]
        ],
        resize_keyboard=True
    )


# -----------------------
# GAME START
# -----------------------
async def start_daily_game(message: Message):
    await message.answer("🔎 Загружаю выпуск...")

    pdf_path, year = run()

    if not pdf_path:
        await message.answer("❌ Не удалось найти выпуск")
        return

    image_path = pdf_to_image(pdf_path)
    options = generate_year_options(int(year))

    user_id = message.from_user.id

    set_state(user_id, {
        "year": int(year),
        "image": image_path,
        "pdf": pdf_path,
    })

    photo = FSInputFile(image_path)

    await message.answer_photo(
        photo,
        caption="🗞 Угадай год этой газеты",
        reply_markup=build_keyboard(options),
    )

    cleanup_files(pdf_path, image_path)


# -----------------------
# COMMANDS
# -----------------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "📰 Игра 'Угадай год по газете'\n\n"
        "/answer — показать ответ\n"
        "или нажми кнопку ниже",
        reply_markup=start_keyboard(),
    )


@dp.message(Command("daily"))
async def daily(message: Message):
    await start_daily_game(message)


@dp.message(F.text == "🎴 Новая газета")
async def daily_button(message: Message):
    await start_daily_game(message)


@dp.message(Command("answer"))
async def answer(message: Message):
    state = get_state(message.from_user.id)

    if not state:
        await message.answer("Сначала запусти игру")
        return

    await message.answer(f"📅 Ответ: {state['year']}")


# -----------------------
# CALLBACK (ANSWERS)
# -----------------------
@dp.callback_query(F.data.startswith("year_"))
async def check_year(call: CallbackQuery):
    user_id = call.from_user.id
    state = get_state(user_id)

    if not state:
        await call.message.answer("Сначала запусти игру")
        await call.answer()
        return

    chosen = int(call.data.split("_")[1])
    correct = state["year"]

    # убрать inline-кнопки
    await call.message.edit_reply_markup(reply_markup=None)

    if chosen == correct:
        await call.message.answer("✅ Правильно!")
    else:
        await call.message.answer(f"❌ Неверно. Правильный год: {correct}")

    clear_state(user_id)

    await call.answer()


# -----------------------
# MAIN
# -----------------------
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())