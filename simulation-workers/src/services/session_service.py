"""
Service Session pour les simulation workers (persistance réelle en base).
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class SessionService:
    """Service pour persister sessions, visites et actions dans la base backend."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            q = text("SELECT id, status FROM sessions WHERE id = :sid")
            res = await self.db.execute(q, {"sid": session_id})
            row = res.first()
            return dict(row._mapping) if row else None
        except Exception:
            return None

    async def update_session_status(self, session_id: str, status: str) -> bool:
        try:
            if status == 'running':
                q = text("UPDATE sessions SET status = :st, started_at = now() WHERE id = :sid")
            elif status in ('completed', 'failed', 'timeout'):
                q = text("UPDATE sessions SET status = :st, completed_at = now() WHERE id = :sid")
            else:
                q = text("UPDATE sessions SET status = :st WHERE id = :sid")
            await self.db.execute(q, {"sid": session_id, "st": status})
            await self.db.commit()
            return True
        except Exception:
            return False

    async def update_session_completion(self, session_id: str, pages_visited: int, actions_performed: int, total_duration: float) -> bool:
        try:
            q = text(
                """
                UPDATE sessions 
                SET status = 'completed',
                    session_duration_ms = :dur,
                    pages_visited = :pages,
                    total_actions = :acts,
                    completed_at = now()
                WHERE id = :sid
                """
            )
            await self.db.execute(q, {
                "sid": session_id,
                "dur": int(total_duration * 1000),
                "pages": pages_visited,
                "acts": actions_performed,
            })
            await self.db.commit()
            return True
        except Exception:
            return False

    async def create_page_visit(self, visit_data: Dict[str, Any]) -> Optional[str]:
        """Insère une page_visit et retourne son id."""
        try:
            q = text(
                """
                INSERT INTO page_visits (session_id, url, title, visit_order, arrived_at, dwell_time_ms, actions_count, scroll_depth_percent)
                VALUES (:sid, :url, :title, :vorder, now(), :dwell, :acnt, :scroll)
                RETURNING id
                """
            )
            params = {
                "sid": visit_data["session_id"],
                "url": visit_data.get("url", ""),
                "title": visit_data.get("title"),
                "vorder": int(visit_data.get("page_number", 1) or 1),
                "dwell": int(visit_data.get("load_time", 0) or 0),
                "acnt": 0,
                "scroll": 0,
            }
            res = await self.db.execute(q, params)
            row = res.first()
            await self.db.commit()
            return str(row[0]) if row else None
        except Exception:
            return None

    async def create_action(self, action_data: Dict[str, Any]) -> Optional[str]:
        """Insère une action pour la page_visit correspondant à (session_id, page_number)."""
        try:
            # Récupérer la page_visit
            q_visit = text(
                "SELECT id FROM page_visits WHERE session_id = :sid AND visit_order = :vorder LIMIT 1"
            )
            res = await self.db.execute(q_visit, {
                "sid": action_data["session_id"],
                "vorder": int(action_data.get("page_number", 1) or 1)
            })
            vrow = res.first()
            if not vrow:
                return None
            page_visit_id = vrow[0]

            # Déterminer l'ordre
            q_ord = text("SELECT COALESCE(MAX(action_order), 0) + 1 FROM actions WHERE page_visit_id = :pvid")
            orow = (await self.db.execute(q_ord, {"pvid": page_visit_id})).first()
            action_order = int(orow[0]) if orow else 1

            # Mapper le type
            raw_type = str(action_data.get("action_type", "click")).lower()
            action_type = "type" if raw_type in ("typing", "type") else raw_type

            q_ins = text(
                """
                INSERT INTO actions (page_visit_id, action_type, element_selector, element_text, coordinates_x, coordinates_y, input_value, action_order, duration_ms)
                VALUES (:pvid, :atype, :selector, :text, :x, :y, :input, :aorder, :dur)
                RETURNING id
                """
            )
            details = action_data.get("details") or {}
            params = {
                "pvid": page_visit_id,
                "atype": action_type,
                "selector": details.get("selector"),
                "text": details.get("text"),
                "x": details.get("x"),
                "y": details.get("y"),
                "input": details.get("text_length"),
                "aorder": action_order,
                "dur": int(details.get("duration_ms", 0) or 0),
            }
            row = (await self.db.execute(q_ins, params)).first()

            # Incrémenter le compteur d'actions de la visite
            await self.db.execute(text("UPDATE page_visits SET actions_count = actions_count + 1 WHERE id = :pvid"), {"pvid": page_visit_id})

            await self.db.commit()
            return str(row[0]) if row else None
        except Exception:
            return None

    async def delete_session(self, session_id: str) -> bool:
        try:
            await self.db.execute(text("DELETE FROM sessions WHERE id = :sid"), {"sid": session_id})
            await self.db.commit()
            return True
        except Exception:
            return False
