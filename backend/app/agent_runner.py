import asyncio
import time
import json
import base64
from typing import Dict, Any
import aiosqlite
from browser_use import Agent, Browser, BrowserConfig
from app.config import DB_PATH, PROFILES_DIR
from app.llm_factory import create_llm_instance

class ActiveSession:
    def __init__(self, task_id: str, browser: Browser, agent: Agent):
        self.task_id = task_id
        self.browser = browser
        self.agent = agent
        self.stop_requested = False
        self.subscribers: list[asyncio.Queue] = []
        self.latest_screenshot = ""

active_sessions: Dict[str, ActiveSession] = {}

async def broadcast_event(session: ActiveSession, event_type: str, data: Dict[str, Any]):
    message = json.dumps({"type": event_type, "data": data})
    for q in list(session.subscribers):
        try:
            await q.put(message)
        except Exception:
            session.subscribers.remove(q)

async def run_agent_task(task_id: str, task_text: str, model_profile: dict, settings: dict, workspace_id: str = "default"):
    start_time = time.time()
    user_data_dir = None
    if settings.get("browser_profile_id"):
        user_data_dir = str(PROFILES_DIR / settings["browser_profile_id"])

    browser_config = BrowserConfig(
        headless=settings.get("headless", True),
        cdp_url=settings.get("cdp_url") or None,
        user_data_dir=user_data_dir,
    )
    browser = Browser(config=browser_config)
    llm = create_llm_instance(model_profile)

    agent = Agent(
        task=task_text,
        llm=llm,
        browser=browser,
        use_vision=settings.get("use_vision", "auto") != "false",
        max_failures=settings.get("max_failures", 5),
        sensitive_data=settings.get("sensitive_data", {})
    )

    session = ActiveSession(task_id=task_id, browser=browser, agent=agent)
    active_sessions[task_id] = session

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tasks SET status = 'running' WHERE id = ?", (task_id,))
        await db.commit()

    step_counter = 0

    async def step_callback(agent_state):
        nonlocal step_counter
        step_counter += 1
        screenshot_b64 = ""
        try:
            page = await browser.get_current_page()
            if page:
                bytes_data = await page.screenshot(type="jpeg", quality=65)
                screenshot_b64 = base64.b64encode(bytes_data).decode("utf-8")
                session.latest_screenshot = screenshot_b64
        except Exception:
            pass

        goal = getattr(agent_state, "goal", f"Step {step_counter}")
        action = str(getattr(agent_state, "action", ""))
        result = str(getattr(agent_state, "result", ""))

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO task_steps (task_id, step_number, goal, action, result, screenshot_b64)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (task_id, step_counter, goal, action, result, screenshot_b64))
            await db.execute("UPDATE tasks SET steps_count = ? WHERE id = ?", (step_counter, task_id))
            await db.commit()

        await broadcast_event(session, "step", {
            "step": step_counter,
            "goal": goal,
            "action": action,
            "result": result,
            "screenshot": screenshot_b64
        })

    agent.register_new_step_callback(step_callback)

    try:
        max_steps = settings.get("max_steps", 100)
        history = await agent.run(max_steps=max_steps)
        final_result = history.final_result() if hasattr(history, "final_result") else "Task finished successfully."
        duration = round(time.time() - start_time, 2)
        status = "stopped" if session.stop_requested else "finished"

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE tasks
                SET status = ?, final_result = ?, duration_seconds = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, final_result, duration, task_id))
            await db.commit()

        await broadcast_event(session, "finished", {
            "status": status,
            "final_result": final_result,
            "duration": duration,
            "steps": step_counter
        })
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        error_msg = str(e)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                UPDATE tasks
                SET status = 'error', error_message = ?, duration_seconds = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (error_msg, duration, task_id))
            await db.commit()

        await broadcast_event(session, "error", {"error": error_msg})
    finally:
        if session.stop_requested:
            try:
                await browser.close()
            except Exception:
                pass
            active_sessions.pop(task_id, None)
