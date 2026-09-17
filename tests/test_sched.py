"""B 角色第一周最小交付：同一组工单，对比四种调度。

运行：
    python tests/test_sched.py
"""

from dataclasses import dataclass


@dataclass
class Job:
    name: str
    burst: int
    priority: int  # 数字越小越急


JOBS = [
    Job("急单-A", burst=3, priority=1),
    Job("长单-B", burst=8, priority=3),
    Job("短单-C", burst=2, priority=2),
    Job("普通-D", burst=5, priority=2),
]


def fcfs(jobs):
    t = 0
    waits = []
    for job in jobs:
        waits.append((job.name, t, t + job.burst))
        t += job.burst
    return waits


def sjf(jobs):
    return fcfs(sorted(jobs, key=lambda j: j.burst))


def priority(jobs):
    return fcfs(sorted(jobs, key=lambda j: (j.priority, j.burst)))


def rr(jobs, quantum=2):
    t = 0
    remain = {j.name: j.burst for j in jobs}
    order = [j.name for j in jobs]
    finish = {}
    while remain:
        progressed = False
        for name in list(order):
            if name not in remain:
                continue
            slice_ = min(quantum, remain[name])
            t += slice_
            remain[name] -= slice_
            progressed = True
            if remain[name] == 0:
                finish[name] = t
                del remain[name]
        if not progressed:
            break
    start_guess = {j.name: 0 for j in jobs}
    return [(name, start_guess[name], finish[name]) for name in [j.name for j in jobs]]


def avg_wait(result, jobs):
    burst = {j.name: j.burst for j in jobs}
    waits = [end - burst[name] for name, _start, end in result]
    return sum(waits) / len(waits)


def report(title, result):
    print(f"\n== {title} ==")
    for name, start, end in result:
        print(f"  {name}: 开始 {start}, 完成 {end}")
    print(f"  平均等待约 {avg_wait(result, JOBS):.2f}")


def main():
    report("FCFS", fcfs(JOBS))
    report("SJF", sjf(JOBS))
    report("动态优先级", priority(JOBS))
    report("RR q=2", rr(JOBS))
    print("\n四种算法完成时间不同，说明调度策略已经进入数字，而不是只写在 PPT 上。")


if __name__ == "__main__":
    main()
