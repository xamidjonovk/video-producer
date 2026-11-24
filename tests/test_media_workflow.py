import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "plugins/video-producer/skills/video-producer"
sys.path.insert(0, str(SKILL))

from online_references import collect
from studio import command_path


class ReferenceWorkflowTests(unittest.TestCase):
    def test_profile_sample_keeps_only_requested_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            fixture = project / "downloader.py"
            fixture.write_text(
                "import json, sys\n"
                "args = sys.argv[1:]\n"
                "assert args[-1] == 'https://www.youtube.com/@Test/shorts'\n"
                "assert '--ignore-config' in args and '--skip-download' in args\n"
                "assert args[args.index('--playlist-end') + 1] == '2'\n"
                "print(json.dumps({'entries':[{'id': str(i), 'title': 'Example', "
                "'url': 'https://youtu.be/dQw4w9WgXcQ', 'view_count': i} for i in range(5)]}))\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = collect(project, "https://www.youtube.com/@Test/shorts?si=demo", 2,
                                 [sys.executable, str(fixture)])
            self.assertEqual(result, 0)
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt["evidence"], "metadata")
            self.assertEqual(len(receipt["videos"]), 2)
            self.assertEqual(receipt["videos"][0]["url"], "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            self.assertTrue(Path(receipt["report"]).is_file())
            with self.assertRaisesRegex(ValueError, "single authorized video"):
                collect(project, "https://www.instagram.com/test/reels/", 5,
                        [sys.executable, str(fixture)], download=True)


@unittest.skipUnless(command_path("ffmpeg"), "set VIDEO_AGENT_FFMPEG to run encoding tests")
class FinishingWorkflowTests(unittest.TestCase):
    def call(self, *arguments):
        result = subprocess.run(list(map(str, arguments)), text=True, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_local_export_checks_hdr_grade_and_audio_master(self):
        ffmpeg = command_path("ffmpeg")
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            source = project / "sdr.mp4"
            hdr = project / "pq.mp4"
            music = project / "music.wav"
            effect = project / "foley.wav"
            self.call(ffmpeg, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=320x180:r=30:d=5",
                      "-f", "lavfi", "-i", "sine=f=470:d=5", "-c:v", "libx264", "-c:a", "aac", source)
            self.call(ffmpeg, "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=320x180:r=30:d=4",
                      "-vf", "format=yuv420p10le", "-c:v", "libx265", "-tag:v", "hvc1",
                      "-x265-params", "colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc",
                      "-color_primaries", "bt2020", "-color_trc", "smpte2084", "-colorspace", "bt2020nc", hdr)
            self.call(ffmpeg, "-v", "error", "-f", "lavfi", "-i", "sine=f=180:d=2", music)
            self.call(ffmpeg, "-v", "error", "-f", "lavfi", "-i", "sine=f=950:d=0.3", effect)
            studio = [sys.executable, SKILL / "vp.py", "studio", project]
            self.call(*studio, "init", "work")
            job = project / "work"
            (job / "captions.srt").write_text(
                "1\n00:00:00,000 --> 00:00:02,000\nOʻzbekcha subtitr sinovi\n", encoding="utf-8",
            )
            plan_path = job / "edit.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            edit = plan | {
                "clips": [{"file": str(source), "end": 3, "grade": {"brightness": 0.035}},
                          {"file": str(hdr), "end": 2}],
                "audio": [{"file": str(music), "role": "music", "loop": True, "fade_in": 0.2, "fade_out": 0.4},
                          {"file": str(effect), "role": "foley", "start": 1.1, "duration": 0.3}],
                "subtitles": "captions.srt",
            }
            plan_path.write_text(json.dumps(edit), encoding="utf-8")
            self.call(*studio, "render", "work")
            report_path = job / "exports/technical-review.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual((report["width"], report["height"]), (1080, 1920))
            self.assertEqual(report["technical_check"], "decoded")
            self.assertEqual(report["color"]["clips"][1]["color_source"], "pq")
            self.assertGreaterEqual(report["color"]["picture"]["samples"], 4)
            self.assertTrue(report["audio_master"]["ducked_music"])
            self.assertEqual(report["audio_master"]["status"], "pass", report["audio_master"])
            self.assertAlmostEqual(report["audio_master"]["export"]["input_i"], -16, delta=1.5)
            self.assertLessEqual(report["audio_master"]["export"]["input_tp"], -0.9)
            plan["clips"] = [{"file": str(source), "end": 2, "gain": 0}]
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            self.call(*studio, "render", "work")
            silent = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(silent["audio_master"]["status"], "no_measurable_audio")
