"""丙：车间进程与机器线程。每个车间一个 Process，每台机器一个 Thread。"""

from __future__ import annotations

import time
from pathlib import Path
from queue import Empty
from threading import Thread

from brickforge.persist import DATA

HB_DIR = DATA / "heartbeats"


def beat(shop_id: str) -> None:
    HB_DIR.mkdir(parents=True, exist_ok=True)
    (HB_DIR / f"{shop_id}.hb").write_text(str(time.time()), encoding="utf-8")


def shop_worker(
    shop: dict,
    jobs: list[dict],
    material,
    report_q,
    tick: float = 0.03,
) -> None:
    beat(shop["id"])
    finished = []
    blocked = 0
    machines = shop.get("machines") or [{"id": "idle", "burst": 1}]

    def machine_loop(machine: dict, assigned: list[dict]) -> None:
        nonlocal blocked
        for job in assigned:
            beat(shop["id"])
            got = material.acquire(timeout=0.4)
            if not got:
                blocked += 1
                continue
            staff = max(int(machine.get("workers") or 0), 0)
            pace = max(0.22, 0.12 + min(staff, 3) * 0.42)
            time.sleep(max(job.get("burst", 1), 1) * tick / pace)
            material.release()
            finished.append({"job": job["id"], "machine": machine.get("id"), "shop": shop["id"]})
            beat(shop["id"])

    threads = []
    if not jobs:
        beat(shop["id"])
    else:
        chunks = [[] for _ in machines]
        for i, job in enumerate(jobs):
            chunks[i % len(machines)].append(job)
        for machine, assigned in zip(machines, chunks):
            th = Thread(target=machine_loop, args=(machine, assigned), daemon=True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()
    report_q.put(
        {
            "shop_id": shop["id"],
            "finished": finished,
            "blocked": blocked,
            "pid": os_pid(),
        }
    )


def os_pid() -> int:
    import os

    return os.getpid()


def drain(q, expected: int, timeout: float = 8.0) -> list:
    got = []
    deadline = time.time() + timeout
    while len(got) < expected and time.time() < deadline:
        try:
            got.append(q.get(timeout=0.2))
        except Empty:
            continue
    return got
