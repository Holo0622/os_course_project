"""操作系统原语冒烟：银行家、分页、SCAN。"""

from brickforge.banker import snapshot
from brickforge.memory import replace
from brickforge.scheduler import Job, compare, run
from brickforge.shipping import run as ship


def main():
    jobs = [
        Job("j1", "急单", 3, 1, dest=12),
        Job("j2", "普通", 5, 2, dest=7),
        Job("j3", "短单", 2, 2, dest=4),
    ]
    bank = snapshot(jobs)
    assert "safe" in bank
    assert len(bank["need"]) == 3
    pages = replace([1, 2, 3, 1, 4, 2], frames=3, algo="lru")
    assert pages["faults"] >= 3
    scan = ship([12, 3, 18, 7], "scan")
    sstf = ship([12, 3, 18, 7], "sstf")
    assert scan["distance"] >= 0 and sstf["distance"] >= 0
    srtf = run(jobs, "srtf")
    mlfq = run(jobs, "mlfq")
    assert srtf and mlfq
    table = compare(jobs)
    assert set(table) >= {"fcfs", "srtf", "mlfq"}
    print("银行家", "安全" if bank["safe"] else "不安全", "缺页", pages["faults"], "SCAN", scan["distance"])


if __name__ == "__main__":
    main()
