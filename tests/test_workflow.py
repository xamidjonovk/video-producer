import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/video-producer"
SKILL = PLUGIN / "skills/video-producer"
sys.path.insert(0, str(SKILL))

from routing import production_plan
from speech import make_srt


class VideoProducerTests(unittest.TestCase):
    def test_both_marketplaces_install_the_same_skill(self):
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / codex["plugins"][0]["source"]["path"]).resolve(), PLUGIN)
        self.assertEqual((ROOT / claude["plugins"][0]["source"]).resolve(), PLUGIN)
        self.assertIn("Automatically use", (SKILL / "SKILL.md").read_text(encoding="utf-8"))

    def test_routing_selects_only_relevant_candidates(self):
        def stages(*workflows):
            return [step["step"] for step in production_plan(workflows)]

        raw = stages("raw-edit")
        self.assertIn("rough-cut", raw)
        self.assertNotIn("cut-or-generate", raw)
        self.assertNotIn("render-html", raw)
        self.assertIn("record-screen", stages("screen-demo"))
        self.assertIn("render-react", stages("react-motion"))
        self.assertIn("sync-original-video", stages("presenter-clone"))
        self.assertNotIn("cut-or-generate", stages("presenter-clone"))
        self.assertNotIn("sync-original-video", raw)
        self.assertNotIn("verify", stages("trend-research"))
        combined = stages("screen-demo", "html-motion")
        self.assertEqual(combined[-2:], ["verify", "package"])
        self.assertEqual(len(combined), len(set(combined)))

    def test_motion_reel_locks_audio_and_maps_coverage_before_sync(self):
        def stages(*workflows):
            return [step["step"] for step in production_plan(workflows)]

        plain = stages("motion-reel")
        self.assertLess(plain.index("lock-dialogue"), plain.index("map-coverage"))
        self.assertNotIn("sync-original-video", plain)
        hybrid = stages("motion-reel", "presenter-clone")
        self.assertEqual(hybrid, stages("presenter-clone", "motion-reel"))
        self.assertEqual(len(hybrid), len(set(hybrid)))
        self.assertNotIn("lock-dialogue", hybrid)
        order = ["lock-presenter-audio", "map-coverage", "prepare-lipsync", "sync-original-video",
                 "rough-cut", "balance-dialogue", "verify", "package"]
        positions = [hybrid.index(step) for step in order]
        self.assertEqual(positions, sorted(positions))

    def test_clip_captions_preserve_language_and_timing(self):
        items = [
            SimpleNamespace(start=0.25, end=1.533, text="  Assalomu   alaykum! "),
            SimpleNamespace(start=1.54, end=1.54, text="Zero duration"),
            SimpleNamespace(start=60.001, end=61.5, text="O‘zbekcha ovoz."),
        ]
        self.assertEqual(
            make_srt(items),
            "1\n00:00:00,250 --> 00:00:01,533\nAssalomu alaykum!\n\n"
            "2\n00:01:00,001 --> 00:01:01,500\nO‘zbekcha ovoz.\n",
        )

    def test_local_install_reuses_matching_version_and_preserves_customizations(self):
        spec = importlib.util.spec_from_file_location("installer", ROOT / "install.py")
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory() as path:
            destination = Path(path) / "skills"
            installed = installer.install(destination)
            self.assertEqual(installed, installer.install(destination))
            skill_file = installed / "SKILL.md"
            skill_file.write_text("my custom workflow", encoding="utf-8")
            with self.assertRaises(ValueError):
                installer.install(destination)
            self.assertEqual(skill_file.read_text(encoding="utf-8"), "my custom workflow")


if __name__ == "__main__":
    unittest.main()
