"""This module provides tests for transactions"""

import asyncio

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_200_OK
)

from wallet_app.schemas import OperationType


@pytest.mark.asyncio
async def test_wallet_deposit(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Perform deposit operation for existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add", json={'balance': 100}
    )
    wallet = response.json()

    request_deposit = {
        "operation_type": OperationType.DEPOSIT,
        "amount": 100,
    }
    response_deposit = await async_client.post(
        f"{base_wallets_url}/{wallet['uuid']}/operation",
        json=request_deposit
    )

    assert response_deposit.status_code == HTTP_200_OK
    data = response_deposit.json()
    assert data['uuid'] == wallet['uuid']
    assert data['balance'] == wallet['balance'] + 100


@pytest.mark.asyncio
async def test_wallet_concurrent_deposit(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Perform concurrent deposit operation for existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 100}
    )
    wallet = response.json()
    amount_1 = 20
    amount_2 = 500

    async def deposit_1():
        """First deposit."""
        return await async_client.post(
            f"/api/v1/wallets/{wallet['uuid']}/operation",
            json={
                'operation_type': OperationType.DEPOSIT,
                'amount': amount_1
            }
        )

    async def deposit_2():
        """Second deposit."""
        return await async_client.post(
            f"/api/v1/wallets/{wallet['uuid']}/operation",
            json={
                'operation_type': OperationType.DEPOSIT,
                'amount': amount_2
            }
        )

    responses = await asyncio.gather(deposit_1(), deposit_2())

    for response in responses:
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['uuid'] == wallet['uuid']

    response_wallet = await async_client.get(
        f"{base_wallets_url}/{wallet['uuid']}"
    )
    assert response_wallet.status_code == HTTP_200_OK
    assert response_wallet.json()['balance'] == (
            wallet['balance'] + amount_1 + amount_2
    )


@pytest.mark.asyncio
async def test_wallet_withdraw(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Perform withdraw operation for existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 200}
    )
    wallet = response.json()

    request_withdraw = {
        "operation_type": OperationType.WITHDRAW,
        "amount": 100,
    }
    response_withdraw = await async_client.post(
        f"{base_wallets_url}/{wallet['uuid']}/operation",
        json=request_withdraw
    )

    assert response_withdraw.status_code == HTTP_200_OK
    data = response_withdraw.json()
    assert data['uuid'] == wallet['uuid']
    assert data['balance'] == wallet['balance'] - 100


@pytest.mark.asyncio
async def test_wallet_concurrent_withdraw(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Perform concurrent withdraw operation for existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 200}
    )
    wallet = response.json()
    amount_1 = 100
    amount_2 = 50

    async def withdraw_1():
        """First withdraw."""
        return await async_client.post(
            f"{base_wallets_url}/{wallet['uuid']}/operation",
            json={
                'operation_type': OperationType.WITHDRAW,
                'amount': amount_1
            }
        )

    async def withdraw_2():
        """Second withdraw."""
        return await async_client.post(
            f"{base_wallets_url}/{wallet['uuid']}/operation",
            json={
                'operation_type': OperationType.WITHDRAW,
                'amount': amount_2
            }
        )

    responses = await asyncio.gather(withdraw_1(), withdraw_2())
    for response in responses:
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data['uuid'] == wallet['uuid']

    response_wallet = await async_client.get(
        f"{base_wallets_url}/{wallet['uuid']}"
    )
    assert response_wallet.status_code == HTTP_200_OK
    assert response_wallet.json()['balance'] == (
            wallet['balance'] - amount_1 - amount_2
    )


@pytest.mark.asyncio
async def test_wallet_concurrent_deposit_withdraw(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Perform concurrent deposit and withdraw operations for existing wallet.
    :param async_client: asynchronous client.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 151}
    )
    wallet = response.json()
    deposit_amount = 50
    withdraw_amount = 200

    async def deposit():
        """Deposit operation."""
        return await async_client.post(
            f"{base_wallets_url}/{wallet['uuid']}/operation",
            json={
                'operation_type': OperationType.DEPOSIT,
                'amount': deposit_amount
            }
        )

    async def withdraw():
        """Withdraw operation."""
        return await async_client.post(
            f"{base_wallets_url}/{wallet['uuid']}/operation",
            json={
                'operation_type': OperationType.WITHDRAW,
                'amount': withdraw_amount
            }
        )

    responses = await asyncio.gather(deposit(), withdraw(), withdraw())
    success_operations = sum(response.is_success for response in responses)
    response_codes = sorted([response.status_code for response in responses])
    response_wallet = await async_client.get(
        f"{base_wallets_url}/{wallet['uuid']}"
    )
    data = response_wallet.json()
    match success_operations:
        case 1:
            assert response_codes == [
                HTTP_200_OK,
                HTTP_400_BAD_REQUEST,
                HTTP_400_BAD_REQUEST
            ]
            assert data['balance'] == wallet['balance'] + deposit_amount

        case 2:
            assert response_codes == [
                HTTP_200_OK,
                HTTP_200_OK,
                HTTP_400_BAD_REQUEST
            ]
            assert data['balance'] == (
                    wallet['balance'] + deposit_amount - withdraw_amount
            )

        case _:
            assert response_codes == [HTTP_400_BAD_REQUEST] * 3
            assert data['balance'] == wallet['balance']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation_type, amount",
    [
        ('deposit', 100),
        ('plus', 50),
        ('add', 200),
    ]
)
async def test_invalid_operation_type(
        async_client: AsyncClient,
        operation_type: str,
        amount: float,
        base_wallets_url: str
) -> None:
    """
    Trying to perform an operation with invalid operation type.
    :param async_client: asynchronous client.
    :param operation_type: invalid operation type.
    :param amount: correct numeric amount.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 100}
    )
    wallet = response.json()

    request_deposit = {
        "operation_type": operation_type,
        "amount": amount,
    }
    response_deposit = await async_client.post(
        f"{base_wallets_url}/{wallet['uuid']}/operation",
        json=request_deposit
    )

    assert response_deposit.status_code == HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation_type, amount",
    [
        (OperationType.DEPOSIT, 0),
        (OperationType.DEPOSIT, -50),
        (OperationType.DEPOSIT, "null"),
        (OperationType.DEPOSIT, "abc"),
    ]
)
async def test_invalid_amount(
        async_client: AsyncClient,
        operation_type: OperationType.DEPOSIT,
        amount: object,
        base_wallets_url: str
) -> None:
    """
    Trying to perform an operation with invalid amount.
    :param async_client: asynchronous client.
    :param operation_type: correct operation type.
    :param amount: invalid amount.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 100}
    )
    wallet = response.json()

    request_deposit = {
        "operation_type": operation_type,
        "amount": amount,
    }
    response_deposit = await async_client.post(
        f"{base_wallets_url}/{wallet['uuid']}/operation",
        json=request_deposit
    )

    try:
        float(amount)
        assert response_deposit.status_code == HTTP_400_BAD_REQUEST
    except ValueError:
        assert response_deposit.status_code == HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_insufficient_funds(
        async_client: AsyncClient,
        base_wallets_url: str
) -> None:
    """
    Trying to perform a withdrawal operation with insufficient funds.
    :param async_client: asynchronous client.
    :return: None.
    """
    response = await async_client.post(
        f"{base_wallets_url}/add",
        json={'balance': 100}
    )
    wallet = response.json()

    request_withdraw = {
        "operation_type": OperationType.WITHDRAW,
        "amount": 101,
    }
    response_deposit = await async_client.post(
        f"{base_wallets_url}/{wallet['uuid']}/operation",
        json=request_withdraw
    )
    assert response_deposit.status_code == HTTP_400_BAD_REQUEST
