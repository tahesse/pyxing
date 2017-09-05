"""
Created on 04.12.2012
Modified on 05.09.2017

@author: codejitsu, github.com/codejitsu/pyxing
@author: tahesse, github.com/tahesse/pyxing
"""

from xing.globals import api_call_names
import logging
from oauthlib import oauth2 as oauth
import json

logger = logging.getLogger(__name__)


class XingException(Exception):
    """
    100 - call stack is empty
    101 - call to not existing api
    """

    def __init__(self, msg: str, code: int):
        self.msg = msg
        self.code = code

    def __str__(self):
        return 'Xing Exception: {msg} Exception Code: {code}'.format(**self.__dict__)


class XingHttpException(Exception):
    """ All http errors. """
    pass


class Xing(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret, version='1', verbose=False,
                 debug=False):
        self.api_version = version
        self.site = 'https://api.xing.com'
        self.format = 'json'

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.verbose = verbose
        self.debug = debug
        self.http_status = None
        self.stack = []

    def __getattr__(self, name):
        """ Put the name on the top of call stack. """

        if name.lower() not in api_call_names:
            self.__log__('Calling not existing api {}'.format(name.lower()))
            raise XingException('Call to not existing api {}'.format(name), 101)

        if self.verbose:
            self.__log__('Put {} on the top of the call stack.'.format(name))

        self.stack.append(name)
        return self

    def __call__(self, *args):
        """ Put arguments on the stack. """
        map(self.stack.append, args)
        return self

    def __request__(self, method, param=None):
        from os import sep
        try:
            if self.stack:
                self.__log__('Calling: {}'.format(sep.join(self.stack)))
                url = self.__make_request_url__()

                if param:
                    url += '?{}'.format(param)

                token = oauth.Token(key=self.access_token, secret=self.access_secret)
                consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)

                client = oauth.Client(consumer, token)

                response = client.request(url, method=method)

                if response:
                    self.http_status = response[0]['status']

                    if method == 'GET':
                        if self.http_status == '200':
                            ''' GET: The call was completed successfully. '''
                            return json.loads(response[1])
                    elif method == 'POST':
                        if self.http_status == '201':
                            ''' POST: The call was completed successfully. '''
                            return json.loads(response[1])

                return None
            else:
                raise XingException('Call stack is empty.', 100)
        finally:
            self.stack = []
            return None

    def get(self, **kwargs):
        params = []
        for name, value in kwargs.items():
            params.append('{0}={1}'.format(name, value))

        param = '&'.join(params) if params else None

        return self.__request__('GET', param)

    def post(self):
        return self.__request__('POST')

    def put(self):
        return self.__request__('PUT')

    def delete(self):
        return self.__request__('DELETE')

    def __make_request_url__(self):
        from os import sep
        first_part = '{site}/v{api_version}/'.format(**self.__dict__)
        return first_part + sep.join(self.stack) + '.' + self.format

    def __log__(self, text):
        """ log the text message to logger or console """

        if self.verbose:
            logger.debug(text)

            if self.debug:
                print(text)
