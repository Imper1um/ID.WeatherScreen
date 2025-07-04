import time
import logging

class Perf:
    def __init__(self, label="Perf", warn_threshold_ms=2000):
        self.label = label
        self.warn_threshold = warn_threshold_ms / 1000.0  # seconds
        self.timestamps = []
        self.stages = []
        self.triggered = False

        self.start_time = time.perf_counter()
        self.timestamps.append(self.start_time)
        self.stages.append("Start")

    def mark(self, stage: str):
        now = time.perf_counter()
        self.timestamps.append(now)
        self.stages.append(stage)

        if not self.triggered:
            first_elapsed = now - self.start_time
            if first_elapsed > self.warn_threshold:
                self.triggered = True
                logging.debug(f"[{self.label}] ⚠ Exceeded {self.warn_threshold * 1000:.0f}ms on stage '{stage}' ({first_elapsed:.2f}s since start)")

    def finish(self):
        if self.triggered:
            output = [f"[{self.label}] Timing Breakdown:"]
            for i in range(1, len(self.timestamps)):
                delta = self.timestamps[i] - self.timestamps[i-1]
                output.append(f"  {self.stages[i-1]} → {self.stages[i]}: {delta:.3f}s")
            total = self.timestamps[-1] - self.timestamps[0]
            output.append(f"  TOTAL: {total:.3f}s")
            for line in output:
                logging.debug(line)