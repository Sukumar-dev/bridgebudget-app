from pydantic import BaseModel, Field, field_validator


class DebtItem(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    balance: float = Field(ge=0, le=1_000_000)
    apr: float = Field(ge=0, le=100)
    minimum_payment: float = Field(ge=0, le=100_000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()


class BudgetRequest(BaseModel):
    location_zip: str = Field(min_length=5, max_length=5)
    household_size: int = Field(ge=1, le=10)
    monthly_income: float = Field(gt=0, le=1_000_000)
    savings: float = Field(ge=0, le=1_000_000)
    housing: float = Field(ge=0, le=1_000_000)
    utilities: float = Field(ge=0, le=1_000_000)
    food: float = Field(ge=0, le=1_000_000)
    transport: float = Field(ge=0, le=1_000_000)
    healthcare: float = Field(ge=0, le=1_000_000)
    childcare: float = Field(ge=0, le=1_000_000)
    insurance: float = Field(ge=0, le=1_000_000)
    other_essentials: float = Field(ge=0, le=1_000_000)
    debts: list[DebtItem] = Field(default_factory=list, max_length=20)

    @field_validator("location_zip")
    @classmethod
    def validate_zip(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("ZIP code must contain 5 digits.")
        return value


class SavedPlanResponse(BaseModel):
    plan_id: str
    share_url: str
    analysis: dict


class LoadedPlanResponse(BaseModel):
    plan_id: str
    input: BudgetRequest
    analysis: dict
