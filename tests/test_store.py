"""丁：仓储分区 + SSTF 出货。"""

from brickforge.shipping import run as ship
from brickforge.warehouse import pack_jobs


def main():
    pack = pack_jobs([3, 5, 2, 8], [8, 5, 12, 3], "best")
    assert pack["placed"] >= 3
    assert "log" in pack
    assert len(pack["origin"]) == 4
    sstf = ship([12, 7, 4, 18], "sstf")
    fcfs = ship([12, 7, 4, 18], "fcfs")
    assert sstf["distance"] <= fcfs["distance"]
    print("丁 · 仓储放入", pack["placed"], "SSTF 寻道", sstf["distance"], "FCFS", fcfs["distance"])


if __name__ == "__main__":
    main()
