from termcolor import colored
from datetime import datetime


class Logger:
    def __init__(self, worker_id=None):
        self.worker_id = worker_id

    def log(self, text):
        ts = datetime.now().strftime('%x %X%p')
        if self.worker_id is not None:
            print('[{}] [{}] {}'.format(ts, str(self.worker_id).ljust(3), text))
        else:
            print('[{}] {}'.format(ts, text))

    def err(self, text):
        ts = datetime.now().strftime('%x %X%p')
        if self.worker_id is not None:
            print(colored('[{}] [{}] {}'.format(ts, str(self.worker_id).ljust(3), text), 'red'))
        else:
            print(colored('[{}] {}'.format(ts, text), 'red'))

    def suc(self, text):
        ts = datetime.now().strftime('%x %X%p')
        if self.worker_id is not None:
            print(colored('[{}] [{}] {}'.format(ts, str(self.worker_id).ljust(3), text), 'green'))
        else:
            print(colored('[{}] {}'.format(ts, text), 'green'))
