from fastapi import APIRouter
import aiosqlite
from app.config import DB_PATH

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("")
async def list_history(workspace_id: str = "default"):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM tasks WHERE workspace_id = ? ORDER BY created_at DESC", (workspace_id,))
        return [dict(t) for t in await cursor.fetchall()]

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM task_steps WHERE task_id = ?", (task_id,))
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()
    return {"deleted": True}
