# app/logging_config.py
import logging
import sys
import structlog
from structlog.processors import JSONRenderer, TimeStamper


def setup_logging() -> None:
    """One‑shot Structlog configuration for the whole service."""
    timestamper = TimeStamper(fmt="iso", utc=True)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
        processors=[
            structlog.contextvars.merge_contextvars,  # request‑id etc.
            structlog.processors.add_log_level,
            timestamper,
            structlog.processors.dict_tracebacks,  # pretty tracebacks
            JSONRenderer(),  # final JSON out
        ],
    )

    # The std‑lib side; structlog will feed into this.
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",  # structlog already produced JSON
        stream=sys.stdout,
    )
