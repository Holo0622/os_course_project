"""乙：同一组工单对比四种调度，等待必须不同。

运行：
    python tests/test_sched.py
"""

from brickforge.scheduler import Job, compare, metrics, run


JOBS = [
    Job("j1", "急单-A", burst=3, priority=1),
    Job("j2", "长单-B", burst=8, priority=3),
    Job("j3", "短单-C", burst=2, priority=2),
    Job("j4", "普通-D", burst=5, priority=2),
]


def main():
    table = compare(JOBS)
    waits = []
    for algo, pack in table.items():
        m = pack["metrics"]
        print(f"{pack['name']}: 平均等待 {m['avg_wait']} 完成 {m['makespan']}")
        waits.append(m["avg_wait"])
        assert m["finished"] == len(JOBS)
    assert len(set(waits)) >= 2
    rr = run(JOBS, "rr")
    assert any(len(row.get("slices") or []) > 1 for row in rr)
    print("乙 · 调度对照通过。")


if __name__ == "__main__":
    main()
