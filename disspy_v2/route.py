'''
~Route~ - is a class what is using for responding in discord API

All:
----

1. ~Route~
...
'''

from asyncio import gather
from typing import TYPE_CHECKING, Iterable, Literal, Optional, NamedTuple

from aiohttp.client_exceptions import ContentTypeError
from requests import delete as DELETE
from requests import get as GET
from requests import head as HEAD
from requests import options as OPTIONS
from requests import patch as PATCH
from requests import post as POST
from requests import put as PUT
from requests.exceptions import JSONDecodeError

from disspy_v2 import utils

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from aiohttp import ClientSession
    from requests import Response

API_VERSION = 10
BASE = f'https://discord.com/api/v{API_VERSION}'

class _HTTPRequestResult(NamedTuple):
    data: dict | None
    status: int

class Route:
    def __init__(
        self,
        endpoint: Optional[str] = '',
        *params: Iterable[str],
        method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'] = 'GET',
        token: Optional[str] = '',
        payload: Optional[dict] = {}
    ) -> None:
        self.endpoint = endpoint % params
        self.url = BASE + self.endpoint
        self.method = method
        self.hdrs = utils.auth(token)
        self.data = payload

    def request(self) -> _HTTPRequestResult:
        '''
        Route.request()
        ---------------

        Sends request with info in object
        '''
        funcs = {
            'GET': GET,
            'POST': POST,
            'PUT': PUT,
            'DELETE': DELETE,
            'PATCH': PATCH,
            'OPTIONS': OPTIONS,
            'HEAD': HEAD,
        }
        func = funcs[self.method]

        resp: 'Response' = func(
            url=self.url,
            json=self.data,
            headers=self.hdrs,
            timeout=2,
        )

        try:
            return resp.json(), resp.status_code
        except JSONDecodeError:
            return resp.text, resp.status_code

    async def _async_request_task(self, session: 'ClientSession') -> _HTTPRequestResult:
        funcs = {
            'GET': session.get,
            'POST': session.post,
            'PUT': session.put,
            'DELETE': session.delete,
            'PATCH': session.patch,
            'OPTIONS': session.options,
            'HEAD': session.head,
        }
        func = funcs[self.method]

        async with func(
            url=self.url,
            json=self.data,
            headers=self.hdrs,
            timeout=2,
        ) as resp:
            try:
                return await resp.json(), resp.status
            except ContentTypeError:
                try:
                    return await resp.text(), resp.status
                except ContentTypeError:
                    return None, resp.status


    async def async_request(self, session: 'ClientSession', loop: 'AbstractEventLoop'):
        '''
        Route.async_request()
        ---------------------

        Sends async request with info in object

        Arguments:
        ==========

        ~session~: The aiohttp client session
        ~loop~: The current asyncio event loop
        '''
        tasks = [loop.create_task(self._async_request_task(session))]
        await gather(*tasks)
