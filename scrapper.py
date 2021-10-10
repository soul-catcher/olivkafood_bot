import asyncio
import pprint
import time
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

_OLIVKA_URL = 'https://m.olivkafood.ru/produkciya/bizneslanch/'


@dataclass(frozen=True)
class MenuItem:
    name: str
    portion: str | None
    info: str | None


class Olivka:
    def __init__(self):
        self.week: list[list[MenuItem]] | None = None
        self.last_update: float | None = None

    async def update(self) -> None:
        print("update")
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


async def main():
    olivka = Olivka()
    await olivka.update()
    pprint.pp(olivka.week)


if __name__ == '__main__':
    asyncio.run(main())
