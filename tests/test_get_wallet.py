"""This module provides tests for obtaining a wallet"""

import uuid

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_wallet(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Obtains an existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response_add = await async_client.post(f"{base_wallets_url}/add", json={})
    request_uuid = uuid.UUID(response_add.json()["uuid"])
    response = await async_client.get(f"{base_wallets_url}/{request_uuid}")

    data = response.json()
    assert data == response_add.json()


@pytest.mark.asyncio
async def test_get_not_exist_wallet(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Trying to get a wallet that does not exist.
    :param async_client: asynchronous client.
    :return: None.
    """
    request_uuid = uuid.uuid4()
    response = await async_client.get(f"{base_wallets_url}/{request_uuid}")

    assert response.is_error
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_uuid",
    [
        {"uuid": "abcde"},
        {"uuid": "123"},
        {"uuid": 3335553},
    ]
)
async def test_get_invalid_wallet(
        async_client: AsyncClient,
        request_uuid: dict,
        base_wallets_url: str
) -> None:
    """
    Trying to get a wallet with an invalid UUID.
    :param async_client: asynchronous client.
    :param request_uuid: invalid UUID.
    :return: None.
    """
    response = await async_client.get(
        f"{base_wallets_url}/{request_uuid['uuid']}"
    )

    assert response.is_error
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
