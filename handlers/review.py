from aiogram import types, Dispatcher
from keyboards import back
from aiogram.dispatcher import FSMContext
from bot_manager import StQuiz, bot, admin, URI
import psycopg2


async def review_request(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer('Напишите нам, что вас не устраивает или что бы вы нам посоветовали.',
                              reply_markup=back())
    await StQuiz.waiting_comment.set()


async def review_command(message: types.Message):
    await message.answer('Напишите нам, что вас не устраивает или что бы вы нам посоветовали.',
                              reply_markup=back())
    await StQuiz.waiting_comment.set()


async def apply(message: types.Message, state: FSMContext):
    db = psycopg2.connect(URI)
    db.autocommit = True
    cursor = db.cursor()
    try:
        comment = message.text
        user_id = message.from_user.id
        name = message.from_user.full_name
        cursor.execute("INSERT INTO comment (comment, user_id, user_name) VALUES (%s, %s, %s)", (comment, user_id, name))
    except Exception as e:
        await bot.send_message(admin, f'Что-то пошло не так в "comment.py", вот:\n{e}', disable_notification=True)
    finally:
        if db:
            db.close()
    await message.answer('Сообщение успешно отправлено!', reply_markup=back())
    await state.finish()


def register_handlers_comment(dp: Dispatcher):
    dp.register_callback_query_handler(review_request, text='review')
    dp.register_message_handler(review_command, commands='review')
    dp.register_message_handler(apply, state=StQuiz.waiting_comment)
