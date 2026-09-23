# 积木工坊 BrickForge

四人课设：可视化拼工厂，用操作系统算法算产量。Python 3.10+，只用标准库。

```text
python -m brickforge
```

调度：FCFS / SJF / SRTF / 优先级 / RR / MLFQ。磁盘：SSTF / SCAN / C-SCAN。内存：首次/最佳/最坏适应 + LRU/FIFO 分页。另有银行家死锁避免、PCB、系统调用轨迹。

## 四人分工（按答辩主讲切，不要抢文件）

| 人 | 主讲 | 只改这些 | 做成什么才算交差 | 别人不准动 |
| --- | --- | --- | --- | --- |
| **甲** | 进程/线程怎么被用户拼出来 | `app/`、`app/js/lab.js`、JSON 字段说明 | 厂区两层积木、连线、工人、件/分、原料图；实验台只**显示**别人算出的 JSON | 不写四种调度、不写 Daemon |
| **乙** | 处理机调度 | `brickforge/scheduler.py`、`tests/test_sched.py` | FCFS / SJF / 优先级 / RR；甘特条；四种算法对照表；换算法产量或等待必须变 | 不改画布 DOM、不写 fork |
| **丙** | 同步与 IPC | `brickforge/sync.py`、`brickforge/workers.py`、`tests/test_sync.py` | 车间=进程、机器=线程；队列传工单；信号量占库位；传送带=有界缓冲，能看出空转/阻塞 | 不改乙的四种算法 |
| **丁** | 守护进程、文件锁、内存/磁盘类比 | `brickforge/daemon.py`、`persist.py`、`warehouse.py`、`shipping.py`、`tests/test_store.py` | 独立守护进程写日志、心跳拉起；布局文件锁；货架首次/最佳适应；出货 SSTF | 不许用前端定时器冒充 Daemon |

公共契约只有一份：`POST /api/simulate` 返回的 JSON。乙写入 `lab.compare` / `lab.gantt`，丙写入 `lab.sync`，丁写入 `lab.warehouse` / `lab.shipping`，甲只读这些字段画实验台。`brickforge/kernel.py` 是胶水，改字段先在组里说一声。

交叉验收：甲查乙的数字是不是真变；乙查丙能不能看出阻塞；丙查丁是不是独立进程；丁查甲的 JSON 内核读不读得懂。

## 目录

- `app/` 甲 · 积木画布与实验台
- `brickforge/scheduler.py` 乙 · 调度
- `brickforge/sync.py` `workers.py` 丙 · 同步 / IPC
- `brickforge/warehouse.py` `shipping.py` `daemon.py` `persist.py` 丁 · 仓储 / 出货 / 守护
- `tests/` 各人自己的冒烟脚本
- `handbook/` 课设手册

## 自测

```text
python tests/test_sched.py
python tests/test_sync.py
python tests/test_store.py
python tests/test_kernel.py
```
