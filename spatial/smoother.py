class StableLabel:
    """
    Simple majority-vote stabilizer for labels across frames.
    You feed it a new value each frame, it returns a stabilized value.
    """
    def __init__(self, window: int = 5):
        self.window = window
        self.buffer = []

    def update(self, value: str) -> str:
        if value is None:
            return self.current()

        self.buffer.append(value)
        if len(self.buffer) > self.window:
            self.buffer.pop(0)

        # majority vote
        counts = {}
        for v in self.buffer:
            counts[v] = counts.get(v, 0) + 1

        best = max(counts.items(), key=lambda x: x[1])[0]
        return best

    def current(self) -> str:
        return self.buffer[-1] if self.buffer else ""
