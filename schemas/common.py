"""Shared response schemas."""
from __future__ import annotations
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    provider: str


class ConfigResponse(BaseModel):
    provider: str
    model: str
    retrieval_top_k: int
    collections: list[str]
    version: str
