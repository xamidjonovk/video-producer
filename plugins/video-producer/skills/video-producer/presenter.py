"""Prepare an existing presenter take and separate speech for video-to-video lip sync."""

import tempfile
from pathlib import Path

from finishing import REC709_TAGS, color_filters
from studio import media_path, number, probe, run, save_json


def prepare_pair(project, args, encoder):
    output = (project / args.output).resolve()
    if output == project or not output.is_relative_to(project) or output.exists():
        raise ValueError("Choose a new output directory inside the project.")
    video = media_path(project, args.video)
    audio = media_path(project, args.audio)
    video_info = probe(video, encoder)
    audio_info = probe(audio, encoder)
    duration = number(args.seconds, "seconds", 0.25)
    video_start = number(args.video_start, "video-start")
    audio_start = number(args.audio_start, "audio-start")
    if not video_info["width"] or not audio_info["audio"]:
        raise ValueError("Supply a video with picture and a separate file with the final speech track.")
    for name, start, info in (("video", video_start, video_info), ("audio", audio_start, audio_info)):
        if start + duration > info["duration"] + 0.02:
            raise ValueError(f"The requested range is outside the {name}. Use a matching range before quoting.")
    filters = color_filters(video_info["video"], {}, number, True)
    filters.extend(("pad=ceil(iw/2)*2:ceil(ih/2)*2", "format=yuv420p"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lipsync-", dir=output.parent) as temporary:
        pair = Path(temporary) / "pair"
        pair.mkdir()
        picture = pair / "presenter.mp4"
        speech = pair / "speech.wav"
        command = (encoder, "-nostdin", "-hide_banner", "-loglevel", "error")
        run(*command, "-ss", f"{video_start:.6f}", "-i", video, "-map", "0:v:0", "-an",
            "-t", f"{duration:.6f}", "-vf", ",".join(filters), "-c:v", "libx264",
            "-crf", "16", "-pix_fmt", "yuv420p", *REC709_TAGS, "-movflags", "+faststart", picture)
        run(*command, "-ss", f"{audio_start:.6f}", "-i", audio, "-map", "0:a:0", "-vn",
            "-t", f"{duration:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1", speech)
        prepared_video = probe(picture, encoder)
        prepared_audio = probe(speech, encoder)
        if not prepared_video["width"] or prepared_video["audio"] or not prepared_audio["audio"]:
            raise ValueError("The export did not produce silent picture and separate speech.")
        if any(abs(info["duration"] - duration) > 0.12 for info in (prepared_video, prepared_audio)):
            raise ValueError("The export did not match the requested duration. Check stream length and source cuts.")
        save_json(pair / "inputs.json", {
            "route": "presenter-clone",
            "video": {"file": picture.name, "source": str(video), "start": video_start,
                      "duration": prepared_video["duration"], "width": prepared_video["width"],
                      "height": prepared_video["height"]},
            "audio": {"file": speech.name, "source": str(audio), "start": audio_start,
                      "duration": prepared_audio["duration"]},
        })
        pair.rename(output)
    return output / "inputs.json"
