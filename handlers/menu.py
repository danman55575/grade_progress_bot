from aiogram import types, Dispatcher
from bot_manager import bot, admin_id, URI
from keyboards import back
from aiogram.dispatcher import FSMContext
import psycopg2
instruction = """Инструкция по использованию <b>GradeProgress Bot</b>:

1️⃣Кнопка <b>Начать</b> - приступить к опросу. Процесс опроса:
  1-й этап. Ввод желаемого среднего балла;
  2-й этап. Выбор способа расчёта:

    1)"Количество отметок":
      3-й этап. Ввод текущего количества отметок
      4-й этап. Ввод текущего среднего балла

    2)"Последовательность":
      3-й этап. Ввод последовательности отметок

2️⃣Кнопка <b>Оставить отзыв</b> - оценить бота. Так вы сможете повлиять на дальнейшее развитие бота 

3️⃣Кнопка <b>Помощь</b> - показать инструкцию по использованию <b>GradeProgress Bot</b>
"""


async def main(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.full_name
    try:
        with psycopg2.connect(URI) as db:
            db.autocommit = True
            cursor = db.cursor()
            cursor.execute("SELECT user_id FROM my_users")
            all_users = cursor.fetchall()
        if (user_id,) in all_users:
            cursor.execute("UPDATE my_users SET amount_query = amount_query + 1 WHERE user_id = %s", (user_id,))
        else:
            cursor.execute("INSERT INTO my_users (user_id, amount_query, user_name) VALUES (%s, %s, %s)", (user_id, 1, name))
    except Exception as e:
        await bot.send_message(admin_id, f'Что-то пошло не так в модуле "menu.py", вот:\n{e}', disable_notification=True)
    finally:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(text='Начать!', callback_data='begin'),
                   types.InlineKeyboardButton(text='Помощь', callback_data='help'),
                   types.InlineKeyboardButton(text='Оставить отзыв📢', callback_data='review')]
        keyboard.add(*buttons)
        await message.answer('Привет! Это <b>главное меню</b>, здесь представлены все основные функции '
                             'бота <i>GradeProgress Bot</i>.', reply_markup=keyboard)
        await state.finish()


async def help_list_call(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(instruction, reply_markup=back())


async def help_list_msg(message: types.Message):
    await message.answer(instruction, reply_markup=back())


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(main, commands='start', state='*')
    dp.register_message_handler(main, text='В меню', state='*')
    dp.register_message_handler(help_list_msg, commands='help')
    dp.register_callback_query_handler(help_list_call, text='help')
