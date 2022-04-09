import psycopg2
import time
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from bot_manager import URI


async def del_from_db():
    with psycopg2.connect(URI) as db:
        db.autocommit = True
        cursor = db.cursor()
        cursor.execute("SELECT count(*) FROM my_users WHERE user_name LIKE 'person%'")
        all_test_users = cursor.fetchone()[0]
        cursor.execute("DELETE FROM my_users WHERE user_name LIKE 'person%'")
        return all_test_users


async def insert_in_db(number):
    with psycopg2.connect(URI) as db:
        db.autocommit = True
        cursor = db.cursor()
        cursor.execute("INSERT INTO my_users (user_id, user_name, amount_query) VALUES (%s, %s, 1)",
                        (number * 317, f'person{number}'))



async def db_test(message: types.Message):
    input_users = int(message.text.split('_')[2])
    try:
        start = time.time()
        for request in range(1, input_users):
            await insert_in_db(request)
        finish = time.time()
        users = await del_from_db()
        await message.answer(f'тест на отказоустойчивость СУБД выполнен! Отчёт:\nКоличество введённых тестовых записей: {input_users}\n'
                             f'Количество записанных тестовых записей: {users}\n Время выполнения: {finish - start} секунд')
    except Exception as e:
        await message.answer(f"Ошибка: {e}")



def register_tests(dp: Dispatcher):
    dp.register_message_handler(db_test, Text(startswith='db_test'))
