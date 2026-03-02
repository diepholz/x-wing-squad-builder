import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

# Allow override via environment variable (needed in Docker where path depth differs)
_env_path = os.environ.get("DEFINITION_PATH")
DEFINITION_PATH = (
    Path(_env_path) if _env_path
    else Path(__file__).resolve().parents[4] / "data" / "definition.json"
)


@lru_cache(maxsize=1)
def _load_definition() -> dict:
    with open(DEFINITION_PATH) as f:
        return json.load(f)


@router.get("/definition")
async def get_definition():
    """Return the full definition.json payload (factions + upgrades)."""
    return _load_definition()


@router.get("/factions")
async def get_factions():
    return _load_definition()["factions"]


@router.get("/upgrades")
async def get_upgrades():
    return _load_definition()["upgrades"]
