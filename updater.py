import time
import threading

class ManualUpdater:

    def __init__(self, client):
        self.client = client

    def update(self):
        self.client.schedule()

    def start(self):pass
    def stop(self):pass

    def is_updating(self):
        return False

class ThreadingUpdater:

    def __init__(self, client):
        self.client = client
        self.thread = None
        self.started = True

    def update(self):
        raise TypeError('is already updating')

    def start(self, update_interval = 0.002):
        """start a thread that calls update every update_interval seconds."""
        assert not self.thread, 'can only start one thread'
        self.update_interval = update_interval
        thread = threading.Thread(target = self._updatethread)
        thread.deamon = True
        thread.start()
        self.thread = thread
        return thread

    def close(self):
        self.started = False
        self.thread.join()

    def _updatethread(self):
        now2 = time.time()
        while self.started:
            now = now2 + self.update_interval
            self.client.schedule()
            now2 = time.time()
            if now > now2:
                time.sleep(now - now2)

    def is_updating(self):
        return True

    
