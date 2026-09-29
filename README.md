# ESP32 Test Harness

An automated verification suite for ESP32-S3 firmware. The ESP32 runs firmware that accepts text commands over USB serial and controls real hardware (an LED, a push button, and a potentiometer). A Python/pytest harness on the PC verifies the device with functional, negative, stress, and soak tests.

## Features

- **Embedded firmware** (C++, Arduino framework) implementing a simple, testable command protocol
- **Functional tests** verifying every command returns the correct reply and format
- **Negative tests** confirming bad input produces a clean error and never crashes or hangs the device
- **Stress testing** with thousands of rapid-fire commands, logging per-command latency to CSV
- **Soak testing** that runs randomized mixed commands over long durations to catch slow failures
- **HTML test reports** via pytest-html

## Hardware

- Freenove ESP32-S3 board
- LED with a 220 Ω resistor
- Push button
- Potentiometer
- Breadboard and jumper wires

## Command protocol

Commands are newline-terminated text. Every reply is a single line starting with `OK` or `ERR`, which keeps the device easy to test automatically.

| Command | Reply | Purpose |
|---|---|---|
| `PING` | `OK PONG` | Health check |
| `VERSION` | `OK 1.0.1` | Firmware version for regression tracking |
| `LED ON` / `LED OFF` | `OK LED ON` / `OK LED OFF` | Drive an output |
| `LED?` | `OK LED ON` / `OK LED OFF` | Read back output state |
| `READ POT` | `OK 0–4095` | Read analog input |
| `READ BTN` | `OK 0` / `OK 1` | Read digital input |
| `ECHO <text>` | `OK <text>` | Data integrity check |
| empty line | `ERR EMPTY` | |
| over 128 characters | `ERR TOO_LONG` | Input length limit |
| anything else | `ERR UNKNOWN_CMD` | |

## Test suites

| Suite | File | What it checks |
|---|---|---|
| Functional | `tests/test_functional.py` | Every command returns the correct reply and format |
| Negative | `tests/test_negative.py` | Invalid input is rejected cleanly and the device stays responsive |
| Stress | `tests/test_stress.py` | High-volume commands with zero failures; latency logged to CSV |
| Soak | `tests/test_stress.py` | Randomized mixed commands over a long run |

## Project structure

```
firmware/serial_device/serial_device.ino   ESP32 firmware
tests/conftest.py                          Serial connection and test options
tests/test_functional.py                   Functional tests
tests/test_negative.py                     Negative tests
tests/test_stress.py                       Stress and soak tests
pytest.ini                                 Test configuration
requirements.txt                           Python dependencies
```

## Getting started

### 1. Flash the firmware

Open `firmware/serial_device/serial_device.ino` in the Arduino IDE, set the pin numbers at the top of the file to match your wiring, select **ESP32S3 Dev Module** as the board, and upload.

### 2. Install the test dependencies

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the tests

Close the Arduino Serial Monitor first, since only one program can use the port at a time. Replace `COM5` with your board's port.

```
# Functional and negative tests
pytest --port COM5 -v -m "not stress and not soak"

# Stress test (10,000 commands)
pytest --port COM5 -v -s -m stress --stress-count 10000

# Soak test (60 minutes)
pytest --port COM5 -v -s -m soak --soak-minutes 60

# HTML report
pytest --port COM5 -m "not soak" --html=report.html --self-contained-html
```

## Tech stack

C++ (Arduino framework) · ESP32-S3 · Python · pytest · pyserial · pytest-html

---

Built by **Dhun Patel**, Computer Engineering, Oakton College · [LinkedIn](https://linkedin.com/in/dhunpatel1337)
