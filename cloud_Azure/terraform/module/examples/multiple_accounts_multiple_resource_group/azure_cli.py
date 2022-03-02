import logging
import time
from typing import Any, Optional

from az.cli import az

log = logging.getLogger(__name__)

EX_OK: int = 0  # exit code for successful command


def az_cli(command: str, max_attempts: int = 1) -> Optional[Any]:
    """
    Azure CLI commands issued in a quick succession may fail,
    eg. when trying to configure a resource that is still being created
    So, allow optional retry with exponential backoff
    """

    wait_sec = 1
    while max_attempts:
        data = _az_cli(command)
        if data is not None:
            return data
        max_attempts -= 1
        if max_attempts == 0:
            break
        log.debug("Retrying Azure CLI command in %d second(s)... (remaining attempts: %d)", wait_sec, max_attempts)
        time.sleep(wait_sec)
        wait_sec = wait_sec * 2

    return None  # all attempts failed


def _az_cli(command: str) -> Optional[Any]:
    """
    Return type specific to the command on success
    Empty result is represented as empty dict (az wrapper feature)
    Return None on Azure CLI command execution error
    """

    try:
        return_code, data, logs = az(command)
    except ValueError:
        log.exception("Failed to execute Azure CLI command")
        return None

    if return_code != EX_OK:
        log.error("Failed to execute Azure CLI command. Error message: '%s'. Error code: %d", logs.strip(), return_code)
        return None

    return data
