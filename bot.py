from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8767833618:AAGl7jVhGT_sqoWA9zacm0vOO1dXypU77N4"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

# ===== КНОПКИ =====

gender_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
gender_kb.add("Мужчина", "Женщина")

activity_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
activity_kb.add(
    "🛋 Сидячий",
    "🚶 Лёгкая",
    "🏃 Средняя",
    "🏋️ Высокая",
    "🔥 Очень высокая"
)

nav_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
nav_kb.add("⬅️ Назад", "🔄 Начать заново")

activity_map = {
    "🛋 Сидячий": 1.2,
    "🚶 Лёгкая": 1.375,
    "🏃 Средняя": 1.55,
    "🏋️ Высокая": 1.725,
    "🔥 Очень высокая": 1.9
}

# ===== START =====

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    uid = str(message.from_user.id)

    user_data[uid] = {
        "step": 1
    }

    await message.answer(
        "💪 Йоу! Давай рассчитаем твой дефицит калорий\n\n"
        "Шаг 1/4 — выбери пол:",
        reply_markup=gender_kb
    )

# ===== ПОЛ =====

@dp.message_handler(lambda m: m.text in ["Мужчина", "Женщина"])
async def gender(message: types.Message):
    uid = str(message.from_user.id)

    user_data[uid]["gender"] = message.text
    user_data[uid]["step"] = 2

    await message.answer("📅 Шаг 2/4 — введи возраст:")

# ===== ЧИСЛА =====

@dp.message_handler(lambda m: m.text.isdigit())
async def numbers(message: types.Message):
    uid = str(message.from_user.id)

    if uid not in user_data:
        await message.answer("Нажми /start")
        return

    u = user_data[uid]

    if "age" not in u:
        u["age"] = int(message.text)
        u["step"] = 3
        await message.answer("📏 Шаг 3/4 — рост (см):")

    elif "height" not in u:
        u["height"] = int(message.text)
        u["step"] = 4
        await message.answer("⚖️ Шаг 4/4 — вес (кг):")

    elif "weight" not in u:
        u["weight"] = int(message.text)
        u["step"] = 5

        await message.answer(
            "🔥 Выбери активность:",
            reply_markup=activity_kb
        )

# ===== РАСЧЁТ + БЖУ =====

@dp.message_handler(lambda m: m.text in activity_map)
async def calc(message: types.Message):
    uid = str(message.from_user.id)
    u = user_data.get(uid)

    if not u:
        await message.answer("Нажми /start")
        return

    required = ["gender", "age", "height", "weight"]

    for r in required:
        if r not in u:
            await message.answer("⚠️ Сначала пройди /start")
            return

    gender = u["gender"]
    age = u["age"]
    height = u["height"]
    weight = u["weight"]

    activity = activity_map[message.text]

    # BMR
    if gender == "Мужчина":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity
    cut = tdee * 0.8

    # ===== БЖУ =====
    protein = weight * 2
    fat = weight * 0.8
    carbs = (cut - (protein * 4 + fat * 9)) / 4

    await message.answer(
        f"📊 РЕЗУЛЬТАТ\n\n"
        f"🔥 Калории (похудение): {round(cut)} ккал\n\n"
        f"🥩 Белки: {round(protein)} г\n"
        f"🥑 Жиры: {round(fat)} г\n"
        f"🍚 Углеводы: {round(carbs)} г\n\n"
        f"⚡ Поддержание: {round(tdee)} ккал\n\n"
        "Хочешь пересчитать? /start"
    )

# ===== ЗАПУСК =====

if __name__ == "__main__":
    print("BOT STARTING...")
    executor.start_polling(dp)