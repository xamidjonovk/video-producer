# Online reference workflow

Use a profile URL for an initial sample of eight public posts unless the brief calls for a different bounded sample. For YouTube, a channel's `/shorts` link samples Shorts, while a plain channel link samples its videos. For Instagram, prefer an available Instagram profile or Reels connector when the website limits metadata. Use YouTube video and transcript tools when available and authorized.

```text
python <skill>/vp.py reference <project> <profile-or-video-URL> --limit 8
python <skill>/vp.py reference <project> <video-URL> --download-authorized
python <skill>/vp.py studio <project> inspect <job> <local-clip>
python <skill>/vp.py scenes <project> <local-clip> <project-relative-analysis-folder>
```

`reference` reuses yt-dlp or prepares the pinned package in the project's Python environment. The report under `references/online/` records links, observed fields, source, timestamp and access status. Use comparable formats and publication ages when evaluating metrics. Prepare local media if the user owns the clip, has download permission, or the platform offers an authorized download. The download option accepts one video at a time.

When a website blocks extraction, retain the access status and use public metadata, a connector such as vidIQ, a viewable public page, or a user-supplied file. Treat metadata, transcript, sampled frames and full playback as distinct sources of evidence.

For an individual source, record the opening visual and line, beat and cut times, framing, typography, pacing, color and sound when observed. Use a contact sheet and scene timestamps for local footage and play the clip when available. Use a transcript as evidence for words and structure. Reuse craft choices in the new video's original concept and media.

[yt-dlp](https://github.com/yt-dlp/yt-dlp) · [PySceneDetect](https://github.com/Breakthrough/PySceneDetect)
