from aiogram import types


# Простая подсказка 'В меню'
def back():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('В меню'))
    return markup


# После нажатия 'Узнать больше📈'
def finish2():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Прогноз'), types.KeyboardButton('В меню'))
    return markup


# Выбор способа расчёта
def choose_way():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    item1 = types.KeyboardButton('Последовательность📊')
    item2 = types.KeyboardButton('Количество🧮')
    item3 = types.KeyboardButton('Назад↩')
    item4 = types.KeyboardButton('В меню')
    markup.add(item1, item2).row(item3, item4)
    return markup


# В состоянии выбора желаемого среднего балла
def scoreboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4,
                                       input_field_placeholder='Ввести желаемый средний балл...')
    item2 = types.KeyboardButton('В меню')
    item3 = types.KeyboardButton('4.50')
    item4 = types.KeyboardButton('4.60')
    item5 = types.KeyboardButton('4.65')
    item6 = types.KeyboardButton('4.67')
    item7 = types.KeyboardButton('3.50')
    item8 = types.KeyboardButton('3.60')
    item9 = types.KeyboardButton('3.65')
    item10 = types.KeyboardButton('3.67')
    markup.add(item3, item4, item5, item6, item7, item8, item9, item10, item2)
    return markup


# После расчёта
def finishboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('Узнать больше📈')
    item2 = types.KeyboardButton('Прогноз')
    item3 = types.KeyboardButton('В меню')
    markup.add(item1, item2, item3)
    return markup


# 'В меню' + 'Назад↩'
def againboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('Назад↩')
    item2 = types.KeyboardButton('В меню')
    markup.add(item1, item2)
    return markup


def adminreply():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    query = types.KeyboardButton('/admin3027')
    markup.add(query)
    return markup
