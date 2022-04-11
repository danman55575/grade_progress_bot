from aiogram import types, Dispatcher
from bot_manager import StQuiz, admin_id, bot, URI
from keyboards import adminreply
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher import FSMContext
import psycopg2


async def admintable(msg: types.Message):
    adminboard = types.InlineKeyboardMarkup(row_width=1)
    adminboard.add(types.InlineKeyboardButton(text='Выборка из бд', callback_data='look_table'),
                    types.InlineKeyboardButton(text='Работа с бд', callback_data='change_table'),
                    types.InlineKeyboardButton(text='Рассылка', callback_data='send'))
    await msg.answer(f'Привет, {msg.from_user.full_name}, {msg.from_user.username}!\nТвой id: {msg.from_user.id}\n')
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute("SELECT count(*) FROM my_users")
            count_users = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM comment")
            count_comments = cursor.fetchone()[0]
        await msg.answer(f'количество отзывов: {count_comments}'
                         f'\nколичество пользователей: {count_users}', reply_markup=adminboard)
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')



async def look_table(call: types.CallbackQuery):
    text = ''
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute("SELECT id, user_name, comment FROM comment")
            for i in cursor.fetchmany(3):
                text += f'\n{i}'
            await call.message.answer(f'Вывод первых 3-х отзывов:{text}')
        await call.message.answer('Жду SQL-запрос для выборки данных🕐')
        await StQuiz.look_table.set()
    except Exception as e:
        await call.message.answer(f'Что-то пошло не так, вот:\n{e}')


async def output_result(msg: types.Message, state: FSMContext):
    text = ''
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute(msg.text)
            for i in cursor.fetchall():
                text += f'\n{i}'
            await msg.answer(f'✅Выборка прошла успешно:{text}', reply_markup=adminreply())
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        await state.finish()


async def change_bd(call: types.CallbackQuery):
    await call.message.answer('Отправь SQL-запрос')
    await call.answer('ВНЕСЕНИЕ ИЗМЕНЕНИЙ В БД!')
    await StQuiz.del_note.set()


async def output_note(msg: types.Message, state: FSMContext):
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute(msg.text)
            await msg.answer('Успешно выполнено!', reply_markup=adminreply())
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        await state.finish()


async def notification_out(call: types.CallbackQuery):
    await call.message.answer("Рассылка будет отправлена с функцией отключения звука.\nНапиши текст сообщения, который"
                              "будет отправлен всем использовавшим данный бот пользователям")
    await StQuiz.waiting_text_for_sending.set()


async def sending_process(message: types.Message):
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute("SELECT user_id FROM my_users")
            all_id = cursor.fetchall()
            for user_id in all_id:
                await bot.send_message(chat_id=user_id[0], text=message.text)
            await message.answer("Рассылка проведена успешно!")
    except Exception as e:
        await message.answer(f"Что-то пошло не так! {e}")




def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admintable, IDFilter(admin_id), commands='admin3027')
    dp.register_callback_query_handler(look_table, text='look_table')
    dp.register_message_handler(output_result, state=StQuiz.look_table)
    dp.register_callback_query_handler(change_bd, text='change_bd')
    dp.register_message_handler(output_note, state=StQuiz.del_note)
    dp.register_callback_query_handler(notification_out, text='send')
    dp.register_message_handler(sending_process, state=StQuiz.waiting_text_for_sending)
