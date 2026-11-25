# Reference intake and production

## Store and analyze references

- Run `references_tool.py` from any accessible directory. Pass the active project path explicitly. A supplied file is copied into `references/media/` under a unique content-derived name. Files placed directly inside `references/` are registered in place. Open local clips using `--inspect` for a contact sheet, metadata and mono audio when available.
- Reuse previous notes, footage and transcripts first. For a new production technique, search the official docs for the tool and version in use, then check a practical case study if the docs leave a decision open. Read metadata or transcripts before opening full videos. Inspect the relevant timestamps and save the source URL, access date and finding so the next run can reuse it.
- Preserve the original clip and its URL or source. For Instagram and YouTube links, register the clean URL before analysis. Use vidIQ `watch_shortform_content` for accessible public short video and the YouTube transcript feature or available connector for longer videos. Save the analysis in `references/notes/<reference-id>.md`. If only metadata or transcript is available, any notes about cadence, framing or audiovisual synchronization must be marked unverified.
- A link creates a record, not a video file. Import the media file when the user supplies it or an authorized media download is available. Use platform export/download or the media owner's approved file. Use yt-dlp only with a permitted direct export or authorized use supported by the platform. Do not use private credentials, bypass paywalls or login barriers, or add an unlicensed reference clip or track to published deliverables.
- For each reference write duration and access method, the first three seconds, scene changes with timecodes, approximate shot lengths, what moves in the shot, how evidence B-roll connects to speech, sound transitions, captions and grading. At the end distill two to four ideas that can transfer to the user's own assets. Change expression, dialogue, graphics and brand identity as appropriate. Reuse themes or craft techniques.

## Production choices

| Source | Workflow |
| --- | --- |
| iPhone, podcast or lecture | Inspect orientation, timing, audio and HDR. Transcribe with available faster-whisper or ElevenLabs. Make a transcript-driven rough cut with natural pauses, then insert only B-roll that adds evidence or context. Time subtitles to the edited audio. In Resolve use correctly tagged sources and matching color management. |
| Hybrid | Keep the user's original performance and natural audio. Try local masking or Resolve for a new background. Match perspective, light direction, color and moving edges. Use short generated inserts to supply shots that cannot be sourced otherwise. |
| Cinematic from scratch | Follow the [cinematic workflow](cinematic.md) from screenplay and reusable asset sheets through timed shot direction, live quotes, a representative take and playback of adjacent shots. |
| Motion and infographics | Use HyperFrames for HTML/GSAP, Remotion for React/data-driven animation, or Fusion when a native Resolve composition is useful. Generate moving footage only when an animation or real recording cannot supply the needed visual. |

Use `studio.py` as a preview and delivery helper. Use Python 3.10 or newer. Run `python <skill>/studio.py doctor` to check tool detection. FFmpeg resolves from `VIDEO_AGENT_FFMPEG`, a machine-local `studio.local.json` beside the executing script, `PATH` or installed `imageio_ffmpeg`. On a machine with another editor or Python environment, reuse its existing FFmpeg binary by specifying the exact path for the current process. Verify FFprobe availability for precise source metadata. Resolve MCP, design tools and external generators depend on the session's installed connectors. If unavailable, keep the script, shot list and edit plan usable without them. Supply an existing SRT for subtitles and carry out creative QA with playback.

## Project files

- `references/index.json`, `references/media/`, `references/notes/`, `references/inspection/`
- Per-video folder with `brief.json`, `script.json`, `edit.json`, raw asset locations, `assets.md`, `higgsfield-plan.json` when needed and `review.md`
- Outputs in `exports/` plus caption, cover and valid publication package when requested
