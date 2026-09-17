"""C 角色冒烟：两个进程用队列传一条工单。Windows / Linux 均可。"""

from multiprocessing import Process, Queue


def worker(inbox: Queue, outbox: Queue) -> None:
    job = inbox.get()
    outbox.put(f"车间已接收: {job}")


def main() -> None:
    inbox: Queue = Queue()
    outbox: Queue = Queue()
    proc = Process(target=worker, args=(inbox, outbox))
    proc.start()
    inbox.put("工单-001")
    print(outbox.get(timeout=5))
    proc.join(timeout=5)
    assert proc.exitcode == 0
    print("IPC 冒烟通过。")


if __name__ == "__main__":
    main()
