import concurrent.futures
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/video-producer/skills"
sys.path.insert(0, str(SKILLS / "video-producer"))

from credit_plan import check


class EfficiencyTests(unittest.TestCase):
    def test_full_quote_and_legacy_unit_quote(self):
        plan = {"cap": 300, "spent": 20, "reserve": 30, "shots": [
            {"id": "batch", "quoted_total": 240, "count": 3}]}
        self.assertEqual(check(plan)["remaining"], 10)
        plan["shots"] = [{"id": "units", "quoted_credits": 80, "count": 3}]
        self.assertEqual(check(plan)["planned"], 240)
        plan["shots"][0]["quoted_total"] = 240
        with self.assertRaises(ValueError):
            check(plan)
        plan["shots"] = [{"id": "small", "quoted_total": Decimal("0.01")}]
        self.assertEqual(check(plan)["planned"], 1)

    def test_resume_and_concurrent_paid_holds(self):
        with tempfile.TemporaryDirectory() as job:
            cli = [sys.executable, str(SKILLS / "higgsfield-shots/takes.py"), job]

            def call(*args, ok=True):
                proc = subprocess.run([*cli, *args], capture_output=True, text=True)
                if ok:
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    return json.loads(proc.stdout)
                self.assertNotEqual(proc.returncode, 0)

            call("init", "--cap", "180", "--reserve", "20")
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(subprocess.run, [*cli, "hold", shot, shot, "100"], capture_output=True)
                        for shot in ("hand", "door")]
                results = [job.result() for job in jobs]
            self.assertEqual(sorted(x.returncode for x in results), [0, 1])
            held = call("status")
            self.assertEqual((held["held"], held["available"]), (100, 60))
            shot = held["takes"][0]["shot"]
            call("hold", shot, "duplicate", "50", "--retry", ok=False)
            call("link", shot, "provider-01")
            call("link", shot, "provider-01")
            call("link", shot, "other-id", ok=False)
            call("finish", shot, "rejected", "100", "0:02 hand drifts")
            call("refund", shot, "80", "billing-01")
            self.assertEqual(call("refund", shot, "80", "billing-01")["available"], 80)
            call("hold", shot, "second", "80", "--retry")
            call("link", "second", "provider-02")
            call("finish", "second", "kept", "80", "provider-02 passes playback")
            call("hold", shot, "third", "0", "--retry", ok=False)
            self.assertEqual(call("status")["spent"], 160)

    def test_offline_installer_places_both_siblings_on_both_hosts(self):
        with tempfile.TemporaryDirectory() as project:
            command = [sys.executable, str(ROOT / "install.py"), "both", "--project", project]
            for _ in range(2):
                subprocess.run(command, check=True, capture_output=True)
            for host in (".agents", ".claude"):
                skills = Path(project) / host / "skills"
                self.assertTrue((skills / "higgsfield-shots/takes.py").is_file())
                self.assertTrue((skills / "video-producer/SKILL.md").is_file())
