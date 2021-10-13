#!/usr/bin/env python
import datetime
import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scrapper import Olivka

TOKEN = os.getenv('OLIVKA_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
ol = Olivka()
scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)


@dp.message_handler(commands={'get_menu'})
async def get_menu(message: Message) -> None:
    await message.answer(f'<pre>{ol.get_today_menu(20)}</pre>', parse_mode='HTML')


async def on_startup(dp: Dispatcher) -> None:
    scheduler.add_job(ol.update, 'interval', hours=1, next_run_time=datetime.datetime.now())


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
