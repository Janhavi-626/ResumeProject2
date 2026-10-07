from __future__ import annotations

from collections import defaultdict, deque
from typing import Deque, Dict, List, Optional


class MemoryService:
    def __init__(self) -> None:
        self.session_memory: Dict[str, Deque[Dict[str, str]]] = defaultdict(lambda: deque(maxlen=25))
        self.workflow_state: Dict[str, Dict[str, object]] = {}

    def add_message(self, session_id: str, role: str, content: str) -> None:
        self.session_memory[session_id].append({"role": role, "content": content})

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        return list(self.session_memory.get(session_id, []))

    def save_workflow_state(self, workflow_id: str, state: Dict[str, object]) -> None:
        self.workflow_state[workflow_id] = state

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, object]]:
        return self.workflow_state.get(workflow_id)


memory_service = MemoryService()
