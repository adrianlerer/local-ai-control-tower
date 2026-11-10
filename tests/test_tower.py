import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tower import Busy, GIB, Snapshot, decide, gib, lease, parse_linux, parse_macos


class Decisions(unittest.TestCase):
    def test_exact_threshold(self):
        r = decide(Snapshot(16*GIB, 10, "fixture"), 6*GIB, 10*GIB, now=10)
        self.assertEqual(r["state"], "ELIGIBLE_ESTIMATE")
        self.assertFalse(r["authorization"])

    def test_one_byte_short(self):
        r = decide(Snapshot(16*GIB-1, 10, "fixture"), 6*GIB, 10*GIB, now=10)
        self.assertEqual(r["state"], "WAIT_MEMORY")
        self.assertEqual(r["deficit_bytes"], 1)

    def test_stale_and_future(self):
        for now in (9, 15.001):
            self.assertEqual(decide(Snapshot(100,10,"f"),0,1,now=now)["state"],"STALE")

    def test_invalid_bytes(self):
        for value in (-1, True, 1.5, "100"):
            with self.assertRaises(ValueError):
                decide(Snapshot(value,10,"f"),0,1,now=10)

    def test_bad_timestamps(self):
        for value in (float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                decide(Snapshot(100,value,"f"),0,1,now=10)

    def test_units(self):
        self.assertEqual(gib("1.5"), 1610612736)
        for text in ("nan", "inf", "-1"):
            with self.assertRaises(Exception): gib(text)

    def test_linux_units(self):
        self.assertEqual(parse_linux("MemAvailable:      123 kB\n"), 123*1024)

    def test_macos_excludes_inactive(self):
        text="Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 10.\nPages inactive: 999.\n"
        self.assertEqual(parse_macos(text),10*16384)

    def test_observation_parse_failure(self):
        for parser in (parse_linux,parse_macos):
            with self.assertRaises(ValueError): parser("unrecognized")


class Leases(unittest.TestCase):
    def test_real_process_exclusion_and_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            code="from pathlib import Path; from tower import lease; import sys;\nwith lease(Path(sys.argv[1])): pass"
            cwd=str(Path(__file__).resolve().parents[1])
            with lease(root):
                child=subprocess.run([sys.executable,"-c",code,str(root)],cwd=cwd,capture_output=True)
                self.assertNotEqual(child.returncode,0)
                self.assertIn(b"Busy",child.stderr)
            child=subprocess.run([sys.executable,"-c",code,str(root)],cwd=cwd,capture_output=True)
            self.assertEqual(child.returncode,0,child.stderr)

    def test_exception_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            try:
                with lease(Path(directory)): raise RuntimeError("fixture")
            except RuntimeError: pass
            with lease(Path(directory)): pass

    def test_shared_directory_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            os.chmod(directory,0o755)
            with self.assertRaises(ValueError):
                with lease(Path(directory)): pass

    def test_symlink_lock_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/"target").touch();(root/"inference.lock").symlink_to(root/"target")
            with self.assertRaises(OSError):
                with lease(root): pass

    def test_child_death_releases_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            code="from pathlib import Path; from tower import lease; import sys,time;\nwith lease(Path(sys.argv[1])):\n print('ready',flush=True);time.sleep(20)"
            p=subprocess.Popen([sys.executable,"-c",code,directory],cwd=str(Path(__file__).resolve().parents[1]),stdout=subprocess.PIPE,text=True)
            try:
                self.assertEqual(p.stdout.readline().strip(),"ready")
                p.terminate();p.wait(timeout=3)
                with lease(Path(directory)): pass
            finally:
                if p.poll() is None: p.kill();p.wait()
                p.stdout.close()


if __name__=="__main__": unittest.main()
