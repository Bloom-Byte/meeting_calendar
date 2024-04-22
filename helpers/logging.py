import logging


def log_exception(exc: Exception) -> None:
    """
    Log an exception.

    :param exc: Exception object.
    """
    logger = logging.getLogger(__name__)
    logger.error(f"An error occurred: {exc}", exc_info=True)
