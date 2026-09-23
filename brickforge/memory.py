"""虚拟内存：工单访问的页号进有限页框，FIFO / LRU 置换，统计缺页。"""

from __future__ import annotations


def replace(refs: list[int], frames: int = 4, algo: str = "lru") -> dict:
    cap = max(int(frames or 4), 1)
    frames_list: list[int] = []
    last: dict[int, int] = {}
    faults = 0
    hits = 0
    log = []
    for t, page in enumerate(refs):
        if page in frames_list:
            hits += 1
            last[page] = t
            log.append({"page": page, "hit": True, "frames": list(frames_list)})
            continue
        faults += 1
        if len(frames_list) < cap:
            frames_list.append(page)
        elif algo == "fifo":
            frames_list.pop(0)
            frames_list.append(page)
        else:
            victim = min(frames_list, key=lambda p: last.get(p, -1))
            frames_list[frames_list.index(victim)] = page
        last[page] = t
        log.append({"page": page, "hit": False, "frames": list(frames_list)})
    total = max(len(refs), 1)
    return {
        "algo": algo,
        "frames": cap,
        "refs": refs,
        "faults": faults,
        "hits": hits,
        "fault_rate": round(faults / total, 3),
        "final": frames_list,
        "log": log[-12:],
    }
