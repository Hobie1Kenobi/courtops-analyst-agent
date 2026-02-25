"""Simulation clock that compresses a workday into a few minutes."""

import threading
import time
from datetime import datetime, timedelta

_lock = threading.Lock()

PHASES = [
    ("morning_intake", 0.0, 0.35),
    ("midday_it_ops", 0.35, 0.7),
    ("endofday_monthend_audit", 0.7, 1.0),
]


class SimClock:
    def __init__(self):
        self._running = False
        self._speed = 1.0
        self._start_wall: float | None = None
        self._start_sim: datetime | None = None
        self._sim_date = datetime.utcnow().replace(hour=7, minute=0, second=0, microsecond=0)
        self._progress = 0.0

    def start(self, speed: float = 30.0, sim_date: datetime | None = None):
        with _lock:
            self._speed = speed
            self._start_wall = time.time()
            if sim_date:
                self._sim_date = sim_date.replace(hour=7, minute=0, second=0, microsecond=0)
            self._start_sim = self._sim_date
            self._running = True
            self._progress = 0.0

    def stop(self):
        with _lock:
            self._running = False

    @property
    def running(self) -> bool:
        return self._running

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def sim_now(self) -> datetime:
        if not self._running or self._start_wall is None or self._start_sim is None:
            return self._sim_date
        elapsed = time.time() - self._start_wall
        sim_elapsed = elapsed * self._speed
        return self._start_sim + timedelta(seconds=sim_elapsed)

    @property
    def progress(self) -> float:
        if not self._running or self._start_wall is None:
            return self._progress
        elapsed = time.time() - self._start_wall
        shift_duration_real = (10 * 3600) / self._speed
        self._progress = min(elapsed / shift_duration_real, 1.0)
        return self._progress

    @property
    def phase(self) -> str:
        p = self.progress
        for name, start, end in PHASES:
            if start <= p < end:
                return name
        return "endofday_monthend_audit"

    @property
    def shift_complete(self) -> bool:
        return self.progress >= 1.0

    def state(self) -> dict:
        return {
            "running": self._running,
            "speed": self._speed,
            "sim_time": self.sim_now.isoformat(),
            "progress": round(self.progress, 4),
            "phase": self.phase,
            "shift_complete": self.shift_complete,
        }


sim_clock = SimClock()
