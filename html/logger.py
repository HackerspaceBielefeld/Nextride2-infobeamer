import logging

# Custom Formatter class to include logger name as `logger_type`
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.asctime = self.formatTime(record, "%d:%m-%H:%M:%S")
        record.logger_name = record.name
        return super().format(record)

# Define the log format to include [dd:mm-hh:mm:ss][logger_name][loglevel] - message
log_format = '[%(asctime)s][%(logger_name)s][%(levelname)s] - %(message)s'

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Capture all levels of logs (DEBUG and above)
    format=log_format,    # Use the custom format
    handler=logging.StreamHandler()  # Output logs to console
)

# Apply the custom formatter to the root logger's handler
root_logger = logging.getLogger()
root_logger.handler.setFormatter(CustomFormatter(log_format))
