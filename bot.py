#!/usr/bin/env python
import datetime
import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scrapper import Olivka

TOKEN = os.environ['OLIVKA_TOKEN']
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
ol = Olivka()
scheduler = AsyncIOScheduler()
scheduler.add_jobstore('sqlalchemy', url='sqlite:///db.sqlite')

logger = logging.getLogger(__name__)


async def send_menu(dp: Dispatcher, chat_id: int):
    await dp.bot.send_message(chat_id, f'<pre>{ol.get_today_menu(20)}</pre>', parse_mode='HTML')


@dp.message_handler(commands={'get_menu'})
async def get_menu(message: Message) -> None:
    await send_menu(dp, message.chat.id)


@dp.message_handler(commands={'set_notifications_time'})
async def set_notifications_time(message: Message) -> None:
    error_message = 'Задайте время в 24-м формате.\nПример использования:\n/set_notifications_time 11:00'
    if not message.get_args():
        await message.answer(error_message)
        return
    # TODO Добавлять таски в scheduler
    await message.answer(message.get_args())


# def set_notification_task(chat_id, time: str):
#     scheduler.add_job(send_menu, )

async def update_ol() -> None:
    await ol.update()


async def on_startup(dp: Dispatcher) -> None:
    scheduler.add_job(
        update_ol, 'interval', hours=1, next_run_time=datetime.datetime.now(), id='update_job', replace_existing=True
    )


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    logging.getLogger('scrapper').setLevel("DEBUG")

    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
