import threading

import requests


class ThreadSessions:
    def __init__(self) -> None:
        self.local = threading.local()
        self.lock = threading.Lock()
        self.sessions: list[requests.Session] = []

    def get(self) -> requests.Session:
        if not hasattr(self.local, "session"):
            session = requests.Session()
            with self.lock:
                self.sessions.append(session)
            self.local.session = session
        return self.local.session

    def close_all(self) -> None:
        with self.lock:
            sessions = list(self.sessions)
            self.sessions.clear()
        for session in sessions:
            session.close()
