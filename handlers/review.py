from aiogram import types, Dispatcher
from keyboards import back
from aiogram.dispatcher import FSMContext
from bot_manager import StQuiz, bot, admin_id, URI
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
    comment = message.text
    user_id = message.from_user.id
    name = message.from_user.full_name
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute("INSERT INTO comment (comment, user_id, user_name) VALUES (%s, %s, %s)", (comment, user_id, name))
        await message.answer('Сообщение успешно отправлено!', reply_markup=back())
        await state.finish()
    except Exception as e:
        await message.answer("Не удалось подключиться к серверу... Попробуйте оставить отзыв позже😉")
        await bot.send_message(admin_id, f'Что-то пошло не так в "comment.py", вот:\n{e}', disable_notification=True)


def register_handlers_review(dp: Dispatcher):
    dp.register_callback_query_handler(review_request, text='review')
    dp.register_message_handler(review_command, commands='review')
    dp.register_message_handler(apply, state=StQuiz.waiting_comment)
