"""Shared pytest setup: command-line options and the `device` fixture."""
import time

import pytest
import serial


def pytest_addoption(parser):
    parser.addoption("--port", action="store", default=None,
                     help="Serial port of the ESP32, e.g. COM5 or /dev/ttyUSB0")
    parser.addoption("--baud", action="store", default=115200, type=int)
    parser.addoption("--stress-count", action="store", default=1000, type=int,
                     help="Number of PINGs in the stress test")
    parser.addoption("--soak-minutes", action="store", default=0, type=float,
                     help="Soak test length in minutes (0 = skip)")


class Device:
    """Small wrapper that sends one command and returns one reply line."""

    def __init__(self, port, baud):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baud
        self.ser.timeout = 2
        # Keep DTR/RTS low so opening the port doesn't hold the ESP32 in reset
        self.ser.dtr = False
        self.ser.rts = False
        self.ser.open()

    def send(self, cmd):
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\n").encode())
        line = self.ser.readline().decode(errors="replace").strip()
        if not line:
            raise TimeoutError(f"No response to {cmd!r}")
        return line

    def close(self):
        self.ser.close()


@pytest.fixture(scope="session")
def device(request):
    port = request.config.getoption("--port")
    if port is None:
        pytest.exit("Pass the serial port, e.g.  pytest --port COM5", returncode=2)

    dev = Device(port, request.config.getoption("--baud"))
    time.sleep(2)  # give the board time to boot if it reset

    for _ in range(5):
        try:
            if dev.send("PING") == "OK PONG":
                break
        except TimeoutError:
            pass
        time.sleep(0.5)
    else:
        dev.close()
        pytest.exit("Device did not answer PING. Is the Serial Monitor closed?",
                    returncode=2)

    yield dev
    dev.send("LED OFF")
    dev.close()
