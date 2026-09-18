from dataclasses import dataclass
@dataclass
class SaturatingAccumulator:
    width: int
    value: int = 0
    @property
    def min_int(self): return -(1 << (self.width-1))
    @property
    def max_int(self): return (1 << (self.width-1))-1
    def clear(self): self.value = 0
    def add(self, term):
        self.value = min(self.max_int, max(self.min_int, self.value + int(term)))
        return self.value
