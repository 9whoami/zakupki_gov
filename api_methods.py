# -*- coding: utf-8 -*-

import os
import simplejson
import logging
from grab import Grab

from config import Conf

__author__ = 'whoami'
__version__ = '1.3.3'
__date__ = '19.02.16 23:14'
__description__ = """
Набор методов для работы с апи
"""


class ApiMethods(Grab):
    BODY = 0
    JSON = 1

    online_only = None
    acc_status = None

    def __init__(self, loggining=False):
        if loggining:
            logger = logging.getLogger('grab')
            logger.addHandler(logging.StreamHandler())
            logger.setLevel(logging.DEBUG)

        config = Conf(section='api')
        self.base_url = config.main_url

        super().__init__(timeout=60, connect_timeout=15, debug=True)
        self.setup(log_dir='/'.join((os.getcwd(), 'grab_logs')),
                   headers={"Content-type": "application/json", "Accept": "application/json"})

    def api_request(self, uri: str = '', **kwargs: dict) -> dict:
        try:
            uri = ''.join((self.base_url, uri,))
            post_data = simplejson.dumps(kwargs)
            self.request(url=uri, post=post_data if kwargs else None)
            response = self.response.json
        except Exception as e:
            response = dict(Message=e)

        return response
