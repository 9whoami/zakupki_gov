#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re

from grab import Grab

__author__ = "wiom"
__version__ = "0.0.0"
__date__ = "07.08.16 3:40"
__description__ = """"""


class ZakupkiGov(Grab):
    total_count = 0
    count = 0

    regexp = {
        'total_count': r'Всего записей\:\s*\<strong\>(\d+)\<\/strong\>',
        'details': r'\<li\>\s*?\<a\s*?[target\=\"\_blank\"]*?\s*?href\=\"(.*?)\"\s*?[target\=\"\_blank\"]*?\>\s*?Сведения\s*?\<\/a\>\s*\<\/li\>'
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
            result = set(re.findall(pattern=self.regexp['details'], string=self._html))
            if self.count >= self.total_count:
                raise StopIteration
            for r in result:
                self.count += 1
                yield r
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

# Переход по этим ссылкам
# Парсинг сведений о закупках

zakupli = ZakupkiGov()

zakupli.site_search(name='Лукоил')

for url_for_details in zakupli:
    print(url_for_details)
