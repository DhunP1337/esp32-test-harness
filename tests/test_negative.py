"""Negative tests: bad input should give a clean error, never a crash or hang."""
import pytest


@pytest.mark.parametrize("cmd", [
    "FOO",
    "ping",          # commands are case-sensitive
    "LED BLUE",
    "READ",
    "ECHO",          # ECHO with no text
    "PING PING",
])
def test_unknown_commands_rejected(device, cmd):
    assert device.send(cmd) == "ERR UNKNOWN_CMD"


def test_empty_line_rejected(device):
    assert device.send("   ") == "ERR EMPTY"


def test_too_long_command_rejected(device):
    assert device.send("ECHO " + "z" * 300) == "ERR TOO_LONG"


def test_device_still_alive_after_bad_input(device):
    device.send("GARBAGE")
    device.send("ECHO " + "z" * 300)
    assert device.send("PING") == "OK PONG"
