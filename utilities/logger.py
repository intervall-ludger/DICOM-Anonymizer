import logging

# Format string for log messages
_log_format = f"%(name)s - %(message)s"

# Dictionary mapping string levels to logging module constants
LOGGING_LEVEL = {
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
    "critical": logging.CRITICAL,
}

# Function to create and configure a StreamHandler for the given log level
def get_stream_handler(level):
    # Create a StreamHandler
    stream_handler = logging.StreamHandler()
    # Set the log level for the handler
    stream_handler.setLevel(level)
    # Set the formatter for the handler to use the log format string
    stream_handler.setFormatter(logging.Formatter(_log_format))
    # Return the configured handler
    return stream_handler


# Function to create and configure a logger with the given name and log level
def get_logger(name, str_level: str = "info"):
    # Convert the string level to lowercase
    str_level = str_level.lower()
    # If the string level is not in the LOGGING_LEVEL dictionary, set it to 'info'
    # and set a warning message
    if str_level not in LOGGING_LEVEL.keys():
        str_level = "info"
        add_warning_message = ""
    # Otherwise, set the warning message to None
    else:
        add_warning_message = None
    # Create a logger with the given name
    logger = logging.getLogger(name)
    # Set the log level for the logger
    logger.setLevel(LOGGING_LEVEL[str_level])
    # Add a StreamHandler to the logger, configured with the log level
    logger.addHandler(get_stream_handler(LOGGING_LEVEL[str_level]))
    # If a warning message was set, log it
    if add_warning_message is not None:
        logger.info(
            "Logger init warning: ",
            "str_level {str_level} is not implemented, default logging level info used",
        )
    # Return the configured logger
    return logger


# Create and configure the global logger with the name "DICOM-Anonymizer" and log level "info"
logger = get_logger(name="DICOM-Anonymizer", str_level="info")
