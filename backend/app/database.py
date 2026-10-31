import aiosqlite
from app.config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS model_profiles (
                id TEXT PRIMARY KEY,
                workspace_id TEXT DEFAULT 'default',
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                api_key_enc TEXT,
                base_url TEXT,
                temperature REAL DEFAULT 0.7,
                extra_params TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                workspace_id TEXT DEFAULT 'default',
                task TEXT NOT NULL,
                model_profile_id TEXT,
                status TEXT NOT NULL,
                steps_count INTEGER DEFAULT 0,
                max_steps INTEGER DEFAULT 100,
                settings_json TEXT,
                final_result TEXT,
                error_message TEXT,
                duration_seconds REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS task_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                goal TEXT,
                action TEXT,
                result TEXT,
                screenshot_b64 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id TEXT DEFAULT 'default',
                task_id TEXT,
                model_profile_id TEXT,
                steps_count INTEGER DEFAULT 0,
                duration_seconds REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.execute("INSERT OR IGNORE INTO workspaces (id, name) VALUES ('default', 'Default Workspace');")
        await db.commit()
