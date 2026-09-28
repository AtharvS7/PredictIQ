"""User-supplied planning assumptions, deliberately separate from ML estimates."""
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Hours = Annotated[Decimal, Field(ge=0, le=100000, max_digits=8, decimal_places=2)]
Rate = Annotated[Decimal, Field(ge=0, le=10000, max_digits=7, decimal_places=2)]


class BudgetTask(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name
    low_hours: Hours
    likely_hours: Hours
    high_hours: Hours
    hourly_rate_usd: Rate

    @model_validator(mode="after")
    def ordered_hours(self):
        if not self.low_hours <= self.likely_hours <= self.high_hours:
            raise ValueError("Hours must satisfy low <= likely <= high")
        return self


class BudgetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_name: Name
    tasks: list[BudgetTask] = Field(min_length=1, max_length=100)
    contingency_pct: Annotated[Decimal, Field(ge=0, le=100, max_digits=5, decimal_places=2)] = Decimal(0)


class BudgetTotals(BaseModel):
    low_hours: Decimal
    likely_hours: Decimal
    high_hours: Decimal
    low_cost_usd: Decimal
    likely_cost_usd: Decimal
    high_cost_usd: Decimal


class SavedBudget(BaseModel):
    id: UUID
    created_at: datetime
    method: Literal["manual_task_budget_v1"] = "manual_task_budget_v1"
    inputs: BudgetRequest
    totals: BudgetTotals


def calculate_budget(request: BudgetRequest) -> BudgetTotals:
    """Sum hours × rates, apply contingency to cost, round totals once to cents.

    Ranges are scenarios supplied by the user, not statistical intervals.
    Hours describe effort; they do not imply elapsed calendar duration.
    """
    result = {}
    multiplier = Decimal(1) + request.contingency_pct / Decimal(100)
    for scenario in ("low", "likely", "high"):
        result[f"{scenario}_hours"] = sum(
            (getattr(task, f"{scenario}_hours") for task in request.tasks), Decimal(0)
        )
        cost = sum((getattr(task, f"{scenario}_hours") * task.hourly_rate_usd
                    for task in request.tasks), Decimal(0))
        result[f"{scenario}_cost_usd"] = (cost * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return BudgetTotals(**result)
