import datetime
import logging
import textwrap
import time
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_OLIVKA_URL = 'https://m.olivkafood.ru/produkciya/bizneslanch/'


@dataclass(frozen=True)
class MenuItem:
    name: str
    portion: str | None
    info: str | None


class Olivka:
    def __init__(self) -> None:
        self.week: list[list[MenuItem]] | None = None
        self.last_update: float | None = None

    async def update(self) -> None:
        logger.debug('updating schedule')
        async with aiohttp.ClientSession() as client:
            async with client.get(_OLIVKA_URL) as r:
                self.week = self._parse_html(await r.text())
                self.last_update = time.time()

    @staticmethod
    def _parse_html(html: str) -> list[list[MenuItem]]:
        soup = BeautifulSoup(html, 'html.parser')
        week = []
        for day in soup.findAll('div', class_='extended-item complex-item')[1::2]:
            items = []
            for item in day.findAll('div', class_='extended-item'):
                name = item.find('div', class_='item-name').string
                if portion := item.find('div', class_='item-portion'):
                    portion = portion.string
                info = item.find('div', class_='item-info').string
                items.append(MenuItem(name, portion, info))
            week.append(items)
        return week

    def get_today_menu(self, width) -> str:
        try:
            today_menu = self.week[datetime.datetime.now().weekday()]
        except IndexError:
            today_menu = []
        return self.render_menu(today_menu, width)

    @staticmethod
    def render_menu(menu: list[MenuItem], width) -> str:
        if not menu:
            return 'Увы на сегодня ничего :('
        rendered = [f'+{" МЕНЮ ":=^{width - 2}}+']
        for item in menu:
            txt = item.name
            if item.portion:
                txt += f' [{item.portion}]'
            for line in textwrap.wrap(txt, width - 4):
                rendered.append(f'| {line:<{width - 4}} |')
            rendered.append(f'+{"-" * (width - 2)}+')

        return '\n'.join(rendered)
