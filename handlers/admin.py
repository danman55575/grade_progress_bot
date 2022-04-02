from aiogram import types, Dispatcher
from bot_manager import StQuiz, admin, bot, URI
from aiogram.dispatcher import FSMContext
from keyboards import adminlookboard, admindeleteboard, adminreply
import psycopg2


async def admintable(msg: types.Message):
    if msg.from_user.id == admin:
        adminboard = types.InlineKeyboardMarkup(row_width=1)
        adminboard.add(types.InlineKeyboardButton(text='Выборка из бд', callback_data='look_table'),
                       types.InlineKeyboardButton(text='Работа с бд', callback_data='change_table'),
                       types.InlineKeyboardButton(text='Отправить', callback_data='send'))
        await msg.answer(f'Привет, {msg.from_user.full_name}, {msg.from_user.username}!\nТвой id: {msg.from_user.id}\n')
        db = psycopg2.connect(URI)
        db.autocommit = True
        cursor = db.cursor()
        try:
            cursor.execute("SELECT count(*) FROM comment")
            count_comments = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM my_users")
            count_users = cursor.fetchone()[0]
            await msg.answer(f'количество отзывов: {count_comments}'
                             f'\nколичество пользователей: {count_users}', reply_markup=adminboard)
        except Exception as e:
            await msg.answer(f'Что-то пошло не так, вот:\n{e}')
        finally:
            if db:
                db.close()


async def look_table(call: types.CallbackQuery):
    db = psycopg2.connect(URI)
    db.autocommit = True
    cursor = db.cursor()
    text = ''
    try:
        cursor.execute("SELECT id, user_name, comment FROM comment")
        for i in cursor.fetchmany(3):
            text += f'\n{i}'
        await call.message.answer(f'Вывод первых 3-х отзывов:{text}')
        await call.message.answer('Теперь надо отправить SQL-запрос для выборки данных', reply_markup=adminlookboard())
        await StQuiz.look_table.set()
    except Exception as e:
        await call.message.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await call.answer('База данных закрыта')


async def output_result(msg: types.Message, state: FSMContext):
    db = psycopg2.connect(URI)
    db.autocommit = True
    cursor = db.cursor()
    text = ''
    try:
        cursor.execute(msg.text)
        for i in cursor.fetchall():
            text += f'\n{i}'
        await msg.answer(f'✅Выборка прошла успешно:{text}')
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await state.finish()
            await msg.answer('✅База данных успешно закрыта!', reply_markup=adminreply())


async def change_bd(call: types.CallbackQuery):
    await call.message.answer('Отправь SQL-запрос',
                              reply_markup=admindeleteboard())
    await call.answer('ВНЕСЕНИЕ ИЗМЕНЕНИЙ В БД!')
    await StQuiz.del_note.set()


async def output_note(msg: types.Message, state: FSMContext):
    db = psycopg2.connect(URI)
    db.autocommit = True
    cursor = db.cursor()
    try:
        cursor.execute(msg.text)
        await msg.answer('Успешно выполнено!')
    except Exception as e:
        await msg.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await state.finish()
            await msg.answer('✅База данных успешно закрыта!', reply_markup=adminreply())


async def notification_out(call: types.CallbackQuery):
    db = psycopg2.connect(URI)
    db.autocommit = True
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM my_users")
        all_id = cursor.fetchall()
        for i in all_id:
            await bot.send_message(i[0], "Бот временно недоступен! Просим извинения за доставленные неудобства.\n"
                                         "  <i>GradeProgress Bot</i>", disable_notification=True)
    except Exception as e:
        await call.message.answer(f'Что-то пошло не так, вот:\n{e}')
    finally:
        if db:
            db.close()
            await call.message.answer('✅База данных успешно закрыта!\nРассылка проведена успешно!', reply_markup=adminreply())


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admintable, commands='admin3027')
    dp.register_message_handler(admintable, text='security_piano_Gmoll_admin')
    dp.register_callback_query_handler(look_table, text='look_table')
    dp.register_message_handler(output_result, state=StQuiz.look_table)
    dp.register_callback_query_handler(change_bd, text='change_bd')
    dp.register_message_handler(output_note, state=StQuiz.del_note)
    dp.register_callback_query_handler(notification_out, text='send')
