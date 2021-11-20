import datetime
import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from scrapper import Olivka

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
logging.basicConfig(level=logging.INFO)


async def send_menu(chat_id: int):
    await dp.bot.send_message(chat_id, f'<pre>{ol.get_today_menu(20)}</pre>', parse_mode='HTML')


@dp.message_handler(commands={'get_menu'})
async def get_menu(message: Message) -> None:
    logger.info(f'Получено сообщение {message.text}')
    await send_menu(message.chat.id)


@dp.message_handler(commands={'set_notifications_time'})
async def set_notifications_time(message: Message) -> None:
    logger.info(f'Получено сообщение {message.text}')
    error_message = ('Задайте время в cron формате.\nПример использования:\n/set_notifications_time 0 10 * * 1-5\n'
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
        await message.answer(f"Время успешно установлено. В следующий раз уведомление придёт\n{job.next_run_time}")
    except ValueError as e:
        msg = f"Неверно задан формат. Ошибка:\n{e}"
        logger.info(msg)
        await message.answer(msg)


async def send_message(chat_id: int, message: str) -> None:
    await dp.bot.send_message(chat_id, message)


@dp.message_handler(commands={'set_custom_notification'})
async def set_custom_notification(message: Message) -> None:
    logger.info(f'Получено сообщение {message.text}')
    error_message = ('Задайте время в cron формате и сообщение.\nПример использования:\n'
                     '/set_custom_notification 0 12 * * 1-5 Время обедать!')
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
            id="custom-message-" + str(message.chat.id),
            jobstore='sqlalchemy',
            replace_existing=True
        )
        await message.answer(f"Время успешно установлено. В следующий раз уведомление придёт\n{job.next_run_time}")
    except ValueError as e:
        msg = f"Неверно задан формат. Ошибка:\n{e}"
        logger.info(msg)
        await message.answer(msg)


async def on_startup(dp: Dispatcher) -> None:
    scheduler.add_job(ol.update, 'interval', hours=1, next_run_time=datetime.datetime.now())


if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    logging.getLogger('scrapper').setLevel("DEBUG")

    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)