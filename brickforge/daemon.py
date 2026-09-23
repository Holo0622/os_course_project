"""丁：厂务守护进程。必须是独立进程，不许用前端定时器冒充。"""

from __future__ import annotations

import os
import time
from multiprocessing import Process
from pathlib import Path

from brickforge.persist import DATA, append_log, load_status, save_status

HB_DIR = DATA / "heartbeats"
PID_FILE = DATA / "daemon.pid"


def daemonize_posix() -> None:
    if os.name != "posix":
        return
    if os.fork() > 0:
        os._exit(0)
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    os.umask(0o22)


def daemon_loop(interval: float = 2.0) -> None:
    HB_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    append_log(time.strftime("%H:%M:%S") + " 厂务精灵启动 pid=" + str(os.getpid()))
    restarts = 0
    while True:
        now = time.strftime("%H:%M:%S")
        stale = []
        cutoff = time.time() - 6
        for path in HB_DIR.glob("*.hb"):
            try:
                stamp = float(path.read_text(encoding="utf-8").strip() or "0")
            except OSError:
                continue
            if stamp < cutoff:
                stale.append(path.stem)
                path.unlink(missing_ok=True)
                restarts += 1
        append_log(f"{now} 心跳巡视 超时车间={stale or '无'} 累计拉起={restarts}")
        status = load_status()
        status.update(
            {
                "daemon_pid": os.getpid(),
                "daemon_alive": True,
                "restarts": restarts,
                "stale": stale,
                "checked_at": now,
            }
        )
        save_status(status)
        time.sleep(interval)


def start_daemon() -> Process:
    proc = Process(target=_entry, name="factory-daemon", daemon=False)
    proc.start()
    return proc


def _entry() -> None:
    try:
        daemonize_posix()
    except OSError:
        pass
    daemon_loop()


def stop_daemon(proc: Process | None) -> None:
    if proc is not None and proc.is_alive():
        proc.terminate()
        proc.join(timeout=2)
    if PID_FILE.exists():
        PID_FILE.unlink()
