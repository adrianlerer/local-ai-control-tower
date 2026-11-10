# Verification scope

Run `python3 -m unittest discover -s tests -v` from the repository root.

The initial local evaluation passed 14 tests on macOS: inclusive capacity threshold, one-byte deficit, invalid inputs, stale and future timestamps, GiB conversion, Linux and macOS fixture parsing, observation failure, real child-process exclusion, exception recovery, private-directory enforcement, symlink rejection and lock release after process termination.

The Linux parser uses synthetic `/proc/meminfo` fixtures. A full Linux-host run has not been performed. A passing parser fixture is not a Linux deployment test. No cloud CI, model inference, GPU allocation or paid API was used for this evaluation.

The demo's `DEMO_COMPLETED` means a fixed sleep finished while holding a cooperative lock. It does not imply model execution, memory allocation equal to the request or correctness of generated content.

## Reproduce rejection and eligibility

```sh
python3 tower.py plan --available-gib 8 --reserve-gib 4 --request-gib 3
python3 tower.py plan --available-gib 6 --reserve-gib 4 --request-gib 3
```

Expected: `ELIGIBLE_ESTIMATE` (exit 0), then `WAIT_MEMORY` with deficit 1,073,741,824 bytes (exit 2). These are deterministic scenarios, not measurements of the author's machine.

## Next validation boundaries

Before integrating with real models: assess actual runtime demand, noncooperating consumers, GPU use, observation failures under load, cancellation and resource restoration. Before a public MCP release: implement and test the protocol and authorization boundary. Before promoting the skill: evaluate its behavior in another assistant or session against explicit failure cases.

## Technical references

- [Linux kernel: /proc/meminfo and MemAvailable](https://www.kernel.org/doc/html/latest/filesystems/proc.html): the Linux estimate is not a reservation.
- [Python 3.12: fcntl](https://docs.python.org/3.12/library/fcntl.html): exclusive, nonblocking advisory locking.
- macOS parsing was checked against the installed `/usr/bin/vm_stat` output; only explicitly free pages are credited.
