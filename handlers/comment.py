from aiogram import types, Dispatcher
from keyboards import back
from aiogram.dispatcher import FSMContext
from bot_manager import StQuiz, bot, admin
import psycopg2


async def idea(call: types.CallbackQuery):
    await call.message.answer('Напишите нам, что вас не устраивает или что бы вы нам посоветовали.',
                              reply_markup=back())
    await StQuiz.waiting_comment.set()


async def apply(message: types.Message, state: FSMContext):
    db = psycopg2.connect('postgres://sbfqqjimvvqzyc:05185c25d6ef587b7cb9f85541a9902030e39dabe606c765a6f77ea9da80c544'
                          '@ec2-54-74-14-109.eu-west-1.compute.amazonaws.com:5432/d4eaaaje408rv8')
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
    dp.register_callback_query_handler(idea, text='review')
    dp.register_message_handler(apply, state=StQuiz.waiting_comment)
