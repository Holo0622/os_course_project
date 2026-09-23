"""系统监视器：PCB、系统调用轨迹。甲只负责画这些 JSON。"""

from __future__ import annotations


def pcb(shops: list[dict], reports: list[dict], timeline: list[dict]) -> list[dict]:
    by_shop = {r.get("shop_id"): r for r in reports}
    rows = []
    for shop in shops:
        rep = by_shop.get(shop.get("id"), {})
        njob = len([t for t in timeline if t.get("shop_id") == shop.get("id")])
        if shop.get("suspended"):
            state = "stopped"
        elif rep.get("blocked"):
            state = "blocked"
        elif njob:
            state = "running"
        else:
            state = "ready"
        rows.append(
            {
                "pid": rep.get("pid") or "—",
                "name": shop.get("name") or shop.get("id"),
                "kind": "进程",
                "state": state,
                "threads": len(shop.get("machines") or []),
                "cpu": njob,
            }
        )
        for machine in shop.get("machines") or []:
            staff = int(machine.get("workers") or 0)
            rows.append(
                {
                    "pid": machine.get("id"),
                    "name": machine.get("name") or machine.get("id"),
                    "kind": "线程",
                    "state": "running" if staff else "sleep",
                    "threads": 0,
                    "cpu": staff,
                }
            )
    for row in timeline:
        rows.append(
            {
                "pid": row.get("id"),
                "name": row.get("name"),
                "kind": "工单",
                "state": "zombie",
                "threads": 0,
                "cpu": row.get("burst"),
            }
        )
    return rows


def syscalls(shops: list[dict], algo: str, slots: int, blocked: int, bank: dict, paging: dict, switches: int) -> list[str]:
    lines = [
        "open(\"data/factory.json\", O_RDWR)",
        "fcntl(fd, F_SETLKW, F_WRLCK)",
    ]
    for shop in shops:
        lines.append(f"fork() → 车间进程 {shop.get('name') or shop.get('id')}")
        for machine in shop.get("machines") or []:
            lines.append(f"clone(CLONE_THREAD) → {machine.get('name') or machine.get('id')}")
    lines.append(f"sem_init(库位, {slots})")
    if blocked:
        lines.append(f"sem_wait() 阻塞 {blocked} 次 EAGAIN")
    else:
        lines.append("sem_wait()/sem_post() 库位未饿死")
    lines.append(f"sched_setscheduler({algo}) 上下文切换 {switches}")
    if bank.get("safe"):
        seq = " → ".join(bank.get("sequence_names") or [])
        lines.append(f"银行家安全序列 {seq or '空'}")
    else:
        lines.append("银行家判定不安全，拒绝超额申请")
    lines.append(
        f"缺页 {paging.get('faults', 0)}/{len(paging.get('refs') or [])} "
        f"置换 {paging.get('algo')} 页框 {paging.get('frames')}"
    )
    lines.append("write(\"data/daemon.log\")")
    lines.append("fcntl(fd, F_SETLK, F_UNLCK); close(fd)")
    return lines
