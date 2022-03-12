from aiogram import types, Dispatcher
from bot_manager import StQuiz, admin
from aiogram.dispatcher import FSMContext
from keyboards import adminlookboard, admindeleteboard
import sqlite3


async def admintable(msg: types.Message):
    if msg.from_user.id == admin:
        adminboard = types.InlineKeyboardMarkup(row_width=1)
        adminboard.add(types.InlineKeyboardButton(text='Выборка из бд', callback_data='look_table'),
                       types.InlineKeyboardButton(text='Работа с бд', callback_data='change_bd'))
        await msg.answer(f'Привет, {msg.from_user.full_name}, {msg.from_user.username}!\nТвой id: {msg.from_user.id}\n')
        db = sqlite3.connect('grade_progress_bot.db')
        cursor = db.cursor()
        try:
            count_comments = cursor.execute("SELECT count() FROM comment").fetchone()[0]
            count_users = cursor.execute("SELECT count() FROM my_users").fetchone()[0]
            await msg.answer(f'количество отзывов: {count_comments}'
                             f'\nколичество пользователей: {count_users}', reply_markup=adminboard)
        except Exception as e:
            await msg.answer(f'Что-то пошло не так, вот:\n{e}')
        finally:
            if db:
                db.close()


async def my_table(call: types.CallbackQuery):
    db = sqlite3.connect('grade_progress_bot.db')
    cursor = db.cursor()
    text = ''
    try:
        for i in cursor.execute("SELECT id, name, comment FROM comment").fetchmany(3):
            text += f'\n{i}'
        await call.message.answer(f'Вывод первых 3-х отзывов:{text}')
        await call.message.answer('Теперь надо отправить SQL-запрос для выборки данных\nSELECT name, comment.comment '
                                  'FROM my_users LEFT JOIN comment ON my_users.user_id == comment.user_id',
                                  reply_markup=adminlookboard())
        await StQuiz.look_table.set()
    except Exception as e:
        await call.message.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await call.answer('База данных закрыта')


async def output_note(msg: types.Message, state: FSMContext):
    db = sqlite3.connect('grade_progress_bot.db')
    cursor = db.cursor()
    text = ''
    try:
        for i in cursor.execute(msg.text).fetchall():
            text += f'\n{i}'
        await msg.answer(f'✅Выборка прошла успешно:{text}')
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await msg.answer('✅База данных успешно закрыта!')
            await state.finish()


async def change_bd(call: types.CallbackQuery):
    await call.message.answer('Отправь SQL-запрос',
                              reply_markup=admindeleteboard())
    await call.answer('РАБОТА С БД!')
    await StQuiz.del_note.set()


async def output_result(msg: types.Message, state: FSMContext):
    db = sqlite3.connect('grade_progress_bot.db')
    cursor = db.cursor()
    try:
        cursor.execute(msg.text)
        db.commit()
        await msg.answer('Успешно выполнено!')
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await msg.answer('✅База данных успешно закрыта!')
            await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admintable, commands='admin3027')
    dp.register_message_handler(admintable, text='security_piano_Gmoll_admin')
    dp.register_callback_query_handler(my_table, text='look_table')
    dp.register_message_handler(output_note, state=StQuiz.look_table)
    dp.register_callback_query_handler(change_bd, text='change_bd')
    dp.register_message_handler(output_result, state=StQuiz.del_note)
