import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from app.config import IS_SUPABASE, SUPABASE_URL, SUPABASE_KEY, SQLITE_DB_PATH

class DatabaseAdapter:
    def __init__(self):
        self.is_supabase = IS_SUPABASE
        self.supabase_client: Optional[Client] = None
        
        if self.is_supabase:
            try:
                print(f"Connecting to Supabase at: {SUPABASE_URL}")
                self.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except Exception as e:
                print(f"Failed to connect to Supabase: {e}. Falling back to SQLite.")
                self.is_supabase = False
        
        if not self.is_supabase:
            print(f"Running in SQLite mode. Database path: {SQLITE_DB_PATH}")
            self._init_sqlite()

    def _init_sqlite(self):
        """Initialize SQLite database schemas if they do not exist."""
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Create organizations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            config TEXT DEFAULT '{}'
        )
        """)
        
        # Create knowledge_nodes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('CONSTRAINT', 'DECISION', 'ANTI_PATTERN', 'FACT')),
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            importance DECIMAL(3,2) NOT NULL,
            derivability_score DECIMAL(3,2) DEFAULT 0.5,
            derivability_class TEXT DEFAULT 'UNKNOWN' CHECK (derivability_class IN (
                'DERIVABLE', 'PARTIALLY_DERIVABLE', 'NON_DERIVABLE', 'UNKNOWN'
            )),
            non_derivable_portion TEXT,
            expected_derivability TEXT,
            expected_score_range TEXT,
            department TEXT,
            tokens_full INTEGER,
            tokens_delta INTEGER,
            scoring_reason TEXT,
            type_floor_applied BOOLEAN DEFAULT FALSE,
            never_exclude BOOLEAN DEFAULT FALSE,
            confidence TEXT DEFAULT 'MEDIUM',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (org_id) REFERENCES organizations(id)
        )
        """)
        
        # Ensure new columns exist (migration helper)
        try:
            cursor.execute("ALTER TABLE knowledge_nodes ADD COLUMN never_exclude BOOLEAN DEFAULT FALSE")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE knowledge_nodes ADD COLUMN confidence TEXT DEFAULT 'MEDIUM'")
        except sqlite3.OperationalError:
            pass
            
        conn.commit()
        conn.close()

    def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve organization by ID."""
        if self.is_supabase:
            try:
                response = self.supabase_client.table("organizations").select("*").eq("id", org_id).execute()
                if response.data:
                    org = response.data[0]
                    # In some environments, Supabase might return config as a dict or a string
                    if isinstance(org.get("config"), str):
                        org["config"] = json.loads(org["config"])
                    return org
            except Exception as e:
                print(f"Supabase get_organization error: {e}. Attempting SQLite fallback.")
        
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organizations WHERE id = ?", (org_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            org = dict(row)
            org["config"] = json.loads(org["config"]) if org["config"] else {}
            return org
        return None

    def update_organization_config(self, org_id: str, config: Dict[str, Any]) -> bool:
        """Update organization configuration."""
        if self.is_supabase:
            try:
                # Supabase handles JSON fields directly
                response = self.supabase_client.table("organizations").update({"config": config}).eq("id", org_id).execute()
                if response.data:
                    return True
            except Exception as e:
                print(f"Supabase update_organization_config error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE organizations SET config = ? WHERE id = ?",
            (json.dumps(config), org_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def get_nodes(self, org_id: str) -> List[Dict[str, Any]]:
        """Retrieve all knowledge nodes for an organization."""
        if self.is_supabase:
            try:
                response = self.supabase_client.table("knowledge_nodes").select("*").eq("org_id", org_id).execute()
                return response.data or []
            except Exception as e:
                print(f"Supabase get_nodes error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_nodes WHERE org_id = ?", (org_id,))
        rows = cursor.fetchall()
        conn.close()
        
        nodes = []
        for r in rows:
            node = dict(r)
            # SQLite does not support true boolean types; convert integer to boolean
            node["type_floor_applied"] = bool(node["type_floor_applied"])
            node["never_exclude"] = bool(node.get("never_exclude", False))
            nodes.append(node)
        return nodes

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific knowledge node by ID."""
        if self.is_supabase:
            try:
                response = self.supabase_client.table("knowledge_nodes").select("*").eq("id", node_id).execute()
                if response.data:
                    return response.data[0]
            except Exception as e:
                print(f"Supabase get_node error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            node = dict(row)
            node["type_floor_applied"] = bool(node["type_floor_applied"])
            node["never_exclude"] = bool(node.get("never_exclude", False))
            return node
        return None

    def upsert_node(self, node_data: Dict[str, Any]) -> bool:
        """Insert or update a knowledge node."""
        if self.is_supabase:
            try:
                response = self.supabase_client.table("knowledge_nodes").upsert(node_data).execute()
                if response.data:
                    return True
            except Exception as e:
                print(f"Supabase upsert_node error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Build SQL dynamic statement for SQLite
        keys = list(node_data.keys())
        values = list(node_data.values())
        
        # SQLite: translate Boolean values to integers
        processed_values = []
        for v in values:
            if isinstance(v, bool):
                processed_values.append(1 if v else 0)
            else:
                processed_values.append(v)
                
        placeholders = ", ".join(["?"] * len(keys))
        columns = ", ".join(keys)
        update_clause = ", ".join([f"{k} = EXCLUDED.{k}" for k in keys if k != "id"])
        
        query = f"""
        INSERT INTO knowledge_nodes ({columns})
        VALUES ({placeholders})
        ON CONFLICT(id) DO UPDATE SET {update_clause}
        """
        
        cursor.execute(query, processed_values)
        conn.commit()
        conn.close()
        return True

    def update_node_scores(self, node_id: str, score_data: Dict[str, Any]) -> bool:
        """Update computed scoring fields of a node."""
        if self.is_supabase:
            try:
                response = self.supabase_client.table("knowledge_nodes").update(score_data).eq("id", node_id).execute()
                if response.data:
                    return True
            except Exception as e:
                print(f"Supabase update_node_scores error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        set_clauses = []
        values = []
        for k, v in score_data.items():
            set_clauses.append(f"{k} = ?")
            if isinstance(v, bool):
                values.append(1 if v else 0)
            else:
                values.append(v)
        
        values.append(node_id)
        set_str = ", ".join(set_clauses)
        
        cursor.execute(f"UPDATE knowledge_nodes SET {set_str} WHERE id = ?", values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def clear_all(self):
        """Clear the database tables (used during re-seeding)."""
        if self.is_supabase:
            try:
                # Execute delete
                self.supabase_client.table("knowledge_nodes").delete().neq("id", "none").execute()
                self.supabase_client.table("organizations").delete().neq("id", "none").execute()
                return
            except Exception as e:
                print(f"Supabase clear_all error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_nodes")
        cursor.execute("DELETE FROM organizations")
        conn.commit()
        conn.close()

    def insert_organization(self, org_id: str, name: str, config: Dict[str, Any]) -> bool:
        """Insert or replace an organization."""
        if self.is_supabase:
            try:
                response = self.supabase_client.table("organizations").upsert({
                    "id": org_id,
                    "name": name,
                    "config": config
                }).execute()
                if response.data:
                    return True
            except Exception as e:
                print(f"Supabase insert_organization error: {e}. Attempting SQLite fallback.")
                
        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO organizations (id, name, config) VALUES (?, ?, ?)",
            (org_id, name, json.dumps(config))
        )
        conn.commit()
        conn.close()
        return True

# Singleton database adapter instance
db = DatabaseAdapter()
