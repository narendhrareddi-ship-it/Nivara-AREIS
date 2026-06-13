"""PostgreSQL client for CRM operations (Replacement for Supabase SDK)."""

from __future__ import annotations

import logging
import os
from typing import Any
from psycopg2 import pool, extras
from nivara.config import settings

logger = logging.getLogger(__name__)

_SSLMODE = os.getenv("DB_SSLMODE", settings.db_sslmode)


class SupabaseCRM:
    """
    Maintains the name SupabaseCRM for backward compatibility with agents and MCP servers,
    but uses a direct PostgreSQL connection for self-hosted offline mode.
    """
    def __init__(self, url: str | None = None, key: str | None = None) -> None:
        # url and key are kept for signature compatibility but ignored in Postgres mode
        self._host = settings.db_host
        self._port = settings.db_port
        self._user = settings.db_user
        self._password = settings.db_password
        self._dbname = settings.db_name
        self._pool: pool.SimpleConnectionPool | None = None

    def _get_pool(self) -> pool.SimpleConnectionPool:
        if self._pool is None:
            try:
                self._pool = pool.SimpleConnectionPool(
                    1, 10,
                    user=self._user,
                    password=self._password,
                    host=self._host,
                    port=self._port,
                    database=self._dbname,
                    sslmode=_SSLMODE,
                )
            except Exception as e:
                logger.error("Failed to initialize Postgres pool: %s", e)
                raise RuntimeError(f"Could not connect to Postgres: {e}")
        return self._pool

    def is_configured(self) -> bool:
        return bool(self._host and self._user and self._dbname)

    def _adapt_params(self, data: dict[str, Any]) -> tuple[Any, ...]:
        adapted = []
        for value in data.values():
            if isinstance(value, (dict, list)):
                adapted.append(extras.Json(value))
            else:
                adapted.append(value)
        return tuple(adapted)

    def _execute_query(self, query: str, params: tuple | list | dict = None, fetch: str = "all") -> Any:
        conn = self._get_pool().getconn()
        try:
            with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch == "all":
                    result = cur.fetchall()
                    conn.commit()
                    return result
                if fetch == "one":
                    result = cur.fetchone()
                    conn.commit()
                    return result
                if fetch == "none":
                    conn.commit()
                    return None
        except Exception as e:
            conn.rollback()
            logger.error("Database query error: %s | Query: %s", e, query)
            raise e
        finally:
            self._get_pool().putconn(conn)

    def get_leads(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = "SELECT * FROM leads"
        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        return self._execute_query(query, tuple(params), fetch="all")

    def get_lead(self, lead_id: str) -> dict[str, Any] | None:
        query = "SELECT * FROM leads WHERE id = %s"
        return self._execute_query(query, (lead_id,), fetch="one")

    def update_lead(self, lead_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if not data:
            return self.get_lead(lead_id) or {}
        
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + [lead_id]
        query = f"UPDATE leads SET {set_clause} WHERE id = %s RETURNING *"
        
        result = self._execute_query(query, tuple(values), fetch="one")
        return result or {}

    def create_lead(self, data: dict[str, Any]) -> dict[str, Any]:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO leads ({cols}) VALUES ({placeholders}) RETURNING *"
        
        result = self._execute_query(query, tuple(data.values()), fetch="one")
        return result or {}

    def log_activity(self, data: dict[str, Any]) -> dict[str, Any]:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO crm_activity ({cols}) VALUES ({placeholders}) RETURNING *"
        
        result = self._execute_query(query, tuple(data.values()), fetch="one")
        return result or {}

    def get_campaigns(self, status: str | None = "active") -> list[dict[str, Any]]:
        query = "SELECT * FROM campaigns"
        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)
        return self._execute_query(query, tuple(params), fetch="all")

    def get_competitors(self, city: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM competitors"
        params = []
        if city:
            query += " WHERE location_city = %s"
            params.append(city)
        return self._execute_query(query, tuple(params), fetch="all")

    def get_ad_performance(self, days: int = 7) -> list[dict[str, Any]]:
        query = "SELECT * FROM ad_performance ORDER BY date DESC LIMIT %s"
        return self._execute_query(query, (days * 10,), fetch="all")

    def get_projects(self, city: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM projects WHERE is_active = true"
        params = []
        if city:
            query += " AND location_city = %s"
            params.append(city)
        return self._execute_query(query, tuple(params), fetch="all")

    def log_bot_action(self, agent_name: str, action: str, status: str, details: str) -> None:
        query = "INSERT INTO bot_logs (agent_name, action, status, details) VALUES (%s, %s, %s, %s)"
        self._execute_query(query, (agent_name, action, status, details), fetch="none")

    def create_social_post(self, data: dict[str, Any]) -> dict[str, Any]:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO social_posts ({cols}) VALUES ({placeholders}) RETURNING *"

        result = self._execute_query(query, self._adapt_params(data), fetch="one")
        return result or {}

    def create_media_asset(self, data: dict[str, Any]) -> dict[str, Any]:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO media_assets ({cols}) VALUES ({placeholders}) RETURNING *"
        result = self._execute_query(query, self._adapt_params(data), fetch="one")
        return result or {}

    def update_media_asset(self, asset_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if not data:
            return self.get_media_asset(asset_id) or {}
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        values = list(self._adapt_params(data)) + [asset_id]
        query = f"UPDATE media_assets SET {set_clause} WHERE id = %s RETURNING *"
        result = self._execute_query(query, tuple(values), fetch="one")
        return result or {}

    def get_media_asset(self, asset_id: str) -> dict[str, Any] | None:
        query = "SELECT * FROM media_assets WHERE id = %s"
        return self._execute_query(query, (asset_id,), fetch="one")

    def get_media_by_project(
        self, project_id: str, asset_type: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM media_assets WHERE project_id = %s"
        params: list[Any] = [project_id]
        if asset_type:
            query += " AND asset_type = %s"
            params.append(asset_type)
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        return self._execute_query(query, tuple(params), fetch="all")

    def get_pending_media_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            "SELECT * FROM media_assets WHERE status IN ('queued', 'generating') "
            "ORDER BY created_at ASC LIMIT %s"
        )
        return self._execute_query(query, (limit,), fetch="all")

    def get_media_ready_to_publish(self, limit: int = 10) -> list[dict[str, Any]]:
        query = (
            "SELECT * FROM media_assets WHERE status = 'completed' AND asset_type = 'video' "
            "AND id NOT IN (SELECT media_asset_id FROM social_posts WHERE media_asset_id IS NOT NULL) "
            "ORDER BY created_at ASC LIMIT %s"
        )
        return self._execute_query(query, (limit,), fetch="all")
