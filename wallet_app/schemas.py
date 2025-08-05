"""
This module describes schemas for verifying request input
and response data
"""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OperationType(str, Enum):
    """Enumeration of allowed wallet operation types."""

    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class SWalletOperation(BaseModel):
    """
    Schema for wallet operations.

    Validates that the operation includes a correct type
    and an optional positive amount.
    """

    operation_type: OperationType
    amount: Optional[float]

    model_config = ConfigDict(extra="forbid")


class SWalletCreate(BaseModel):
    """Scheme for creating a new wallet.

    Contains an optional 'balance' parameter
    thar must be positive. If it is not specified, the default value is 0.
    """

    balance: Optional[float] = Field(default=0, ge=0)

    model_config = ConfigDict(extra="forbid")


class SWalletCreated(BaseModel):
    """
    Scheme for output data after creation or some wallet operation.

    Returns wallet UUID and current balance.
    """

    uuid: UUID
    balance: float

    model_config = ConfigDict(from_attributes=True)
