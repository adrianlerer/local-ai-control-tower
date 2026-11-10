"""Small, cooperative local admission demo. Python 3.11+, POSIX only."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import fcntl
import json
import math
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import time

GIB = 1024 ** 3


def natural(value: int, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


@dataclass(frozen=True)
class Snapshot:
    available_bytes: int
    observed_at: float
    method: str


def decide(snapshot: Snapshot, reserve: int, request: int, *, now: float) -> dict:
    """An estimate, never a reservation or a guarantee of future RAM."""
    available = natural(snapshot.available_bytes, "available")
    reserve = natural(reserve, "reserve")
    request = natural(request, "request")
    if not all(type(v) in (float, int) and math.isfinite(v)
               for v in (now, snapshot.observed_at)):
        raise ValueError("finite monotonic timestamps required")
    age = now - snapshot.observed_at
    state = ("STALE" if age < 0 or age > 5 else
             "ELIGIBLE_ESTIMATE" if available >= reserve + request else "WAIT_MEMORY")
    return {"state": state, "available_bytes": available,
            "reserve_bytes": reserve, "request_bytes": request,
            "deficit_bytes": max(0, reserve + request - available),
            "method": snapshot.method, "authorization": False}


def parse_linux(text: str) -> int:
    match = re.search(r"^MemAvailable:\s+(\d+) kB$", text, re.MULTILINE)
    if not match:
        raise ValueError("MemAvailable is unavailable")
    return int(match[1]) * 1024


def parse_macos(text: str) -> int:
    page = re.search(r"page size of (\d+) bytes", text)
    free = re.search(r"^Pages free:\s+(\d+)\.", text, re.MULTILINE)
    if not page or not free:
        raise ValueError("unrecognized vm_stat output")
    # Deliberately conservative: do not credit inactive/purgeable/compressed pages.
    return int(page[1]) * int(free[1])


def observe() -> Snapshot:
    system = platform.system()
    if system == "Linux":
        amount = parse_linux(Path("/proc/meminfo").read_text())
        method = "linux-memavailable-estimate"
    elif system == "Darwin":
        result = subprocess.run(["/usr/bin/vm_stat"], capture_output=True,
                                text=True, timeout=3, check=True,
                                env={**os.environ, "LC_ALL": "C"})
        amount = parse_macos(result.stdout)
        method = "macos-free-pages-only-conservative"
    else:
        raise ValueError("supported hosts: macOS and Linux")
    return Snapshot(amount, time.monotonic(), method)


class Busy(RuntimeError):
    pass


@contextmanager
def lease(directory: Path):
    """Nonblocking cooperative exclusion, scoped to one private directory."""
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = directory.lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or info.st_mode & 0o077):
        raise ValueError("state directory must be owner-only (0700), not a symlink")
    path = directory / "inference.lock"
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_nlink != 1 or info.st_mode & 0o077):
            raise ValueError("unsafe lock file")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Busy("another cooperating process holds this lock") from exc
        yield
    finally:
        os.close(fd)  # POSIX releases this process's lock even after an exception.


def gib(text: str) -> int:
    try:
        value = float(text)
        if not math.isfinite(value) or value < 0 or value > 2 ** 30:
            raise ValueError()
        return int(value * GIB)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected finite non-negative GiB") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("observe")
    for command in ("plan", "demo"):
        p = sub.add_parser(command)
        p.add_argument("--reserve-gib", type=gib, required=True)
        p.add_argument("--request-gib", type=gib, required=True)
        if command == "plan":
            p.add_argument("--available-gib", type=gib,
                           help="synthetic input; does not observe this host")
        else:
            p.add_argument("--state-dir", type=Path, required=True)
            p.add_argument("--hold-seconds", type=int, choices=range(1, 31), default=3)
    args = parser.parse_args()
    try:
        if args.command == "observe":
            print(json.dumps(asdict(observe())))
            return 0
        if args.command == "plan":
            sample = (Snapshot(args.available_gib, time.monotonic(), "synthetic")
                      if args.available_gib is not None else observe())
            result = decide(sample, args.reserve_gib, args.request_gib, now=time.monotonic())
        else:
            with lease(args.state_dir):
                result = decide(observe(), args.reserve_gib, args.request_gib,
                                now=time.monotonic())
                if result["state"] == "ELIGIBLE_ESTIMATE":
                    # Fixed demonstration only: no model, arbitrary command or network.
                    print(json.dumps({"state": "DEMO_HOLDING_LOCK",
                                      "model_calls": 0}), flush=True)
                    time.sleep(args.hold_seconds)
                    result["state"] = "DEMO_COMPLETED"
        print(json.dumps(result))
        return 0 if result["state"] in ("ELIGIBLE_ESTIMATE", "DEMO_COMPLETED") else 2
    except Busy:
        print(json.dumps({"state": "BUSY", "model_calls": 0}))
        return 3
    except (ValueError, OSError, subprocess.SubprocessError):
        # Do not log environment variables, filesystem contents or private command output.
        print(json.dumps({"state": "OBSERVATION_OR_STATE_ERROR", "authorization": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
