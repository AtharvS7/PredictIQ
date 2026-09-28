"""Authenticated, owner-scoped manual task budgets. No model invocation."""
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.models.budget import BudgetRequest, SavedBudget, calculate_budget

router = APIRouter()


def saved_budget(row):
    inputs = BudgetRequest.model_validate(json.loads(row["inputs_json"]))
    return SavedBudget(id=row["id"], created_at=row["created_at"], inputs=inputs,
                       totals=calculate_budget(inputs))


@router.post("/budgets", response_model=SavedBudget, status_code=201)
async def create_budget(body: BudgetRequest, user: CurrentUser = Depends(require_role("editor"))):
    pool = await get_db()
    row = await pool.fetchrow(
        "INSERT INTO budgets(user_id, inputs_json) VALUES($1, $2::jsonb) RETURNING *",
        user.id, body.model_dump_json(),
    )
    return saved_budget(row)


@router.get("/budgets", response_model=list[SavedBudget])
async def list_budgets(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                       user: CurrentUser = Depends(get_current_user)):
    pool = await get_db()
    rows = await pool.fetch(
        "SELECT * FROM budgets WHERE user_id=$1 ORDER BY created_at DESC, id DESC LIMIT $2 OFFSET $3",
        user.id, limit, offset,
    )
    return [saved_budget(row) for row in rows]


@router.get("/budgets/{budget_id}", response_model=SavedBudget)
async def get_budget(budget_id: UUID, user: CurrentUser = Depends(get_current_user)):
    pool = await get_db()
    row = await pool.fetchrow("SELECT * FROM budgets WHERE id=$1 AND user_id=$2", budget_id, user.id)
    if row is None:
        raise HTTPException(404, "Budget not found")
    return saved_budget(row)


@router.delete("/budgets/{budget_id}", status_code=204)
async def delete_budget(budget_id: UUID, user: CurrentUser = Depends(require_role("editor"))):
    pool = await get_db()
    result = await pool.execute("DELETE FROM budgets WHERE id=$1 AND user_id=$2", budget_id, user.id)
    if result != "DELETE 1":
        raise HTTPException(404, "Budget not found")
