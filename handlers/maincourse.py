from aiogram import Dispatcher
from bot_manager import dp, bot, StQuiz
from keyboards import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import re
data = dict()
# data['amount_grades'] - количество отметок
# data['score_purpose'] - желаемый средний балл
# data['current_score'] - текущий средний балл
# data['tap_amount'] - пользовательское количество отметок
# basa[(оценка, номер оценки, средний балл)] - кортеж в списке


async def begin(call: types.CallbackQuery):
    global data
    user_id = call.from_user.id
    data[user_id] = dict()
    data[user_id]['basa'] = []
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Пожалуйста, введи желаемый средний балл.', reply_markup=scoreboard())
    await StQuiz.waiting_purpose_score.set()


async def purpose_score(message: types.Message):
    global data
    user_id = message.from_user.id
    try:
        if 2 < float(message.text) <= 5:
            data[user_id]["score_purpose"] = float(message.text)
            await message.answer('✅\nОтлично, выбери способ расчёта👇\n"Последовательность📊" - ввести последовательность отметок\n"Количество🧮" - ввести текущий средний балл и количество отметок', reply_markup=choose_way())
            await StQuiz.next()
        else:
            await message.answer('❌\nМеня не обманешь😏Ну так, каков желаемый средний балл?')
    except:
        await message.reply('❌\nОшибка🙁 Введи желаемый средний балл ещё раз.\nНе забывай, что в качестве '
                            'десятичного разделителя я принимаю "."\nВерно    👉"4.50"\nНеверно    👉"4,50".')


async def cross(message: types.Message):
    if message.text == 'Последовательность📊':
        await message.answer('✅\nОтлично,теперь введи свои оценки (можешь скопировать и вставить из эл. дневника)',
                             reply_markup=againboard())
        await StQuiz.next()
    elif message.text == 'Количество🧮':
        await message.answer('✅\nТвой средний балл на настоящий момент?', reply_markup=againboard())
        await StQuiz.waiting_present_score.set()
    elif message.text == 'Назад↩':
        await message.answer('Я тебя понял, жду желаемый средний балл🕐', reply_markup=scoreboard())
        await StQuiz.waiting_purpose_score.set()
    else:
        await message.answer('Давай выберем способ расчёта👇')


async def list_calc(message: types.Message, state: FSMContext):
    global data, text
    user_id = message.from_user.id
    try:
        if message.text == 'Назад↩':
            await message.reply('<s>Что, опять?</s>\nВыбирай подходящий способ расчёта👇', reply_markup=choose_way())
            await StQuiz.waiting_way_calc.set()
        else:
            text = ''
            grades = ''.join(re.split('[ ,\n]', message.text))
            data[user_id]['summa'] = 0
            data[user_id]['amount_grades'] = 0
            for grade in grades:
                data[user_id]['summa'] += int(grade)
                data[user_id]['amount_grades'] += 1
            await calc_grade(5, 0, data[user_id]['score_purpose'], data[user_id]['amount_grades'], data[user_id]['summa'], user_id)
            await message.reply(f'Вот ответ:' + text, reply_markup=finishboard())
            await state.finish()
    except:
        await message.answer('❌ Ошибка🙁\nПопробуй ввести свои оценки ещё раз.')


async def present_score(message: types.Message):
    global data
    user_id = message.from_user.id
    try:
        if message.text == 'Назад↩':
            await message.reply('Выбирай подходящий способ расчёта👇', reply_markup=choose_way())
            await StQuiz.waiting_way_calc.set()
        else:
            data[user_id]["current_score"] = float(message.text)
            if data[user_id]["current_score"] >= data[user_id]['score_purpose']:
                await message.reply('Твой текущий средний балл больше желаемого, введи средний балл ещё раз.')
                await message.answer(f'Введённые данные:\nЖелаемый средний балл 👉{data[user_id]["score_purpose"]}'
                                     f'\nТекущий средний балл 👉{data[user_id]["current_score"]}')
            else:
                await message.answer('Хорошо, теперь введи количество отметок', reply_markup=againboard())
                await StQuiz.next()
    except:
        await message.answer('❌\nОшибка🙁 Введи текущий средний балл ещё раз.\nНе забывай, что в качестве '
                             'десятичного разделителя я принимаю "."\n❌Неверно    👉"4,50"\n✅Верно    👉"4.50".')


async def amount_calc(message: types.Message, state: FSMContext):
    global data, text
    user_id = message.from_user.id
    try:
        if message.text == 'Назад↩':
            await message.reply('Перезапишем твой текущий средний балл', reply_markup=againboard())
            await StQuiz.waiting_present_score.set()
        else:
            text = ''
            data[user_id]['amount_grades'] = int(message.text)
            data[user_id]['summa'] = data[user_id]['current_score'] * data[user_id]['amount_grades']
            await calc_grade(5, 0, data[user_id]['score_purpose'], data[user_id]['amount_grades'], data[user_id]['summa'], user_id)
            await message.reply(f'Вот ответ:' + text, reply_markup=finishboard())
            await state.finish()
    except:
        await message.reply('❌\nОшибка🙁 Введи количество отметок, стоящих у тебя в дневнике, ещё раз.')


async def calc_grade(grade, answer, score, amount, summa, user_id):
    global text, data
    a = []
    nowscore = summa / amount
    while score > round(nowscore, 2):
        summa += grade
        amount += 1
        answer += 1
        nowscore = summa / amount
        a.append((grade, answer, round(nowscore, 4)))
        if answer > 99:
            text += f'\nКоличество отметок {grade} превосходит 99.'
            break
    if answer < 100:
        text += f'\nКоличество отметок "{grade}" равно {answer}'
        if 0 < len(a) <= 5:
            for i in range(-1, -len(a) - 1, -1):
                data[user_id]['basa'].append(a[i])
        else:
            for i in range(-1, -6, -1):
                data[user_id]['basa'].append(a[i])
    if grade - 1 > score:
        await calc_grade(grade - 1, answer, score, amount, summa - answer, user_id)


async def table(message: types.Message):
    global data
    user_id = message.from_user.id
    data[user_id]['basa'].reverse()
    table3, table4, table5 = '', '', ''
    for i in data[user_id]['basa']:
        grade, answer, nowscore = i
        if grade == 5:
            table5 += f'\nПри {answer:2}-ой отметке "5" средний балл:   👉{nowscore}'
        elif grade == 4:
            table4 += f'\nПри {answer:2}-ой отметке "4" средний балл:  👉{nowscore}'
        elif grade == 3:
            table3 += f'\nПри {answer:2}-ой отметке "3" средний балл:  👉{nowscore}'
    if table5 == '':
        await message.answer(f'Количество отметок больше 99!\nПроверь введённые данные на наличие ошибки👆', reply_markup=back())
    else:
        await message.answer(f'📋Мини-табель "Прогресс" при получении отметки "5":' + table5, reply_markup=finish2())
    if table4 != '':
        await message.answer(f'📋Мини-табель "Прогресс" при получении отметки "4":' + table4)
    if table3 != '':
        await message.answer(f'📋Мини-табель "Прогресс" при получении отметки "3":' + table3)


def get_keyboard():
    buttons = [types.InlineKeyboardButton(text="3", callback_data="num_3"),
        types.InlineKeyboardButton(text="4", callback_data="num_4"),
        types.InlineKeyboardButton(text="5", callback_data="num_5"),
        types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish"),
        types.InlineKeyboardButton(text="1", callback_data="num_1"),
        types.InlineKeyboardButton(text="2", callback_data="num_2")]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard


async def cmd_numbers(message: types.Message):
    global data
    user_id = message.from_user.id
    data[user_id]['addit'] = []
    data[user_id]['current_score'] = data[user_id]['summa'] / data[user_id]['amount_grades']
    data[user_id]['tap_amount'] = 0
    await message.answer(f"<b>Укажите оценку</b>👇\nДополнительные отметки:{data[user_id]['addit']}\n"
                         f"Средний балл: {data[user_id]['current_score']}", reply_markup=get_keyboard())


async def update_num_text(message: types.Message, grade, user_id):
    global data
    data[user_id]['tap_amount'] += 1
    data[user_id]['amount_grades'] += 1
    data[user_id]['summa'] += int(grade)
    data[user_id]['current_score'] = data[user_id]['summa'] / data[user_id]['amount_grades']
    await message.edit_text(f"<b>Укажите оценку</b>👇\n"
                            f"Дополнительные отметки: {data[user_id]['addit']}\nВаш средний балл: {data[user_id]['current_score']:.5}",
                            reply_markup=get_keyboard())


async def callbacks_num(call: types.CallbackQuery):
    global data
    user_id = call.from_user.id
    action = call.data.split("_")[1]
    if action == "5":
        data[user_id]['addit'].append('5')
        await update_num_text(call.message, 5, user_id)
    elif action == "4":
        data[user_id]['addit'].append('4')
        await update_num_text(call.message, 4, user_id)
    elif action == "3":
        data[user_id]['addit'].append('3')
        await update_num_text(call.message, 3, user_id)
    elif action == "2":
        data[user_id]['addit'].append('2')
        await update_num_text(call.message, 2, user_id)
    elif action == "1":
        data[user_id]['addit'].append('1')
        await update_num_text(call.message, 1, user_id)
    elif action == "finish":
        await call.message.edit_text(f"Итого:\nВсего отметок: {data[user_id]['amount_grades']}"
                                     f"\nКоличество дополнительных отметок: {data[user_id]['tap_amount']}\n"
                                     f"История ввода отметок: {data[user_id]['addit']}")
        await call.message.answer(f"Полученный средний балл:  <b>{data[user_id]['current_score']:.5}</b>"
                                  f"\nЦелевой средний балл:  <b>{data[user_id]['score_purpose']}</b>", reply_markup=back())
    await call.answer()


def register_handlers_maincourse(dp: Dispatcher):
    dp.register_callback_query_handler(begin, text='begin')
    dp.register_message_handler(purpose_score, state=StQuiz.waiting_purpose_score)
    dp.register_message_handler(cross, state=StQuiz.waiting_way_calc)
    dp.register_message_handler(list_calc, state=StQuiz.waiting_list_calc)
    dp.register_message_handler(present_score, state=StQuiz.waiting_present_score)
    dp.register_message_handler(amount_calc, state=StQuiz.waiting_amount_calc)
    dp.register_message_handler(table, text='Узнать больше📈')
    dp.register_message_handler(cmd_numbers, text='Прогноз')
    dp.register_callback_query_handler(callbacks_num, Text(startswith='num_'))

