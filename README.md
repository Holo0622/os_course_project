# 积木工坊 BrickForge

操作系统原理课程设计。GitHub：https://github.com/Nozombie892/os_course_project.git

初期工作手册：用浏览器打开 `handbook/index.html`。

当前测试（四人组第一周冒烟）：

```text
python tests/test_sched.py
python tests/test_ipc_queue.py
```

- `tests/test_sched.py`：同一组工单对比 FCFS / SJF / 动态优先级 / RR
- `tests/test_ipc_queue.py`：两个进程用队列传递一条工单
