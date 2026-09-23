"""丙：传送带有界缓冲 + 队列 IPC 冒烟。"""

from multiprocessing import Process, Queue

from brickforge.persist import default_layout
from brickforge.sync import line_buffers


def worker(inbox: Queue, outbox: Queue) -> None:
    job = inbox.get()
    outbox.put(f"车间已接收: {job}")


def test_buffers():
    buf = line_buffers(default_layout()["shops"], capacity=6)
    assert buf["belts"]
    assert buf["buffer_slots"] >= 6
    assert "有界缓冲" in "".join(buf["kinds"])
    return buf


def test_queue():
    inbox: Queue = Queue()
    outbox: Queue = Queue()
    proc = Process(target=worker, args=(inbox, outbox))
    proc.start()
    inbox.put("工单-001")
    msg = outbox.get(timeout=5)
    proc.join(timeout=5)
    assert proc.exitcode == 0
    assert "工单-001" in msg


if __name__ == "__main__":
    test_queue()
    buf = test_buffers()
    print("丙 · IPC 与缓冲通过，传送带", len(buf["belts"]), "条")
