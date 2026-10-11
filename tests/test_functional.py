"""Functional tests: does every command do what the protocol says?"""
import pytest


def test_ping(device):
    assert device.send("PING") == "OK PONG"


def test_version_format(device):
    resp = device.send("VERSION")
    assert resp.startswith("OK ")
    parts = resp[3:].split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts), resp


def test_led_on_then_off(device):
    assert device.send("LED ON") == "OK LED ON"
    assert device.send("LED?") == "OK LED ON"
    assert device.send("LED OFF") == "OK LED OFF"
    assert device.send("LED?") == "OK LED OFF"


def test_read_pot_in_range(device):
    resp = device.send("READ POT")
    assert resp.startswith("OK ")
    value = int(resp.split()[1])
    assert 0 <= value <= 4095


def test_read_button_is_binary(device):
    assert device.send("READ BTN") in ("OK 0", "OK 1")


@pytest.mark.parametrize("text", [
    "hello",
    "Hello World",
    "12345",
    "symbols !@#$%^&*()",
    "x" * 50,
    "y" * 100,
])
def test_echo_returns_same_text(device, text):
    assert device.send(f"ECHO {text}") == f"OK {text}"
