#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   spider2.py
@Author  :   Racle
@Version :   1.0
@Desc    :   None
'''

### NOTE
# 因为百度页面代码不知道为什么会时不时变化，以下代码只成果执行了第一次。
# 调试了很久，解析静态页面，抽取信息失败。应该是百度的反爬虫措施。还有一堆<span>


import random
import asyncio
import aiohttp
from lxml import etree
from agents import user_agent


header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Host": "zhidao.baidu.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(user_agent)
}


def parse_search_pages(text):
    html = etree.HTML(text)
    target_div = html.xpath("//div[@class='list-inner']/div/dl/dt/a")
    titles, urls = [], []
    for item in target_div:
        titles.append(item.xpath("./text()")[0])
        urls.append(item.xpath("./@href")[0])
    return titles, urls


def parse_item_pages(text):
    html = etree.HTML(text)
    answer = html.xpath("//div[@class='full-content']")
    return answer.strip()


async def fetch_content(url):
    async with aiohttp.ClientSession(headers=header,
                                     connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url) as response:
            return await response.text()


async def search(query, top=3):
    init_url = "https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word=" + query
    init_page = await fetch_content(init_url)
    titles, urls = parse_search_pages(init_page.encode('utf-8', errors='ignore'))

    answer_tasks = [fetch_content(url) for url in urls]
    answer_pages = await asyncio.gather(*answer_tasks)

    for a_page in answer_pages:
        answer = parse_item_pages(a_page.encode('utf-8', errors='ignore'))
        print(answer)


if __name__ == '__main__':
    # await search("姚明的身高是多少")  # 在jupyter notebook中
    # asyncio.run(search("姚明的身高是多少"))  # python 3.7及以上
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search("姚明的身高是多少"))