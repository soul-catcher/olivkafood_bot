import logging

from aiogram import executor

from .bot import dp, scheduler, on_startup

logging.basicConfig(level='INFO')
logging.getLogger('bot.bot').setLevel('DEBUG')
logging.getLogger('bot.scrapper').setLevel('DEBUG')

scheduler.start()
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
