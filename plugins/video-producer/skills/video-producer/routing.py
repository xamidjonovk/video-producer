"""Translate the agent's semantic production intent into an actionable workflow."""


REEL_COVERAGE = ("map-coverage", "source-cutaways", "animate-explanation")
REEL_FINISH = ("rough-cut", "balance-dialogue", "verify", "package")
PRESENTER_AUDIO = ("inspect", "presenter-script", "lock-presenter-audio")
PRESENTER_SYNC = ("prepare-lipsync", "sync-original-video")


WORKFLOWS = {
    "raw-edit": ("inspect", "transcribe-if-needed", "rough-cut", "refine", "verify", "package"),
    "repurpose": ("inspect", "transcribe-if-needed", "select-complete-beats", "rough-cut", "reframe", "verify", "package"),
    "subtitles": ("inspect", "transcribe-if-needed", "verify-timing", "package"),
    "screen-demo": ("storyboard", "record-screen", "rough-cut", "verify", "package"),
    "html-motion": ("storyboard", "render-html", "verify", "package"),
    "react-motion": ("storyboard", "render-react", "verify", "package"),
    "launch-film": ("storyboard", "choose-launch-engine", "score-if-needed", "verify", "package"),
    "explainer": ("research", "storyboard", "voice-if-needed", "choose-explainer-engine", "verify", "package"),
    "one-shot": ("storyboard", "render-continuous", "verify", "package"),
    "composite": ("inspect", "matte-if-needed", "composite", "verify", "package"),
    "cinematic": ("storyboard", "reference-plates", "quote-if-needed", "cut-or-generate", "verify", "package"),
    "motion-reel": ("inspect", "lock-dialogue", *REEL_COVERAGE, *REEL_FINISH),
    "presenter-clone": (*PRESENTER_AUDIO, "map-coverage", *PRESENTER_SYNC, "rough-cut", "verify", "package"),
    "trend-research": ("research", "derive-original-hooks"),
    "publishing-draft": ("verify", "package"),
}


CHOICES = {
    "inspect": ("FFmpeg/FFprobe", "PySceneDetect when shot structure needs analysis"),
    "transcribe-if-needed": ("existing transcript or captions", "faster-whisper", "ElevenLabs Scribe when authorized"),
    "rough-cut": ("existing NLE or Resolve", "local FFmpeg edit plan", "Ghost Editor for eligible macOS talking-head jobs"),
    "record-screen": ("existing recorder/OBS", "OpenScreen"),
    "lock-dialogue": ("approved recording, script and timed captions",),
    "map-coverage": ("timestamped beat sheet in the job's script.json", "source contact sheet"),
    "source-cutaways": ("real product recording", "owned or licensed action footage with source and timecodes"),
    "animate-explanation": ("HyperFrames for timed diagrams and UI callouts", "existing editable motion timeline"),
    "balance-dialogue": ("speech-first mix with timed Foley", "FFmpeg loudness and true-peak measurement"),
    "render-html": ("HyperFrames",),
    "render-react": ("Remotion, subject to its license",),
    "choose-launch-engine": ("HyperFrames", "huashu-motion when custom scoring or annotated revisions justify it",
                             "Remotion for React assets"),
    "choose-explainer-engine": ("HyperFrames for HTML", "Remotion for React/data", "anything2explainer when eligible"),
    "render-continuous": ("original HyperFrames/Remotion camera plan", "onetake when eligible"),
    "matte-if-needed": ("existing Resolve Magic Mask", "MatAnyone for soft edges", "SAM 2 for object tracking"),
    "composite": ("Resolve Fusion", "EffectCraft"),
    "reference-plates": ("original assets", "authorized image generation"),
    "quote-if-needed": ("Higgsfield Shots for generated takes, live quotes and prior job receipts",),
    "presenter-script": ("approved script", "owned Reels for voice and pacing references"),
    "lock-presenter-audio": ("original recording", "existing authorized ElevenLabs voice clone if requested"),
    "prepare-lipsync": ("vp.py lipsync-prep", "FFmpeg/FFprobe"),
    "sync-original-video": ("Higgsfield Lipsync Studio / Sync Lipsync 3", "sync. labs sync-3"),
    "cut-or-generate": ("owned footage or licensed stock", "Higgsfield or ElevenLabs video when authorized",
                        "existing ComfyUI workflow with compatible Wan or LTX model"),
    "voice-if-needed": ("original recording", "authorized ElevenLabs voice"),
    "score-if-needed": ("licensed stems or real Foley", "Earshot for sound selection or synthesis"),
    "research": ("local reference notes", "public sources", "vidIQ when suitable"),
    "verify": ("FFmpeg decode check", "playback at target size with audio"),
    "package": ("editable timeline or edit plan", "MP4 and SRT as requested", "local publishing draft if requested"),
}


def production_plan(workflows):
    workflows = tuple(workflows)
    combined_reel = {"motion-reel", "presenter-clone"}
    ordered = {}
    for name in workflows:
        steps = WORKFLOWS[name]
        if name in combined_reel and combined_reel.issubset(workflows):
            steps = (*PRESENTER_AUDIO, *REEL_COVERAGE, *PRESENTER_SYNC, *REEL_FINISH)
        ordered.update(dict.fromkeys(steps))
    for step in ("verify", "package"):
        if step in ordered:
            ordered[step] = ordered.pop(step)
    return [{"step": step, "tools": list(CHOICES.get(step, ()))} for step in ordered]
