from aiogram import types, Dispatcher
from keyboard import back
from aiogram.dispatcher import FSMContext
from bot_manager import StQuiz, bot, admin
import sqlite3


async def idea(call: types.CallbackQuery):
    await call.message.answer('Напишите нам, что вас не устраивает или что бы вы нам посоветовали.',
                              reply_markup=back())
    await StQuiz.waiting_comment.set()


async def apply(message: types.Message, state: FSMContext):
    db = sqlite3.connect('grade_progress_bot.db')
    cursor = db.cursor()
    try:
        comment = message.text
        user_id = message.from_user.id
        name = message.from_user.full_name
        cursor.execute("INSERT INTO comment ('comment', 'user_id', 'name') VALUES (?,?,?)", (comment, user_id, name))
        db.commit()
    except Exception as e:
        await bot.send_message(admin, f'Что-то пошло не так в "comment.py", вот:\n{e}', disable_notification=True)
    finally:
        if db:
            db.close()
    await message.answer('Сообщение успешно отправлено!', reply_markup=back())
    await state.finish()


def register_handlers_comment(dp: Dispatcher):
    dp.register_callback_query_handler(idea, text='review')
    dp.register_message_handler(apply, state=StQuiz.waiting_comment)
