from datetime import date as date_type
from sqlalchemy import Column, Date, Float, Integer, String, text

try:
    from .database import Base
except ImportError:
    from database import Base


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, default=date_type.today, server_default=text("(date('now'))"))
