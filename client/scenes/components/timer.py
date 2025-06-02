import time

class Timer:
    def __init__(self, total_time: float):
        self.total_time = total_time
        self.time_left = total_time
        self.active = False
        self.last_update = time.time()

    def start(self):
        self.time_left = self.total_time
        self.active = True
        self.last_update = time.time()

    def stop(self):
        self.active = False

    def reset(self):
        self.time_left = self.total_time
        self.last_update = time.time()

    def update(self):
        if self.active:
            now = time.time()
            elapsed = now - self.last_update
            self.time_left -= elapsed
            self.last_update = now

            if self.time_left <= 0:
                self.time_left = 0
                self.active = False
                return True  # Timer hết
        return False

    def get_time_left(self):
        return max(0, self.time_left)

    def is_active(self):
        return self.active
