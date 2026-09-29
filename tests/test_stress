"""Stress and soak tests. Results are saved to results/*.csv."""
import csv
import random
import statistics
import time
from pathlib import Path

import pytest

RESULTS = Path(__file__).resolve().parent.parent / "results"


def timed_send(device, cmd):
    start = time.perf_counter()
    try:
        resp = device.send(cmd)
    except TimeoutError:
        resp = "<timeout>"
    return resp, (time.perf_counter() - start) * 1000  # milliseconds


@pytest.mark.stress
def test_ping_stress(device, request):
    count = request.config.getoption("--stress-count")
    rows, failures = [], []

    for i in range(count):
        resp, ms = timed_send(device, "PING")
        rows.append((i, resp, round(ms, 3)))
        if resp != "OK PONG":
            failures.append((i, resp))

    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "stress_latency.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "response", "latency_ms"])
        writer.writerows(rows)

    latencies = [r[2] for r in rows]
    print(f"\n{count} PINGs | failures: {len(failures)} | "
          f"avg {statistics.mean(latencies):.2f} ms | "
          f"max {max(latencies):.2f} ms")

    assert not failures, f"{len(failures)} failures, first few: {failures[:5]}"


@pytest.mark.soak
def test_mixed_command_soak(device, request):
    minutes = request.config.getoption("--soak-minutes")
    if minutes <= 0:
        pytest.skip("Soak test skipped (use --soak-minutes 60 to run it)")

    cases = [
        ("PING", lambda r: r == "OK PONG"),
        ("LED ON", lambda r: r == "OK LED ON"),
        ("LED OFF", lambda r: r == "OK LED OFF"),
        ("READ POT", lambda r: r.startswith("OK ")),
        ("READ BTN", lambda r: r in ("OK 0", "OK 1")),
        ("ECHO soak-test", lambda r: r == "OK soak-test"),
    ]
    end = time.time() + minutes * 60
    sent, failures = 0, []

    while time.time() < end:
        cmd, check = random.choice(cases)
        resp, _ = timed_send(device, cmd)
        sent += 1
        if not check(resp):
            failures.append((sent, cmd, resp))

    print(f"\nSoak: {sent} commands over {minutes} min | failures: {len(failures)}")
    assert not failures, f"First few failures: {failures[:5]}"
