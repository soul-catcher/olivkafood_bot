import datetime
import logging

import aiogram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message

from scrapper import Olivka

TOKEN = '2007485886:AAHA2G3ldlhd2pcmdJQtJapXLILRPw1zQqw'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
ol = Olivka()
scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)


@dp.message_handler(commands={'get_menu'})
async def get_menu(message: Message):
    await message.answer(str(ol.week))


async def on_startup(dp: aiogram.Dispatcher):
    scheduler.add_job(ol.update, 'interval', hours=1, next_run_time=datetime.datetime.now())


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
