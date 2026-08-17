"""ANCHA's vault — Supabase when configured, SQLite fallback for local dev."""
import json, os, pathlib, sqlite3

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent

try:
    from supabase import create_client
except Exception:
    create_client = None

class DB:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(url, key) if (url and key and create_client) else None
        self.sqlite = None if self.supabase else sqlite3.connect(ROOT / "colony.db")
        if self.sqlite:
            self.sqlite.executescript("""
            CREATE TABLE IF NOT EXISTS laws(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, rule TEXT, active INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, domain TEXT, tools TEXT, manifest TEXT, status TEXT DEFAULT 'dormant');
            CREATE TABLE IF NOT EXISTS missions(id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, kind TEXT, state TEXT DEFAULT 'queued', body TEXT);
            CREATE TABLE IF NOT EXISTS findings(id INTEGER PRIMARY KEY AUTOINCREMENT, tool TEXT, target TEXT, domain TEXT, data TEXT, ts REAL);
            """)
            self.sqlite.commit()

    def add_law(self, name, rule, active=1):
        if self.sqlite:
            self.sqlite.execute("INSERT INTO laws(name,rule,active) VALUES(?,?,?)",
                                (name, rule, active))
            self.sqlite.commit()

    def list_laws(self):
        return self.sqlite.execute("SELECT name, rule, active FROM laws").fetchall() if self.sqlite else []

    def register(self, m):
        if self.sqlite:
            self.sqlite.execute(
                "INSERT OR REPLACE INTO members(name,role,domain,tools,manifest,status) VALUES(?,?,?,?,?,?)",
                (m["name"], m["role"], m["domain"], json.dumps(m.get("tools", [])),
                 json.dumps(m), "dormant"))
            self.sqlite.commit()

    def count_members(self):
        return len(self.sqlite.execute("SELECT name FROM members").fetchall()) if self.sqlite else 0

    def member_for_tool(self, tool):
        rows = self.sqlite.execute("SELECT name, tools, manifest FROM members").fetchall() if self.sqlite else []
        for name, tools_json, manifest in rows:
            if tool in json.loads(tools_json):
                return {"name": name, "manifest": json.loads(manifest)}
        return None

    def member_by_name(self, name):
        row = (self.sqlite.execute("SELECT manifest FROM members WHERE name=?", (name,)).fetchone()
               if self.sqlite else None)
        return {"name": name, "manifest": json.loads(row[0])} if row else None

    def store_finding(self, msg):
        b = msg["body"]
        if self.sqlite:
            self.sqlite.execute(
                "INSERT INTO findings(tool,target,domain,data,ts) VALUES(?,?,?,?,?)",
                (b.get("tool"), b.get("target"), msg["domain"],
                 json.dumps(b.get("data", {})), msg.get("ts", 0)))
            self.sqlite.commit()
        elif self.supabase:
            try:
                self.supabase.table("findings").insert({
                    "tool": b.get("tool"), "target": b.get("target"),
                    "domain": msg["domain"], "data": b.get("data", {})}).execute()
            except Exception:
                pass
