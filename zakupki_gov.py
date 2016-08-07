#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from grab import Grab

__author__ = "wiom"
__version__ = "0.0.0"
__date__ = "07.08.16 3:40"
__description__ = """"""


class ZakupkiGov(Grab):
    def __init__(self):
        logger = logging.getLogger('grab')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

        super().__init__(timeout=60, connect_timeout=15, debug=True)
        self.setup(log_dir='/'.join((os.getcwd(), 'zakupki_logs')))

    def site_request(self, url: str):
        try:
            response = self.go(url=url)
        except Exception as e:
            response = e
        finally:
            return response

    def site_search(self, name: str, page: int = 1, perpage: str = '_10'):
        url = 'http://zakupki.gov.ru/epz/order/quicksearch/search_eis.html?' \
              'morphology=on&sortDirection=false&showLotsInfoHidden=false&' \
              'fz44=on&fz223=on&fz94=on&regions=&priceFrom=0&priceTo=200000000000&' \
              'currencyId=1&publishDateFrom=&publishDateTo=&updateDateFrom=&updateDateTo=&' \
              'sortBy=UPDATE_DATE&pageNumber={}&recordsPerPage={}&searchString={}'.format(page, perpage, name)

        return self.site_request(url=url)


zakupli = ZakupkiGov()
query_string = {
    'searchString': 'Лукоил'
}
zakupli.site_search(**query_string)


