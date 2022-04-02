from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State


admin = 1141475192
TOKEN = '5070610299:AAG1nnmISS99_czMOADldrP_nArYDArMXN4'
URI = 'postgres://sbfqqjimvvqzyc:05185c25d6ef587b7cb9f85541a9902030e39dabe606c765a6f77ea9da80c544@ec2-54-74-14-109.' \
      'eu-west-1.compute.amazonaws.com:5432/d4eaaaje408rv8'
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
