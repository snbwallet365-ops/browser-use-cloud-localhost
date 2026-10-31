import uuid
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import aiosqlite
from app.config import DB_PATH
from app.agent_runner import run_agent_task, active_sessions
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

class TaskCreate(BaseModel):
    task: str
    model_profile_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    workspace_id: str = "default"

class FollowUp(BaseModel):
    task: str

@router.post("")
async def create_task(req: TaskCreate):
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    settings_dict = req.settings or {}
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        profile_query = "SELECT * FROM model_profiles WHERE id = ?"
        params = [req.model_profile_id]
        if not req.model_profile_id:
            profile_query = "SELECT * FROM model_profiles WHERE is_default = 1 LIMIT 1"
            params = []
        cursor = await db.execute(profile_query, params)
        profile = await cursor.fetchone()
        
        profile_dict = dict(profile) if profile else {
            "id": "default-fallback",
            "name": "Default OpenAI",
            "provider": "openai",
            "model": "gpt-4o",
            "api_key_enc": "",
            "base_url": None,
            "temperature": 0.7,
            "extra_params": "{}"
        }

        await db.execute("""
            INSERT INTO tasks (id, workspace_id, task, model_profile_id, status, max_steps, settings_json)
            VALUES (?, ?, ?, ?, 'queued', ?, ?)
        """, (task_id, req.workspace_id, req.task, profile_dict["id"], settings_dict.get("max_steps", 100), json.dumps(settings_dict)))
        await db.commit()

    asyncio.create_task(run_agent_task(task_id, req.task, profile_dict, settings_dict, req.workspace_id))
    return {"id": task_id, "status": "queued"}

@router.get("/{task_id}")
async def get_task(task_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = await cursor.fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        cursor = await db.execute("SELECT * FROM task_steps WHERE task_id = ? ORDER BY step_number ASC", (task_id,))
        steps = await cursor.fetchall()
        
        return {
            **dict(task),
            "settings": json.loads(task["settings_json"] or "{}"),
            "steps": [dict(s) for s in steps]
        }

@router.get("/{task_id}/events")
async def stream_task_events(task_id: str):
    session = active_sessions.get(task_id)
    queue = asyncio.Queue()
    if session:
        session.subscribers.append(queue)

    async def event_generator():
        if session and session.latest_screenshot:
            yield f"data: {json.dumps({'type': 'screenshot', 'data': {'screenshot': session.latest_screenshot}})}\n\n"
        try:
            while True:
                msg = await queue.get()
                yield f"data: {msg}\n\n"
                parsed = json.loads(msg)
                if parsed.get("type") in ("finished", "error"):
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if session and queue in session.subscribers:
                session.subscribers.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/{task_id}/stop")
async def stop_task(task_id: str):
    session = active_sessions.get(task_id)
    if not session:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE tasks SET status = 'stopped' WHERE id = ?", (task_id,))
            await db.commit()
        return {"status": "stopped"}

    session.stop_requested = True
    try:
        session.agent.stop()
    except Exception:
        pass
    return {"status": "stopping"}

@router.post("/{task_id}/follow-up")
async def follow_up(task_id: str, req: FollowUp):
    session = active_sessions.get(task_id)
    if not session:
        raise HTTPException(status_code=400, detail="Active browser session closed.")
    asyncio.create_task(session.agent.step())
    return {"status": "resumed", "task": req.task}
