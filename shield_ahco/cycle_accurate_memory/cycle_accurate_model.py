from __future__ import annotations
from dataclasses import dataclass

@dataclass
class SyncReadMemory:
    data: list[int]
    pending_addr: int | None = None
    rdata: int = 0
    valid: bool = False

    def tick(self, req: bool, addr: int):
        self.valid = self.pending_addr is not None
        if self.pending_addr is not None:
            self.rdata = self.data[self.pending_addr]
        self.pending_addr = addr if req else None


@dataclass
class MacState:
    sum_qaqw: int = 0
    sum_qa: int = 0

    def clear(self):
        self.sum_qaqw = 0
        self.sum_qa = 0

    def consume(self, qa: int, qw: int):
        self.sum_qaqw += int(qa) * int(qw)
        self.sum_qa += int(qa)


class DenseLatency1Model:
    """
    Dense engine with explicit 1-cycle feature/weight read latency.

    Per tap:
      ISSUE -> WAIT -> CONSUME
    """
    def __init__(self, act, weight, din, dout):
        self.act = SyncReadMemory(act)
        self.weight = SyncReadMemory(weight)
        self.din = din
        self.dout = dout
        self.cycles = 0

    def run(self):
        outputs=[]
        for o in range(self.dout):
            mac=MacState()
            for i in range(self.din):
                # ISSUE
                self.act.tick(True, i)
                self.weight.tick(True, o*self.din+i)
                self.cycles += 1

                # WAIT / data appears at end of this cycle
                self.act.tick(False, 0)
                self.weight.tick(False, 0)
                self.cycles += 1

                assert self.act.valid and self.weight.valid
                mac.consume(self.act.rdata, self.weight.rdata)

            outputs.append((mac.sum_qaqw, mac.sum_qa))
        return outputs
