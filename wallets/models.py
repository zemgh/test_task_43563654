from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres import Base


class Wallet(Base):
    __tablename__ = 'wallets'
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True)
    balance: Mapped[int] = mapped_column(default=0)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'balance': self.balance
        }

