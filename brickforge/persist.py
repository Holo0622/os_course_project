"""布局与日志落盘，带跨平台文件锁。"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
LAYOUT = DATA / "factory.json"
STATUS = DATA / "status.json"
DAEMON_LOG = DATA / "daemon.log"
LOCK = DATA / "factory.lock"


@contextmanager
def file_lock():
    LOCK.parent.mkdir(exist_ok=True)
    handle = open(LOCK, "a+b")
    try:
        _lock(handle)
        yield
    finally:
        _unlock(handle)
        handle.close()


def _lock(handle):
    handle.seek(0, 2)
    if handle.tell() < 1:
        handle.write(b"1")
        handle.flush()
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _unlock(handle):
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_layout() -> dict:
    with file_lock():
        if not LAYOUT.exists():
            return default_layout()
        return json.loads(LAYOUT.read_text(encoding="utf-8"))


def save_layout(layout: dict) -> dict:
    with file_lock():
        LAYOUT.write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
    return layout


def save_status(payload: dict) -> None:
    with file_lock():
        STATUS.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_status() -> dict:
    if not STATUS.exists():
        return {}
    return json.loads(STATUS.read_text(encoding="utf-8"))


def append_log(line: str) -> None:
    with file_lock():
        with DAEMON_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line.rstrip() + "\n")


def tail_log(n: int = 12) -> list[str]:
    if not DAEMON_LOG.exists():
        return []
    lines = DAEMON_LOG.read_text(encoding="utf-8").splitlines()
    return lines[-n:]


def default_layout() -> dict:
    return {
        "scheduler": "priority",
        "ship_algo": "sstf",
        "price": 18,
        "raw": 120,
        "raw_kind": "steel",
        "daemon": True,
        "warehouse_policy": "best",
        "shelves": [8, 5, 12, 3],
        "buffer_cap": 6,
        "quantum": 2,
        "page_frames": 4,
        "page_algo": "lru",
        "inbound": {
            "items": [{"id": "in1", "name": "冷轧钢板", "qty": 120, "cap": 3000, "cost": 2}]
        },
        "outbound": {
            "items": [{"id": "out1", "name": "积木成品", "qty": 0, "cap": 3000, "price": 18}]
        },
        "feeds": [{"from": "in1", "to": "s1"}],
        "ships": [{"from": "s2", "to": "out1"}],
        "links": [{"from": "s1", "to": "s2"}],
        "jobs": [
            {"id": "j1", "name": "急单", "burst": 3, "priority": 1, "dest": 12, "sku": "A"},
            {"id": "j2", "name": "普通", "burst": 5, "priority": 2, "dest": 7, "sku": "A"},
            {"id": "j3", "name": "加急", "burst": 4, "priority": 2, "dest": 9, "sku": "A"},
        ],
        "shops": [
            {
                "id": "s1",
                "type": "press",
                "name": "加工车间",
                "x": 40,
                "y": 80,
                "machines": [
                    {"id": "m1", "type": "station", "name": "工位机", "x": 200, "y": 80, "burst": 3, "priority": 1, "workers": 1, "ppm": 20},
                    {"id": "m3", "type": "arm", "name": "机械臂", "x": 400, "y": 20, "burst": 3, "priority": 2, "workers": 1, "ppm": 19},
                    {"id": "m4", "type": "station", "name": "折弯机", "x": 400, "y": 190, "burst": 4, "priority": 2, "workers": 1, "ppm": 16},
                ],
                "wires": [
                    {"from": "__inlet__", "to": "m1"},
                    {"from": "m1", "to": "m3"},
                    {"from": "m1", "to": "m4"},
                    {"from": "m3", "to": "__outlet__"},
                    {"from": "m4", "to": "__outlet__"},
                ],
            },
            {
                "id": "s2",
                "type": "assemble",
                "name": "组装车间",
                "x": 280,
                "y": 80,
                "machines": [
                    {"id": "m2", "type": "arm", "name": "机械臂", "x": 200, "y": 80, "burst": 4, "priority": 2, "workers": 1, "ppm": 15}
                ],
                "wires": [{"from": "__inlet__", "to": "m2"}, {"from": "m2", "to": "__outlet__"}],
            },
        ],
    }
