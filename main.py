import asyncio
import requests
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove



bot = Bot(token = "secret xD")
API = "2ce80ab55efff7d78fc31f1868ec0dcf"

dp = Dispatcher()

kb_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Узнать прогноз погоды")
        ],
        [
            KeyboardButton(text="Ежедневник")
        ],
    ],
    resize_keyboard=True, input_field_placeholder="Выберите нужный вариант"
)

kb_weather = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Узнать какой сейчас прогноз погоды")
        ],
        [
            KeyboardButton(text="Узнать погоду на ближайшие 4 дня")
        ],
    ],
    resize_keyboard=True, input_field_placeholder="Выберите нужный вариант"
)

del_kbd = ReplyKeyboardRemove()

class AddWeather(StatesGroup):
    city_name = State()
    weather_choise = State()

    texts = {
        'AddWeather:city_name': 'Введите город заново:',
        'AddWeather:weather_choise': "Выберите заново необходимые действия"
    }

your_city = ""

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Для того чтобы вернуться к предыдущему шагу напишите в чате слово назад\nДля того чтобы вернуться к меню напишите слово отмена в чате")
    await message.answer("Выберите нужный вариант:", reply_markup=kb_start)

@dp.message(StateFilter(None), F.text == "Узнать прогноз погоды")
async def start_weather(message: types.Message, state: FSMContext):
    await message.answer("Напишите название города или населённого пункта", reply_markup=del_kbd)
    await state.set_state(AddWeather.city_name)

@dp.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=kb_start)

@dp.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddWeather.city_name:
        await message.answer('Предыдущего шага нет, или введите название города или напишите "отмена"')
        return

    previous = None
    for step in AddWeather.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddWeather.texts[previous.state]}")
            return
        previous = step

@dp.message(AddWeather.city_name, F.text)
async def weather_choise(message: types.Message, state: FSMContext):
    your_city = message.text

    for i in your_city:
        if i.isdigit():
            await message.answer("Вы ввели недопустимое название города \nВведите заново")
            return

    await message.answer(f"Вы выбрали город: {your_city}")
    await state.update_data(city_name=your_city)
    await message.answer("Выберите необходимое действие", reply_markup=kb_weather)
    await state.set_state(AddWeather.weather_choise)

@dp.message(AddWeather.weather_choise, F.text == "Узнать какой сейчас прогноз погоды")
async def weather_now(message: types.Message, state: FSMContext):
    data = await state.get_data()
    your_city = data.get("city_name")

    try:
        now = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={your_city}&appid={API}&units=metric", timeout=10)  # Таймаут 10 секунд
        now.raise_for_status()  # Проверка на наличие ошибок HTTP

        json_data = now.json()
        await message.answer(f"Погода сейчас: {json_data['main']['temp']}°C", reply_markup=kb_start)

    except requests.exceptions.Timeout:
        await message.answer("Запрос к серверу превысил время ожидания. Попробуйте позже.")
    except requests.exceptions.RequestException as e:
        await message.answer(f"Произошла ошибка при выполнении запроса: {e}")
    else:
        # Этот блок выполняется, только если ошибок не было
        await state.update_data(weather_choise=message.text)
        data = await state.get_data()  # Пример использования данных из состояния
    finally:
        await state.clear()

async def main():
    await dp.start_polling(bot)
    await bot.delete_webhook(drop_pending_updates=True)

asyncio.run(main())

# Здесь был Матвей
