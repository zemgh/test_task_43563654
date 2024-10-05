from pydantic import BaseModel, Field, conint, constr, ConfigDict, Extra


class WalletSchema(BaseModel):
    uuid: constr(min_length=36, max_length=36) = Field(description='Wallet UUID')
    balance: int = Field(description='Balance')

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class WalletOperationSchema(BaseModel):
    operationType: str = Field(..., description='Type of operation', example='DEPOSIT, WITHDRAW')
    amount: int = Field(..., description='The amount to change the balance')

    model_config = ConfigDict(
        extra='forbid'
    )