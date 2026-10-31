import uuid
import json
from fastapi import APIRouter
import aiosqlite
from app.config import DB_PATH
from app.security import encrypt_secret, mask_secret, decrypt_secret
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/models", tags=["Model Profiles"])

class ProfileCreate(BaseModel):
    name: str
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    extra_params: Optional[Dict[str, Any]] = None
    is_default: bool = False

@router.get("")
async def list_profiles(workspace_id: str = "default"):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM model_profiles WHERE workspace_id = ? ORDER BY created_at DESC", (workspace_id,))
        rows = await cursor.fetchall()
        result = []
        for r in rows:
            raw_key = decrypt_secret(r["api_key_enc"] or "")
            result.append({
                "id": r["id"],
                "name": r["name"],
                "provider": r["provider"],
                "model": r["model"],
                "masked_key": mask_secret(raw_key),
                "base_url": r["base_url"],
                "temperature": r["temperature"],
                "is_default": bool(r["is_default"])
            })
        return result

@router.post("")
async def create_profile(req: ProfileCreate, workspace_id: str = "default"):
    pid = f"mod_{uuid.uuid4().hex[:10]}"
    enc_key = encrypt_secret(req.api_key or "")
    async with aiosqlite.connect(DB_PATH) as db:
        if req.is_default:
            await db.execute("UPDATE model_profiles SET is_default = 0 WHERE workspace_id = ?", (workspace_id,))
        await db.execute("""
            INSERT INTO model_profiles (id, workspace_id, name, provider, model, api_key_enc, base_url, temperature, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pid, workspace_id, req.name, req.provider, req.model, enc_key, req.base_url, req.temperature, 1 if req.is_default else 0))
        await db.commit()
    return {"id": pid, "name": req.name}

@router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM model_profiles WHERE id = ?", (profile_id,))
        await db.commit()
    return {"deleted": True}
