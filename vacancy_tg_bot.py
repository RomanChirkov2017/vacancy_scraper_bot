import json
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


import os
from dotenv import load_dotenv

from main import collect_hh_data, collect_sj_data

load_dotenv(".env")

token = os.getenv("TOKEN")

class SearchState(StatesGroup):
    waiting_for_keywords_hh = State()
    waiting_for_keywords_sj = State()
    waiting_for_keywords_both = State()

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def send_vacancy_card(message: types.Message, item):
    card = f'{hlink(item.get("name"), item.get("url"))}\n' \
           f'{hbold("Зарплата от: ")}{item.get("salary_from"), item.get("currency")}\n' \
           f'{hbold("Зарплата до: ")}{item.get("salary_to"), item.get("currency")}\n' \
           f'{hbold("Описание: ")}{item.get("description")}'
    await message.answer(card)
    await asyncio.sleep(1)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_buttons = ['HeadHunter', 'SuperJob', 'Обе платформы']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.reply("Привет, это бот для поиска вакансий!")
    await message.answer("Выберите платформу для поиска:", reply_markup=keyboard)


@dp.message_handler(Text(equals='HeadHunter'), state='*')
async def get_hh_vacancy(message: types.Message, state: FSMContext):
    await SearchState.waiting_for_keywords_hh.set()
    await message.answer('Введите ключевые слова для поиска через пробел: ')

@dp.message_handler(state=SearchState.waiting_for_keywords_hh)
async def process_keywords(message: types.Message, state: FSMContext):
    keywords = message.text.lower()

    await message.answer('Сбор данных. Пожалуйста, подождите...')

    await collect_hh_data(keywords)

    with open('vacancies_hh.json', 'r') as file:
        data = json.load(file)

    await message.answer(f'Найдено вакансий: {len(data)}.')

    for item in data:
        await send_vacancy_card(message, item)
        await state.finish()


@dp.message_handler(Text(equals='SuperJob'), state='*')
async def get_sj_vacancy(message: types.Message, state: FSMContext):
    await SearchState.waiting_for_keywords_sj.set()
    await message.answer('Введите ключевые слова для поиска через пробел: ')

@dp.message_handler(state=SearchState.waiting_for_keywords_sj)
async def process_keywords(message: types.Message, state: FSMContext):
    keywords = message.text.lower()

    await message.answer('Сбор данных. Пожалуйста, подождите...')

    await collect_sj_data(keywords)

    with open('vacancies_sj.json', 'r') as file:
        data = json.load(file)

    await message.answer(f'Найдено вакансий: {len(data)}.')

    for item in data:
        await send_vacancy_card(message, item)
        await state.finish()


@dp.message_handler(Text(equals='Обе платформы'), state='*')
async def get_both_vacancy(message: types.Message, state: FSMContext):
    await SearchState.waiting_for_keywords_both.set()
    await message.answer('Введите ключевые слова для поиска через пробел: ')


@dp.message_handler(state=SearchState.waiting_for_keywords_both)
async def process_keywords_both(message: types.Message, state: FSMContext):
    keywords = message.text.lower()

    await message.answer('Сбор данных. Пожалуйста, подождите...')

    await collect_hh_data(keywords)
    await collect_sj_data(keywords)

    with open('vacancies_hh.json', 'r') as file:
        data_hh = json.load(file)


    with open('vacancies_sj.json', 'r') as file:
        data_sj = json.load(file)

    await message.answer(f'Найдено вакансий: {len(data_hh) + len(data_sj)}.')

    for item in data_hh:
        await send_vacancy_card(message, item)

    for item in data_sj:
        await send_vacancy_card(message, item)

    await state.finish()



def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    main()