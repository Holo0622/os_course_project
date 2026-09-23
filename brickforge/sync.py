"""丙：同步与 IPC。传送带 = 有界缓冲，库位 = 信号量，工单 = 消息队列。不要改乙的调度算法。"""

from __future__ import annotations


def line_buffers(shops: list[dict], capacity: int = 6) -> dict:
    """每条传送带是容量有限的缓冲槽，人少或没接上就会空转/堵住。"""
    cap = max(int(capacity or 6), 1)
    belts = []
    for shop in shops:
        machines = {m.get("id"): m for m in (shop.get("machines") or []) if m.get("id")}
        ids = set(machines)
        for wire in shop.get("wires") or []:
            src, dst = wire.get("from"), wire.get("to")
            if src not in ids or dst not in ids or src == dst:
                continue
            staff = min(max(int(machines[src].get("workers") or 0), 0), 3)
            fill = 0 if staff == 0 else min(cap, 1 + staff * 2)
            waiters = 0 if staff else 1
            belts.append(
                {
                    "shop": shop.get("name") or shop.get("id"),
                    "from": machines[src].get("name") or src,
                    "to": machines[dst].get("name") or dst,
                    "capacity": cap,
                    "fill": fill,
                    "waiters": waiters,
                }
            )
    used = sum(b["fill"] for b in belts)
    slots = sum(b["capacity"] for b in belts) or cap
    return {
        "owner": "丙",
        "kinds": ["消息队列(工单)", "信号量(库位)", "有界缓冲(传送带)"],
        "belts": belts,
        "buffer_slots": slots,
        "buffer_used": used,
        "empty_belts": sum(1 for b in belts if b["fill"] == 0),
    }


def describe(blocked: int, slots: int, buffers: dict) -> str:
    parts = [
        f"信号量槽 {slots}",
        f"传送带缓冲 {buffers.get('buffer_used', 0)}/{buffers.get('buffer_slots', 0)}",
    ]
    if blocked:
        parts.append(f"阻塞 {blocked} 次")
    if buffers.get("empty_belts"):
        parts.append(f"{buffers['empty_belts']} 条带空转")
    return " · ".join(parts)
