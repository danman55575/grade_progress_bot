import logging
from aiogram import executor
from bot_manager import dp
from handlers import maincourse, menu, admin, review


logging.basicConfig(level=logging.INFO)


menu.register_handlers_menu(dp)
maincourse.register_handlers_maincourse(dp)
comment.register_handlers_review(dp)
admin.register_handlers_admin(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
