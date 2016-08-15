#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
from bs4 import BeautifulSoup

import simplejson
from grab import Grab

__author__ = "wiom"
__version__ = "0.0.0"
__date__ = "07.08.16 3:40"
__description__ = """"""


class ZakupkiGov(Grab):
    total_count = 0
    count = 0

    xpath = {
        'items': './/*/body/div/div[1]/div[3]/div/div/table',
        'status': 'table/tbody/tr/td[@class="tenderTd"]/dl/dt/strong',
        'reg_nomber': 'table/tbody/tr/td[@class="descriptTenderTd"]/dl/dt/a',
        'organization': 'table/tbody/tr/td[@class="descriptTenderTd"]/dl/dd[@class="nameOrganization"]/a',
        'amount': 'table/tbody/tr/td[@class="amountTenderTd"]/ul/li',
    }

    regexp = {
        'total_count': r'Всего записей\:\s*\<strong\>(\d+)\<\/strong\>',
        'details': r'\<li\>\s*?\<a\s*?[target\=\"\_blank\"]*?\s*?href\=\"(.*?)\"\s*?[target\=\"\_blank\"]*?\>\s*?Сведения\s*?\<\/a\>\s*\<\/li\>',
    }

    _html = ''
    _last_query_string = {}

    def __init__(self):
        logger = logging.getLogger('grab')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

        super().__init__(timeout=60, connect_timeout=15, debug=True)
        self.setup(log_dir='/'.join((os.getcwd(), 'zakupki_logs')))

    def __iter__(self):
        self.count = 0
        result = re.search(pattern=self.regexp['total_count'], string=self._html)
        self.total_count = int(result.groups()[0]) if result else 0

        return self.__next__()

    def __next__(self):
        while True:
            # <div class="registerBox registerBoxBank margBtm20">
            soup = BeautifulSoup(self._html, 'html.parser')
            items = soup.find_all('div', {'class': ['registerBox', 'registerBoxBank', 'margBtm20']})

            if self.count >= self.total_count:
                raise StopIteration

            for item in items:
                self.count += 1
                _item = {}

                _item['status'] = item.findNext('td', {'class': ['tenderTd']}).dl.dt.strong.text.strip()
                _item['reg_nomber'] = item.findNext('td', {'class': ['descriptTenderTd']}).dl.dt.a.text.strip()
                _item['amount'] = [x.text for x in item.findNext('td', {'class': 'amountTenderTd'}).ul.findAll('li')]

                yield simplejson.dumps(_item, ensure_ascii=False)
            else:
                self._last_query_string['page'] += 1
                self._html = self.site_search(**self._last_query_string)

    def site_request(self, url: str):
        try:
            response = self.go(url=url).body.decode('utf-8')
        except Exception as e:
            response = e
        finally:
            return response

    def site_search(self, name: str, page: int = 1, perpage: str = '_10'):
        self._last_query_string = {
            'name': name,
            'page': page,
            'perpage': perpage
        }

        url = 'http://zakupki.gov.ru/epz/order/quicksearch/search_eis.html?' \
              'morphology=on&sortDirection=false&showLotsInfoHidden=false&' \
              'fz44=on&fz223=on&fz94=on&regions=&priceFrom=0&priceTo=200000000000&' \
              'currencyId=1&publishDateFrom=&publishDateTo=&updateDateFrom=&updateDateTo=&' \
              'sortBy=UPDATE_DATE&pageNumber={}&recordsPerPage={}&searchString={}'.format(page, perpage, name)

        self._html = self.site_request(url=url)
        return self._html

zakupli = ZakupkiGov()

zakupli.site_search(name='Лукоил')

for url_for_details in zakupli:
    print(url_for_details)
