"""Create an SRT from a local source using the project's transcription environment."""

import argparse
from pathlib import Path


def timestamp(seconds):
    remaining = max(0, round(seconds * 1000))
    minutes, remaining = divmod(remaining, 60_000)
    hours, minutes = divmod(minutes, 60)
    seconds, milliseconds = divmod(remaining, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def make_srt(segments):
    cues = []
    for segment in segments:
        text = " ".join(segment.text.split())
        if text and segment.end > segment.start:
            time_range = f"{timestamp(segment.start)} --> {timestamp(segment.end)}"
            cues.append(f"{len(cues) + 1}\n{time_range}\n{text}")
    return "\n\n".join(cues) + "\n" if cues else ""


def main():
    from faster_whisper import WhisperModel

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--language", help="ISO 639-1 language code, such as uz or en.")
    parser.add_argument("--model", default="small")
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"Media file is missing: {args.source}")
    if args.output.suffix.lower() != ".srt" or args.output.exists() or args.output.is_symlink():
        parser.error("Choose a new .srt output path.")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(args.source), language=args.language, vad_filter=True)
    content = make_srt(segments)
    if not content:
        parser.error("The model found no speech to caption.")
    with args.output.open("x", encoding="utf-8", newline="\n") as target:
        target.write(content)


if __name__ == "__main__":
    main()
