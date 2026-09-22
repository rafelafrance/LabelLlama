import threading
import unittest
from unittest.mock import patch

from llama.pylib.thread_sessions import ThreadSessions


class TestThreadSessions(unittest.TestCase):
    def test_get_returns_same_session_per_thread_01(self) -> None:
        """A thread reuses one session for every get."""
        sessions = ThreadSessions()

        first = sessions.get()
        second = sessions.get()

        assert first is second

    def test_different_threads_get_different_sessions_02(self) -> None:
        """Each thread gets a session of its own."""
        sessions = ThreadSessions()
        results: list = []

        def worker() -> None:
            results.append(sessions.get())

        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # One distinct session per thread, plus the main thread's
        assert len(set(results)) == 3
        assert sessions.get() not in results

    def test_sessions_list_tracks_unique_sessions_03(self) -> None:
        """The tracker holds one entry per thread."""
        sessions = ThreadSessions()

        for _ in range(5):
            sessions.get()

        assert len(sessions.sessions) == 1
        assert sessions.sessions[0] is sessions.get()

    def test_concurrent_get_is_thread_safe_04(self) -> None:
        """Threads racing to get sessions neither share nor lose one."""
        n_threads = 8
        sessions = ThreadSessions()
        seen: list[list] = []
        lock = threading.Lock()

        def worker() -> None:
            local_sessions = {sessions.get() for _ in range(25)}
            with lock:
                seen.append(local_sessions)

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread saw exactly one session across all its gets
        assert all(len(s) == 1 for s in seen)
        # And the tracker holds exactly one session per thread
        assert len(sessions.sessions) == n_threads

    def test_close_all_closes_and_clears_05(self) -> None:
        """close_all closes every session and empties the tracker."""
        with patch("llama.pylib.thread_sessions.requests.Session") as mock:
            sessions = ThreadSessions()
            session_a = sessions.get()
            assert sessions.get() is session_a

            sessions.close_all()

        mock.assert_called_once()
        session_a.close.assert_called_once()
        assert sessions.sessions == []

    def test_close_all_is_idempotent_06(self) -> None:
        """Closing an already empty tracker is harmless."""
        with patch("llama.pylib.thread_sessions.requests.Session"):
            sessions = ThreadSessions()
            sessions.get()
            sessions.close_all()

        # A second close_all on an empty tracker must not raise
        sessions.close_all()
        assert sessions.sessions == []


if __name__ == "__main__":
    unittest.main()
