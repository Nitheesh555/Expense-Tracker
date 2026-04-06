from datetime import date as date_type
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

try:
    from .database import SessionLocal, get_total_salary, init_db
    from .models import ExpenseModel
    from .schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate, TotalsOut
except ImportError:
    from database import SessionLocal, get_total_salary, init_db
    from models import ExpenseModel
    from schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate, TotalsOut

app = FastAPI(title="Simple Expense Tracker")


init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/expenses/", response_model=ExpenseOut)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    expense_date = expense.date or date_type.today()
    new_expense = ExpenseModel(
        name=expense.name,
        amount=expense.amount,
        category=expense.category,
        date=expense_date,
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@app.get("/expenses/", response_model=list[ExpenseOut])
def get_expenses(
    year: Annotated[int | None, Query(ge=1)] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    week: Annotated[int | None, Query(ge=1, le=53)] = None,
    day: Annotated[int | None, Query(ge=1, le=31)] = None,
    category: Annotated[str | None, Query(min_length=1)] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ExpenseModel)

    if year is not None:
        query = query.filter(func.strftime("%Y", ExpenseModel.date) == f"{year:04d}")
    if month is not None:
        query = query.filter(func.strftime("%m", ExpenseModel.date) == f"{month:02d}")
    if week is not None:
        query = query.filter(func.strftime("%W", ExpenseModel.date) == f"{week:02d}")
    if day is not None:
        query = query.filter(func.strftime("%d", ExpenseModel.date) == f"{day:02d}")
    if category is not None:
        normalized_category = " ".join(category.strip().split()).lower()
        if not normalized_category:
            raise HTTPException(status_code=400, detail="Category filter cannot be empty")
        query = query.filter(func.lower(ExpenseModel.category) == normalized_category)

    return query.order_by(ExpenseModel.date.desc(), ExpenseModel.id.desc()).all()


@app.get("/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.put("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, updated_expense: ExpenseUpdate, db: Session = Depends(get_db)):
    db_expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = updated_expense.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(db_expense)
    db.commit()
    return {"message": "Expense deleted successfully"}


@app.get("/expenses/month/{year}/{month}/", response_model=list[ExpenseOut])
def get_expenses_by_month(year: int, month: int, db: Session = Depends(get_db)):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 1:
        raise HTTPException(status_code=400, detail="Year must be greater than 0")

    expenses = (
        db.query(ExpenseModel)
        .filter(func.strftime("%Y", ExpenseModel.date) == f"{year:04d}")
        .filter(func.strftime("%m", ExpenseModel.date) == f"{month:02d}")
        .order_by(ExpenseModel.date.desc(), ExpenseModel.id.desc())
        .all()
    )
    return expenses


@app.get("/totals/", response_model=TotalsOut)
def get_totals(db: Session = Depends(get_db)):
    total_expense = db.query(func.coalesce(func.sum(ExpenseModel.amount), 0.0)).scalar() or 0.0
    total_salary = get_total_salary()
    remaining_amount = total_salary - float(total_expense)

    return TotalsOut(
        total_expense=float(total_expense),
        total_salary=float(total_salary),
        remaining_amount=float(remaining_amount),
    )
