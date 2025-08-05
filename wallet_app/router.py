"""This module provides API request handlers"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
)

from wallet_app.deps import get_db, get_transaction_session
from wallet_app.models import Wallet
from wallet_app.schemas import (
    SWalletOperation,
    SWalletCreated,
    SWalletCreate,
    OperationType,
)

router = APIRouter(prefix="/api/v1", tags=["wallets"])


@router.post(
    "/wallets/add", response_model=SWalletCreated, status_code=HTTP_201_CREATED
)
async def create_wallet(
        data: SWalletCreate = Body(default={}),
        db: AsyncSession = Depends(get_db)
) -> SWalletCreated:
    """
    Creates a new wallet.

    Input data must be in valid format 'SWalletCreate'.
    Allows empty input data.
    If it worked without errors, it returns the status code 'HTTP_201_CREATED'.
    :param data: data to create a new wallet.
    :param db: asynchronous database session generator.
    :return: created wallet object in format 'SWalletCreated'.
    """
    wallet = Wallet(**data.model_dump())
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return SWalletCreated.model_validate(wallet)


@router.post(
    "/wallets/{wallet_uuid}/operation",
    response_model=SWalletCreated,
    status_code=HTTP_200_OK,
)
async def wallet_operating(
        wallet_uuid: UUID,
        operation: SWalletOperation,
        session: AsyncSession = Depends(get_transaction_session),
):
    """
    Performs a wallet operation.

    Input data must be in valid format 'SWalletOperation'.
    If it worked without errors, it returns the status code 'HTTP_200_OK',
    otherwise it returns the status code 'HTTP_400_BAD_REQUEST'
    or 'HTTP_404_NOT_FOUND' based on the error.
    :param wallet_uuid: UUID of existing wallet.
    :param operation: operation to perform.
    Contains 'operation_type' and 'amount'.
    :param session: asynchronous database session generator for transactions.
    :return: updated wallet object in format 'SWalletCreated'.
    """
    if operation.amount <= 0:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Transfer amount must be positive"
        )
    async with session.begin():
        result = await session.execute(
            select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
        )
        wallet = result.scalar_one_or_none()
        if wallet is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        if operation.operation_type == OperationType.DEPOSIT:
            wallet.balance += operation.amount
        else:
            if wallet.balance < operation.amount:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Insufficient funds"
                )
            wallet.balance -= operation.amount
    await session.commit()
    return SWalletCreated.model_validate(wallet)


@router.get("/wallets/{wallet_uuid}", status_code=HTTP_200_OK)
async def get_wallet(
        wallet_uuid: UUID, db: AsyncSession = Depends(get_db)
) -> SWalletCreated:
    """
    Returns an existing wallet by UUID.

    Input UUID must exist and be UUID as well.
    If it worked without errors, it returns the status code 'HTTP_200_OK',
    otherwise, it returns the status code 'HTTP_404_NOT_FOUND'.
    :param wallet_uuid: UUID of existing wallet.
    :param db: asynchronous database session generator.
    :return: wallet object in format 'SWalletCreated'.
    """
    result = await db.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="Wallet not found")
    return SWalletCreated.model_validate(wallet)


@router.delete("/wallets/{wallet_uuid}", status_code=HTTP_204_NO_CONTENT)
async def delete_wallet(
        wallet_uuid: UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """
    Deletes an existing wallet by UUID.

    Input UUID must exist and be UUID as well.
    If it worked without errors,
    it returns the status code 'HTTP_204_NO_CONTENT'.
    :param wallet_uuid: UUID of existing wallet.
    :param db: asynchronous database session generator.
    :return: None
    """
    result = await db.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="Wallet not found")
    await db.delete(wallet)
    await db.commit()
