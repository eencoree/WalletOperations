"""This module provides tests for adding a new wallet"""

from uuid import UUID

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_json",
    [
        {"balance": 10},
        {"balance": 3000},
        {"balance": 0},
        {},
        {"balance": 1},
    ]
)
async def test_add_wallet(
        async_client: AsyncClient,
        request_json: dict,
        base_wallets_url: str
) -> None:
    """
    Adding a new wallet with correct parameters.
    :param async_client: asynchronous client.
    :param request_json: parameters for wallet creation.
    :return: None.
    """
    response = await async_client.post(
        url=base_wallets_url+"/add",
        json=request_json
    )

    assert response.status_code == HTTP_201_CREATED
    data = response.json()

    assert data['balance'] >= 0
    assert isinstance(UUID(data['uuid']), UUID)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_json",
    [
        {"balance": -10},
        {"uuid": "abcdefghigk"},
        {"balance": "one hundred"},
    ]
)
async def test_add_invalid_wallet(
        async_client: AsyncClient,
        request_json: dict,
        base_wallets_url: str
) -> None:
    """
    Adding a new wallet with invalid parameters.
    :param async_client: asynchronous client.
    :param request_json: invalid parameters for wallet creation.
    :return: None.
    """
    response = await async_client.post(
        url=base_wallets_url+"/add",
        json=request_json
    )

    assert response.is_error
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
