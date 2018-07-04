from selenium import webdriver
from lxml import html
from time import time, sleep
from socket import create_connection, timeout
from typing import List
from threading import Thread
from pyperclip import copy
from sys import argv


def check_proxy(addr: str, port: str, type_: str, spisok: List[tuple]):
    start = time()
    try:
        create_connection((addr, int(port)), timeout=0.5)
        end = round(time() - start, 4)
        print(f'{addr}:{port} ({type_}) – {end} ms')
        spisok.append((addr, port, type_, end))
    except timeout:
        print(f'{addr}:{port} ({type_}) – timeout')


def get_addresses(url: str)-> List[tuple]:
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)
    source = html.fromstring(driver.page_source)
    driver.close()
    address = source.xpath('/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td[1]/font[2]/text()[1]')
    ports = source.xpath('/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td[1]/font[2]/text()[2]')
    types = source.xpath('/html/body/table[2]/tbody/tr[4]/td/table/tbody/tr/td[2]/font[1]/text()[1]')
    return [(address[i], ports[i], types[i + 2].strip()) for i in range(len(ports))]


def main(number: int):
    proxies = get_addresses('http://spys.one/proxys/DE')
    spisok: List[tuple] = []
    threads = [Thread(target=check_proxy, args=(proxy[0], proxy[1], proxy[2], spisok)) for proxy in proxies]
    for thread in threads:
        thread.start()
    while not spisok:
        sleep(0.1)
    if number and number <= len(spisok):
        copy(f'{spisok[number - 1][0]}:{spisok[number - 1][1]} ({spisok[number - 1][2]})')


if __name__ == '__main__':
    main(int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 0)

