from typing import List, Dict
from collections import deque

class SessionMemory:
    def __init__(self, maxlen: int = 10):
        self.interactions = deque(maxlen=maxlen)

    def add_record(self, payload: Dict):
        self.interactions.appendleft(payload)

    def export_rows(self) -> List[Dict]:
        return list(self.interactions)
