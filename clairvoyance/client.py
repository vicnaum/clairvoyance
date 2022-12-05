import asyncio
from typing import Dict, Optional
import time

import aiohttp

from clairvoyance.entities.context import client_ctx, log
from clairvoyance.entities.interfaces import IClient


class Client(IClient):

    def __init__(
        self,
        url: str,
        max_retries: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        concurrent_requests: Optional[int] = None,
    ) -> None:
        self._url = url
        self._session = None

        self._headers = headers or {}
        self._max_retries = max_retries or 30
        self._semaphore = asyncio.Semaphore(concurrent_requests or 50)

        client_ctx.set(self)

    async def post(
        self,
        document: Optional[str],
        retries: int = 0,
    ) -> Dict:
        """Post a GraphQL document to the server and return the response as JSON."""
        log().debug(f'Posting {document}, retries {retries} of {self._max_retries}')

        time.sleep(0.5)
        time.sleep(10 * retries)
        if (retries > 10): time.sleep(60*retries)

        if retries >= self._max_retries:
            log().warning(f'Reached max retries: {retries}')
            return {}

        async with self._semaphore:
            if not self._session:
                self._session = aiohttp.ClientSession(headers=self._headers)

            # Translate an existing document into a GraphQL request.
            gql_document = {'query': document} if document else None

            try:
                response = await self._session.post(
                    self._url,
                    json=gql_document,
                )

                if response.status >= 500:
                    log().warning(f'Received status code {response.status}')
                    return await self.post(document, retries + 1)

                response_json = await response.json(content_type=None)
                return response_json

            # except (
            #     aiohttp.client_exceptions.ClientConnectionError,
            #     aiohttp.client_exceptions.ClientPayloadError,
            # ) as e:
            except Exception as e:
                log().warning(f'Error posting to {self._url}: {e} - Retry {retries} of {self._max_retries}')

        time.sleep(1 + (10 * retries))
        if (retries > 10): time.sleep(60*retries)
        
        return await self.post(document, retries + 1)

    async def close(self) -> None:
        if self._session:
            await self._session.close()
