# Color and sound finishing

Inspect camera metadata and problem shots before the final render. Match exposure and white balance from cut to cut. Keep skin tones natural and preserve important highlights. Use the available calibrated Resolve color pipeline for Dolby Vision, log, camera LUTs and uncertain camera color tags. The local renderer can tone-map tagged BT.2020 PQ/HLG to Rec.709 SDR using FFmpeg with zscale. Review the tone-mapped image at normal brightness.

Set a mild project grade or per-clip `grade` when a visual check justifies it. Supported controls are `brightness`, `contrast`, `saturation` and `gamma`. Leave controls neutral for footage that already matches. The color report records source kinds and sampled luma. Inspect neighboring cuts and compare important frames to the intended look.

Keep spoken audio intelligible. Time cues to actions, use room tone where a cut needs continuity, and add Foley where it supports the image. Label additional audio as `dialogue`, `music`, `ambience`, or `foley` in the edit plan. Use `start`, `source_start`, `duration`, `fade_in`, `fade_out` and `gain` as needed. For a missing effect, `vp.py sfx <project> "a soft paper rustle" <job>/assets/paper.wav` can prepare and use Earshot locally. Verify the cue against the picture.

New local edit plans use a configurable -16 LUFS and -1 dBTP master and duck music behind foreground audio. The renderer applies constant gain when the measured mix has enough true-peak headroom, preserving its dynamics. It uses loudnorm when reaching the target needs peak control. Inspect the encoded AAC measurements in `technical-review.json`. Fix missed loudness or peak limits when it shows `review`. Confirm intentional silence before delivery when it shows `no_measurable_audio`. At normal playback speed check voice, music balance, lip sync, effect timing, edits and colors. Record issues at the timecode and rerender after changes.

```json
{
  "color": {"hdr_to_sdr": true, "grade": {"contrast": 1.04}},
  "master": {"lufs": -16, "true_peak": -1, "duck_music": true},
  "audio": [
    {"file": "assets/bed.wav", "role": "music", "loop": true, "fade_in": 0.3, "fade_out": 0.8},
    {"file": "assets/paper.wav", "role": "foley", "start": 2.12, "duration": 0.35}
  ]
}
```

[FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) · [Earshot](https://github.com/Leonxlnx/earshot)
