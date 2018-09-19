from time import time, sleep
from threading import Thread
from pyperclip import copy
from sys import argv
import asyncio
from pyppeteer import launch
from typing import List
from requests import get
from requests.exceptions import Timeout, ProxyError, ConnectionError
from socket import timeout
from urllib3.exceptions import ReadTimeoutError


async def main(value: str):
    browser = await launch()
    proxy = await get_address(browser, value)
    await browser.close()
    return proxy


async def get_address(browser, url):
    page = await browser.newPage()
    await page.goto(url)
    urls = await page.xpath('/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td[1]/font[2]')
    ips = [(await page.evaluate('(element) => element.innerText', ip)) for ip in urls]
    types_ = await page.xpath('/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td[2]/font[1]')
    types = [(await page.evaluate('(element) => element.innerText', types_[i])) for i in range(2, len(types_))]
    return [(ips[i], types[i].split()[0].strip()) for i in range(len(ips))]


def check_proxy(addr: str, type_: str, spisok_: List[tuple]):
    start = time()
    proxy = {'http': f'http://{addr}'} if 'http' in type_.lower() else {'http': f'socks5://{addr}'}
    try:
        get('https://ya.ru', proxies=proxy, timeout=0.5)
        end = round(time() - start, 4)
        spisok_.append((addr, type_, end))
    except (timeout, Timeout, ProxyError, ReadTimeoutError, ConnectionError):
        pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    addresses = ('http://spys.one/proxys/IT', 'http://spys.one/proxys/DE', 'http://spys.one/proxys/FR')
    tasks = [loop.create_task(main(url)) for url in addresses]
    proxies_ = loop.run_until_complete(asyncio.gather(*tasks))
    proxies = [item for lst in proxies_ for item in lst]
    spisok: List[tuple] = []
    threads = [Thread(target=check_proxy, args=(proxy[0], proxy[1], spisok)) for proxy in proxies]
    for thread in threads:
        thread.start()
    sleep(0.5)
    spisok.sort(key=lambda x: x[2])
    print(*[f'{key[0]} ({key[1]}) – {key[2]} ms' for key in spisok], sep='\n')
    number = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 0
    if number and number <= len(spisok):
        copy(f'{spisok[number - 1][0]} ({spisok[number - 1][1]})')
