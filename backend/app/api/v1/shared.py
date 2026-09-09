"""Public, expiry-aware estimate sharing with an explicit privacy-safe DTO."""
import json
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.models.estimate import EstimateInputs, EstimateOutputs

router = APIRouter()


class SharedEstimate(BaseModel):
    project_name: str
    version: int
    created_at: str
    inputs: EstimateInputs
    outputs: EstimateOutputs


class SharedPassword(BaseModel):
    password: str = Field(max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return value


async def read_shared(token: str, password: Optional[str]) -> SharedEstimate:
    if len(token) != 43 or not all(char.isascii() and (char.isalnum() or char in "-_") for char in token):
        raise HTTPException(status_code=404, detail="Share link is unavailable")
    pool = await get_db()
    row = await pool.fetchrow(
        """SELECT s.id AS share_id, s.password_hash, e.project_name, e.version,
                  e.created_at, e.inputs_json, e.outputs_json
           FROM share_links s JOIN estimates e ON e.id=s.estimate_id
           WHERE s.token=$1 AND s.expires_at > NOW() AND e.status='complete'""", token,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Share link is unavailable")
    if row["password_hash"]:
        valid = False
        if password:
            try:
                valid = await run_in_threadpool(bcrypt.checkpw, password.encode(), row["password_hash"].encode())
            except ValueError:
                valid = False
        if not valid:
            raise HTTPException(status_code=401, detail="A valid share password is required")
    # Recheck expiry/deletion while recording a successful view.
    updated = await pool.fetchval(
        """UPDATE share_links s SET view_count=s.view_count+1
           FROM estimates e WHERE s.id=$1 AND e.id=s.estimate_id
             AND s.expires_at > NOW() AND e.status='complete' RETURNING s.id""", row["share_id"],
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Share link is unavailable")
    inputs = row["inputs_json"]
    outputs = row["outputs_json"]
    return SharedEstimate(project_name=row["project_name"], version=row["version"], created_at=str(row["created_at"]),
        inputs=EstimateInputs.model_validate(json.loads(inputs) if isinstance(inputs, str) else inputs),
        outputs=EstimateOutputs.model_validate(json.loads(outputs) if isinstance(outputs, str) else outputs))


@router.get("/shared/{token}", response_model=SharedEstimate)
@limiter.limit("30/minute")
async def get_shared(token: str, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return await read_shared(token, None)


@router.post("/shared/{token}", response_model=SharedEstimate)
@limiter.limit("10/minute")
async def unlock_shared(token: str, payload: SharedPassword, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    return await read_shared(token, payload.password)
