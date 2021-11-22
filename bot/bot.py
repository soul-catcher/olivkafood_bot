import datetime
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiohttp.client import ClientConnectionError

from .scrapper import Olivka

TOKEN = os.environ['OLIVKA_TOKEN']
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
ol = Olivka()
jobstores = {
    'sqlalchemy': SQLAlchemyJobStore('sqlite:///db.sqlite'),
    'default': MemoryJobStore(),
}
scheduler = AsyncIOScheduler(jobstores=jobstores)
logger = logging.getLogger(__name__)


async def send_menu(chat_id: int) -> None:
    await dp.bot.send_message(chat_id, f'<pre>{ol.get_today_menu("МЕНЮ", 20)}</pre>', parse_mode='HTML')


@dp.message_handler(commands={'get_menu'})
async def get_menu(message: Message) -> None:
    logger.info(
        f'Получено сообщение из {message.chat.type} {message.chat.title or message.chat.username}: {message.text}'
    )
    await send_menu(message.chat.id)


@dp.message_handler(commands={'set_notifications_time'})
async def set_notifications_time(message: Message) -> None:
    logger.info(
        f'Получено сообщение из {message.chat.type} {message.chat.title or message.chat.username}: {message.text}'
    )
    error_message = ('Задайте время в cron формате.\nПример использования:\n/set_notifications_time 0 10 * * mon-fri\n'
                     'В таком случае уведомление будет приходить с понедельника по пятницу в 10 часов.')
    if not (args := message.get_args()):
        await message.answer(error_message)
        return
    try:
        job = scheduler.add_job(
            send_menu,
            CronTrigger.from_crontab(args),
            (message.chat.id, ),
            id=str(message.chat.id),
            jobstore='sqlalchemy',
            replace_existing=True
        )
        await message.answer(f'Время успешно установлено. В следующий раз уведомление придёт\n{job.next_run_time}')
    except ValueError as e:
        msg = f'Неверно задан формат. Ошибка:\n{e}'
        logger.info(msg)
        await message.answer(msg)


async def send_message(chat_id: int, message: str) -> None:
    await dp.bot.send_message(chat_id, message)


@dp.message_handler(commands={'set_custom_notification'})
async def set_custom_notification(message: Message) -> None:
    logger.info(
        f'Получено сообщение из {message.chat.type} {message.chat.title or message.chat.username}: {message.text}'
    )
    error_message = ('Задайте время в cron формате и сообщение.\nПример использования:\n'
                     '/set_custom_notification 0 12 * * mon-fri Время обедать!')
    alist = message.get_args().split()
    if len(alist) < 6:
        await message.answer(error_message)
        return
    cron, custom_message = ' '.join(alist[:5]), ' '.join(alist[5:])
    try:
        job = scheduler.add_job(
            send_message,
            CronTrigger.from_crontab(cron),
            (message.chat.id, custom_message),
            id='custom-message-' + str(message.chat.id),
            jobstore='sqlalchemy',
            replace_existing=True
        )
        await message.answer(f'Время успешно установлено. В следующий раз уведомление придёт\n{job.next_run_time}')
    except ValueError as e:
        msg = f'Неверно задан формат. Ошибка:\n{e}'
        logger.info(msg)
        await message.answer(msg)


@scheduler.scheduled_job('interval', hours=1, next_run_time=datetime.datetime.now())
async def updater():
    try:
        await ol.update()
    except ClientConnectionError as e:
        logger.warning(f'Menu not updated! Error "{e}"')
