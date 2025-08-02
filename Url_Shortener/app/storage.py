import time
import threading

class URLStorage:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add_url(self, original_url, short_code):
        with self.lock:
            self.data[short_code] = {
                'url': original_url,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'clicks': 0
            }

    def get_url(self, short_code):
        return self.data.get(short_code)

    def increment_click(self, short_code):
        with self.lock:
            if short_code in self.data:
                self.data[short_code]['clicks'] += 1
