"""This module provides tests for deleting a wallet"""

import uuid

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY
)


@pytest.mark.asyncio
async def test_delete_wallet(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Deleting an existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response_add = await async_client.post(f"{base_wallets_url}/add", json={})
    request_uuid = uuid.UUID(response_add.json()["uuid"])
    response = await async_client.delete(f"{base_wallets_url}/{request_uuid}")

    assert response.is_success
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_not_exist_wallet(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Trying to delete a non-existent wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    request_uuid = uuid.uuid4()
    response = await async_client.delete(f"{base_wallets_url}/{request_uuid}")

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
async def test_delete_invalid_wallet(
        async_client: AsyncClient,
        request_uuid: dict,
        base_wallets_url: str
) -> None:
    """
    Trying to delete a wallet with invalid UUID format.
    :param async_client: asynchronous client.
    :param request_uuid: invalid wallet uuid.
    :return: None.
    """
    response = await async_client.delete(
        f"{base_wallets_url}/{request_uuid['uuid']}"
    )

    assert response.is_error
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
