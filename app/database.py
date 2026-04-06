import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "expenses.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
TOTAL_SALARY_DEFAULT = 0.0

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_total_salary() -> float:
    raw_value = os.getenv("TOTAL_SALARY")
    if raw_value is None:
        return TOTAL_SALARY_DEFAULT
    try:
        return float(raw_value)
    except ValueError:
        return TOTAL_SALARY_DEFAULT


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_expense_date_column()


def _ensure_expense_date_column() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "expenses" not in table_names:
        return

    column_names = {column["name"] for column in inspector.get_columns("expenses")}
    if "date" in column_names:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE expenses ADD COLUMN date DATE"))
        connection.execute(text("UPDATE expenses SET date = date('now') WHERE date IS NULL"))
