"""丁：仓储分配。货架 = 内存分区，首次适应 / 最佳适应。不要改乙的调度、丙的缓冲。"""

from __future__ import annotations


def allocate(shelves: list[int], demand: int, policy: str = "best") -> dict:
    """shelves 是各货架剩余空间。返回放入的下标和碎片。"""
    candidates = [(i, space) for i, space in enumerate(shelves) if space >= demand]
    if not candidates:
        return {"ok": False, "index": -1, "fragment": 0, "shelves": shelves}
    if policy == "first":
        index, space = candidates[0]
    elif policy == "worst":
        index, space = max(candidates, key=lambda item: item[1] - demand)
    else:
        index, space = min(candidates, key=lambda item: item[1] - demand)
    leftover = space - demand
    updated = list(shelves)
    updated[index] = leftover
    return {"ok": True, "index": index, "fragment": leftover, "shelves": updated}


def pack_jobs(sizes: list[int], shelves: list[int], policy: str = "best") -> dict:
    current = list(shelves)
    origin = list(shelves)
    placed = 0
    fragments = []
    rejected = 0
    log = []
    for size in sizes:
        result = allocate(current, size, policy)
        current = result["shelves"]
        log.append(
            {
                "size": size,
                "ok": result["ok"],
                "index": result["index"],
                "fragment": result["fragment"],
            }
        )
        if result["ok"]:
            placed += 1
            fragments.append(result["fragment"])
        else:
            rejected += 1
    frag_rate = 0.0
    if current:
        frag_rate = round(sum(1 for s in current if 0 < s < 3) / len(current), 2)
    return {
        "placed": placed,
        "rejected": rejected,
        "fragment_rate": frag_rate,
        "shelves": current,
        "origin": origin,
        "policy": policy,
        "log": log,
    }
