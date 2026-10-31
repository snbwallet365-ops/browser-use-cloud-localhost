from fastapi import APIRouter
import aiosqlite
from app.config import DB_PATH

router = APIRouter(prefix="/api/usage", tags=["Usage"])

@router.get("")
async def get_usage(workspace_id: str = "default"):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT COUNT(*) as total_runs, SUM(steps_count) as total_steps, SUM(duration_seconds) as total_duration
            FROM tasks WHERE workspace_id = ?
        """, (workspace_id,))
        summary = await cursor.fetchone()
        return {"summary": dict(summary) if summary else {}}
