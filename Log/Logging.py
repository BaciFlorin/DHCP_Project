import logging

# CONSOLE LOGGER CONFIG
logger = logging.getLogger("console_logger")
logger.setLevel(logging.DEBUG)

# FILE LOGGER CONFIG
file_logger = logging.getLogger("message_logger")
file_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler = logging.FileHandler("Log\messagesFlow.log", 'w')
handler.setFormatter(formatter)
file_logger.addHandler(handler)


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)
