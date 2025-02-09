import logging
import os
from logging.handlers import RotatingFileHandler  # Import RotatingFileHandler

class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Ensure the logs directory exists
        log_directory = os.path.join('app', 'logs')
        os.makedirs(log_directory, exist_ok=True)

        # Define log file path
        log_file = os.path.join(log_directory, 'predictions.log')

        # Set up RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 , backupCount=3  # Rotate at 5MB, keep 3 backups
        )

        # Set formatter for log messages
        formatter = logging.Formatter('%(levelname)s : %(message)s')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def exception(self, message):
        self.logger.exception(message)


# import logging
# import os

# class Logger:
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.logger.setLevel(logging.DEBUG)
#         file_handler = logging.FileHandler(os.path.join('app', 'logs', 'predictions.log'))
#         formatter = logging.Formatter('%(levelname)s : %(message)s')
#         file_handler.setFormatter(formatter)
#         self.logger.addHandler(file_handler)        

#     def info(self,message):
#         self.logger.info(message)

#     def exception(self,message):
#         self.logger.exception(message)
