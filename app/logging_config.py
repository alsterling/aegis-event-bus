# app/logging_config.py
import logging
import sys
import structlog

def setup_logging():
    """Configures the structlog logging system."""
    
    # This is the shared part of the configuration for all loggers
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.dict_tracebacks,
        structlog.stdlib.PositionalArgumentsFormatter(),
    ]

    structlog.configure(
        processors=shared_processors + [
            # This processor prepares the log for the standard library
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # This configures the final output, in our case, JSON
    formatter = structlog.stdlib.ProcessorFormatter(
        # The 'event' is the main message.
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    # Get the root logger and remove any existing handlers to prevent duplicates
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # Add our custom handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)