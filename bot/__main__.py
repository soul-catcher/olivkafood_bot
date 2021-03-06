import logging

from aiogram import executor

from .bot import dp, scheduler

logging.basicConfig(level='INFO')
logging.getLogger(__package__).setLevel('DEBUG')

scheduler.start()
executor.start_polling(dp, skip_updates=True)
