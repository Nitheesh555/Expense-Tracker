from datetime import date as date_type
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class ExpenseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    date: date_type | None = None

    @field_validator("name", "category")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        normalized = _normalize_text(value)
        if not normalized:
            raise ValueError("Value cannot be empty")
        return normalized

    @field_validator("category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        return value.lower()


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    amount: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    date: date_type | None = None

    @field_validator("name", "category")
    @classmethod
    def normalize_optional_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = _normalize_text(value)
        if not normalized:
            raise ValueError("Value cannot be empty")
        return normalized

    @field_validator("category")
    @classmethod
    def normalize_optional_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.lower()

    @model_validator(mode="after")
    def validate_any_field_present(self) -> "ExpenseUpdate":
        if all(
            field is None for field in (self.name, self.amount, self.category, self.date)
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expense_id: int = Field(validation_alias="id")
    name: str
    amount: float
    category: str
    date: date_type


class TotalsOut(BaseModel):
    total_expense: float
    total_salary: float
    remaining_amount: float
