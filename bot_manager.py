from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State


admin = 1141475192
TOKEN = '5070610299:AAG1nnmISS99_czMOADldrP_nArYDArMXN4'
bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())


class StQuiz(StatesGroup):
    waiting_purpose_score = State()
    waiting_way_calc = State()
    waiting_list_calc = State()
    waiting_present_score = State()
    waiting_amount_calc = State()
    waiting_comment = State()
    look_table = State()
    del_note = State()
